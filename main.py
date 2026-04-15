from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
import uvicorn
import logging

from app.operations import add, subtract, multiply, divide
from app.database import Base, engine, get_db
from app.models import User, Calculation
from app.schemas import (
    UserCreate,
    UserLogin,
    UserRead,
    CalculationCreate,
    CalculationUpdate,
    CalculationRead,
)
from app.security import hash_password, verify_password
from app.factory import CalculationFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both a and b must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    try:
        result = add(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    try:
        result = subtract(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    try:
        result = multiply(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    try:
        result = divide(operation.a, operation.b)
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/users/register", response_model=UserRead, responses={400: {"model": ErrorResponse}})
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User registered successfully: {db_user.username}")
    return db_user


@app.post("/users/login", responses={400: {"model": ErrorResponse}})
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    logger.info(f"User logged in successfully: {db_user.username}")
    return {"message": "Login successful"}


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).all()


@app.get("/calculations/{calculation_id}", response_model=CalculationRead, responses={404: {"model": ErrorResponse}})
def read_calculation(calculation_id: int, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.post("/calculations", response_model=CalculationRead, responses={400: {"model": ErrorResponse}})
def add_calculation(calculation: CalculationCreate, db: Session = Depends(get_db)):
    if calculation.user_id is not None:
        existing_user = db.query(User).filter(User.id == calculation.user_id).first()
        if not existing_user:
            raise HTTPException(status_code=400, detail="User does not exist")

    try:
        result = CalculationFactory.compute(calculation.a, calculation.b, calculation.type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_calculation = Calculation(
        a=calculation.a,
        b=calculation.b,
        type=calculation.type,
        result=result,
        user_id=calculation.user_id,
    )
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


@app.put("/calculations/{calculation_id}", response_model=CalculationRead, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def edit_calculation(calculation_id: int, calculation_update: CalculationUpdate, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    try:
        result = CalculationFactory.compute(calculation_update.a, calculation_update.b, calculation_update.type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    calculation.a = calculation_update.a
    calculation.b = calculation_update.b
    calculation.type = calculation_update.type
    calculation.result = result

    db.commit()
    db.refresh(calculation)
    return calculation


@app.delete("/calculations/{calculation_id}", responses={404: {"model": ErrorResponse}})
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calculation)
    db.commit()
    return {"message": "Calculation deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)