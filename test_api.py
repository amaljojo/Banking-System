import pytest
from fastapi.testclient import TestClient
from main import app
from config.database import users_collection, accounts_collection

client = TestClient(app)

# Helper function to clean up test data (user and related accounts)
def clean_test_user():
    # Delete the test user and related accounts
    users_collection.delete_one({"username": "testuser"})
    accounts_collection.delete_many({"user": "testuser"})

# Test user creation
def test_create_user():
    # Create a new user
    response = client.post("/auth/create", json={
        "username": "testuser",
        "password": "Password1",
        "full_name": "Test User",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json() == {"message": "New user created successfully!"}

# Test login with valid credentials
def test_login_success():
    # Login with correct credentials
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# Test login with invalid credentials
def test_login_failure():
    # Login with incorrect credentials
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

# Test account creation with authentication
def test_create_account():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    token = login_response.json()["access_token"]

    # Create a new account
    response = client.post(
        "/bank/account",  
        json={
            "account_number": "1234567890",
            "balance": 100.0,
            "username": "testuser", 
            "account_type": "Savings"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Account created successfully!"}

# Test account creation without authentication
def test_create_account_unauthenticated():
    # Attempt to create an account without a token
    response = client.post("/bank/account", json={
        "account_number": "1234567890",
        "balance": 100.0,
        "username": "testuser", 
        "account_type": "Savings"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Test retrieving all accounts with authentication
def test_get_accounts():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    token = login_response.json()["access_token"]

    # Retrieve all accounts
    response = client.get(
        "/bank/accounts",  
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    accounts = response.json()
    assert isinstance(accounts, list)
    assert len(accounts) > 0

def test_get_accounts_no_accounts():
    # Create a new user for the test
    client.post("/auth/create", json={
        "username": "noaccountsuser",
        "password": "Password1",
        "full_name": "No Accounts User",
        "email": "noaccounts@example.com"
    })
    
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "noaccountsuser",
        "password": "Password1"
    })
    token = login_response.json()["access_token"]

    # Attempt to retrieve all accounts for the new user (who has no accounts)
    response = client.get(
        "/bank/accounts",  
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert response.json() == {"detail": "No accounts found"}


# Test filtering accounts based on balance
def test_filter_accounts():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    token = login_response.json()["access_token"]

    # Filter accounts based on balance
    response = client.get(
        "/bank/accounts/filter", 
        params={"max_balance": 200.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    accounts = response.json()
    assert all(account["balance"] <= 200.0 for account in accounts)

def test_delete_account():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create an account to delete
    client.post(
        "/bank/account",
        json={
            "account_number": "9876543210",
            "username": "testuser",
            "balance": 200.0,
            "account_type": "Checking"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Delete the account
    response = client.delete(
        "/bank/account/9876543210",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())  # Debugging: print the response
    assert response.status_code == 200
    assert response.json() == {"message": "Account deleted successfully"}


def test_deposit_to_account():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create an account for deposit
    client.post(
        "/bank/account",
        json={
            "account_number": "1122334455",
            "username": "testuser",
            "balance": 0.0,
            "account_type": "Savings"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Deposit into the account
    response = client.put(
        "/bank/account/1122334455/deposit?amount=150.0",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Deposit successful"
    assert response.json()["new_balance"] == 150.0


def test_withdraw_from_account():
    # Obtain a token for authentication
    login_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "Password1"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create an account with an initial balance
    client.post(
        "/bank/account",
        json={
            "account_number": "2233445566",
            "username": "testuser",
            "balance": 500.0,
            "account_type": "Savings"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Withdraw from the account
    response = client.put(
        "/bank/account/2233445566/withdraw?amount=200.0",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Withdrawal successful"
    assert response.json()["new_balance"] == 300.0  # Initial 500 - 200 withdrawal


# Cleanup after tests (run after tests to remove test user and accounts)
@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    clean_test_user()




