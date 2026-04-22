# tests/e2e/test_e2e.py

import pytest  # Import the pytest framework for writing and running tests

# The following decorators and functions define E2E tests for the FastAPI calculator application.


@pytest.mark.e2e
def test_hello_world(page, fastapi_server):
    """
    Test that the homepage displays "Hello World".

    This test verifies that when a user navigates to the homepage of the application,
    the main header (`<h1>`) correctly displays the text "Hello World". This ensures
    that the server is running and serving the correct template.
    """
    page.goto('http://localhost:8000')
    assert page.inner_text('h1') == 'Hello World'


@pytest.mark.e2e
def test_calculator_add(page, fastapi_server):
    """
    Test the addition functionality of the calculator.

    This test simulates a user performing an addition operation using the calculator
    on the frontend. It fills in two numbers, clicks the "Add" button, and verifies
    that the result displayed is correct.
    """
    page.goto('http://localhost:8000')

    page.fill('#a', '10')
    page.fill('#b', '5')

    page.click('button:text("Add")')

    page.wait_for_function(
        "document.querySelector('#result') && document.querySelector('#result').innerText !== ''"
    )
    assert page.inner_text('#result') == 'Calculation Result: 15'


@pytest.mark.e2e
def test_calculator_divide_by_zero(page, fastapi_server):
    """
    Test the divide by zero functionality of the calculator.

    This test simulates a user attempting to divide a number by zero using the calculator.
    It fills in the numbers, clicks the "Divide" button, and verifies that the appropriate
    error message is displayed.
    """
    page.goto('http://localhost:8000')

    page.fill('#a', '10')
    page.fill('#b', '0')

    page.click('button:text("Divide")')

    page.wait_for_function(
        "document.querySelector('#result') && document.querySelector('#result').innerText !== ''"
    )
    assert page.inner_text('#result') == 'Error: Cannot divide by zero!'


# ---------------------------------------------------
# AUTHENTICATION TESTS FOR REGISTRATION AND LOGIN
# ---------------------------------------------------


@pytest.mark.e2e
def test_register_success(page, fastapi_server):
    """
    Test successful user registration.

    This test simulates a user filling out the registration form with valid data.
    It verifies that the application responds with a success message and stores the JWT.
    """
    page.goto("http://localhost:8000/register")

    page.fill("#username", "dariel")
    page.fill("#email", "dariel@example.com")
    page.fill("#password", "secret123")
    page.fill("#confirmPassword", "secret123")

    page.click("button:text('Register')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )
    assert "Registration successful" in page.inner_text("#message")


@pytest.mark.e2e
def test_register_short_password(page, fastapi_server):
    """
    Test registration failure with a short password.

    This test ensures that the front-end validation prevents weak passwords
    and displays an appropriate error message.
    """
    page.goto("http://localhost:8000/register")

    page.fill("#username", "dariel2")
    page.fill("#email", "dariel2@example.com")
    page.fill("#password", "123")
    page.fill("#confirmPassword", "123")

    page.click("button:text('Register')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )
    assert "Password must be at least 6 characters." in page.inner_text("#message")


@pytest.mark.e2e
def test_login_success(page, fastapi_server):
    """
    Test successful user login.

    This test first registers a new user, then attempts to log in with valid credentials.
    It verifies that the login process succeeds and returns a success message.
    """
    # Register user first
    page.goto("http://localhost:8000/register")

    page.fill("#username", "dariel3")
    page.fill("#email", "dariel3@example.com")
    page.fill("#password", "secret123")
    page.fill("#confirmPassword", "secret123")

    page.click("button:text('Register')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )

    # Then login
    page.goto("http://localhost:8000/login")

    page.fill("#email", "dariel3@example.com")
    page.fill("#password", "secret123")

    page.click("button:text('Login')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )
    assert "Login successful" in page.inner_text("#message")


@pytest.mark.e2e
def test_login_wrong_password(page, fastapi_server):
    """
    Test login failure with incorrect password.

    This test verifies that the application correctly rejects invalid login attempts
    and displays an error message.
    """
    # Register user first
    page.goto("http://localhost:8000/register")

    page.fill("#username", "dariel4")
    page.fill("#email", "dariel4@example.com")
    page.fill("#password", "secret123")
    page.fill("#confirmPassword", "secret123")

    page.click("button:text('Register')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )

    # Attempt login with wrong password
    page.goto("http://localhost:8000/login")

    page.fill("#email", "dariel4@example.com")
    page.fill("#password", "wrongpass")

    page.click("button:text('Login')")

    page.wait_for_function(
        "document.querySelector('#message') && document.querySelector('#message').innerText !== ''"
    )
    assert "Invalid credentials" in page.inner_text("#message")