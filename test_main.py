"""
Run with:
    pytest -v

Covers: register, login, create task, fetch tasks, and unauthorized
access to a protected route without a token.
"""


def get_auth_headers(client, username="haris", password="mySecret123"):
    """Helper: registers a user (ignoring if already registered from
    a previous test), logs in, and returns headers with a valid token."""
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )

    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "alicepass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    # password / hashed_password should never come back in the response
    assert "password" not in body
    assert "hashed_password" not in body


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "bobpass123"},
    )

    response = client.post(
        "/auth/token",
        data={"username": "bob", "password": "bobpass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_create_task(client):
    headers = get_auth_headers(client, username="carol", password="carolpass123")

    response = client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Cover the main flows", "status": "pending"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["status"] == "pending"


def test_fetch_tasks(client):
    headers = get_auth_headers(client, username="dave", password="davepass123")

    client.post("/tasks", json={"title": "Task A"}, headers=headers)
    client.post("/tasks", json={"title": "Task B"}, headers=headers)

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 2
    titles = [t["title"] for t in tasks]
    assert "Task A" in titles
    assert "Task B" in titles


def test_unauthorized_access_without_token(client):
    # no Authorization header at all
    response = client.get("/tasks")
    assert response.status_code == 401
    body = response.json()
    assert body["error"] is True
    assert body["status"] == 401


def test_duplicate_username_conflict(client):
    client.post(
        "/auth/register",
        json={"username": "erin", "email": "erin@example.com", "password": "erinpass123"},
    )
    # try registering the SAME username again with a different email
    response = client.post(
        "/auth/register",
        json={"username": "erin", "email": "erin2@example.com", "password": "erinpass123"},
    )
    assert response.status_code == 409
    body = response.json()
    assert body["error"] is True
    assert body["status"] == 409


def test_user_cannot_see_another_users_task(client):
    frank_headers = get_auth_headers(client, username="frank", password="frankpass123")
    grace_headers = get_auth_headers(client, username="grace", password="gracepass123")

    create_response = client.post(
        "/tasks", json={"title": "Frank's private task"}, headers=frank_headers
    )
    task_id = create_response.json()["id"]

    # grace tries to fetch frank's task by id - should get 404, not the task
    response = client.get(f"/tasks/{task_id}", headers=grace_headers)
    assert response.status_code == 404
