# PyJudge API Documentation

Base URL for local development: `http://127.0.0.1:8000`

Interactive documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Authentication

### `POST /signup`

Creates a user and returns access and refresh tokens.

Request:

```json
{
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "password": "strongpass123"
}
```

### `POST /login`

Authenticates a user and returns tokens.

### `POST /refresh?refresh_token=...`

Issues a fresh access and refresh token pair from a refresh token.

### `POST /logout`

Stateless logout placeholder. Clients should discard tokens.

## Problems

### `GET /problems`

Returns all problems.

### `GET /problem/{id}`

Returns one problem with only public sample test cases.

### `GET /problem/{id}/samples`

Returns public test cases for a problem.

### `POST /problem` Admin

Creates a problem with optional test cases.

```json
{
  "title": "Add Two Numbers",
  "description": "Read two integers and print their sum.",
  "constraints": "-10^9 <= a,b <= 10^9",
  "difficulty": "Easy",
  "time_limit": 2,
  "memory_limit": 128,
  "tags": "math,io",
  "test_cases": [
    {"input": "2 3\n", "expected_output": "5\n", "is_hidden": false},
    {"input": "10 7\n", "expected_output": "17\n", "is_hidden": true}
  ]
}
```

### `PUT /problem/{id}` Admin

Updates problem metadata.

### `DELETE /problem/{id}` Admin

Deletes a problem and its test cases.

### `POST /testcases?problem_id={id}` Admin

Adds one test case to a problem.

## Execution and Submissions

### `POST /run`

Runs code against public sample tests. It does not mark a problem as solved.

```json
{
  "problem_id": 1,
  "language": "python",
  "source_code": "a,b=map(int,input().split()); print(a+b)"
}
```

### `POST /submit`

Stores a pending submission and queues hidden-test judging. If Celery is unavailable in local dev, the API schedules an inline background judge task.

### `GET /submission/{id}`

Returns a submission result for its owner or an admin.

### `GET /history`

Returns the current user's submission history.

## Users and Leaderboard

### `GET /profile`

Returns current user profile.

### `GET /leaderboard`

Returns users sorted by solved count, score, and acceptance rate.

## Admin

### `GET /dashboard` Admin

Returns counts for users, problems, test cases, submissions, and banned users.

### `GET /admin/submissions` Admin

Returns the latest submissions.

### `POST /admin/users/{user_id}/ban` Admin

Bans a user. Banned users cannot log in or access authenticated APIs.

## Auth Header

Protected routes require:

```http
Authorization: Bearer <access_token>
```

## Verdicts

- `Pending`
- `Accepted`
- `Wrong Answer`
- `Compilation Error`
- `Runtime Error`
- `Time Limit Exceeded`
- `Memory Limit Exceeded`
- `Presentation Error`