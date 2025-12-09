# Testing Guide - AI Content Platform

This document describes how to test the complete functionality of the AI Content Platform after the fixes.

## Prerequisites

- Backend installed and configured (see ai-content-platform-backend/README.md)
- Backend running on http://localhost:5000

## 1. Health Check

Verify the API is running:

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

## 2. User Registration

Register a new user:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "message": "註冊成功"
}
```

## 3. User Login

Login and get an access token:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser"
  }
}
```

**Save the access_token for subsequent requests.**

## 4. Create Project

Create a new project (replace YOUR_TOKEN with the token from step 3):

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My First Project",
    "description": "Test project description"
  }'
```

Expected response:
```json
{
  "message": "Project created",
  "project_id": 1,
  "name": "My First Project",
  "description": "Test project description",
  "owner_id": 1
}
```

**Save the project_id for the next steps.**

## 5. List Projects

Get all projects for the authenticated user:

```bash
curl -X GET http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
[
  {
    "project_id": 1,
    "name": "My First Project",
    "description": "Test project description",
    "role": "owner",
    "created_at": "2025-12-09T10:30:00"
  }
]
```

## 6. Create Content

Create content in the project (replace PROJECT_ID):

```bash
curl -X POST http://localhost:5000/api/contents/project/PROJECT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Test Content",
    "prompt": "What is artificial intelligence?",
    "response": "AI is the simulation of human intelligence in machines...",
    "tags": ["ai", "test", "tutorial"]
  }'
```

Expected response:
```json
{
  "message": "Content created",
  "id": 1
}
```

## 7. Get Content by Project

Retrieve all content for a project:

```bash
curl -X GET http://localhost:5000/api/contents/project/PROJECT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
[
  {
    "id": 1,
    "prompt": "What is artificial intelligence?",
    "response": "AI is the simulation of human intelligence in machines...",
    "tags": ["ai", "test", "tutorial"],
    "date": "2025-12-09T10:35:00"
  }
]
```

## 8. Search Content

Search across all content:

```bash
curl -X GET "http://localhost:5000/api/search?q=artificial" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 9. Tag Operations

### List all tags:
```bash
curl -X GET http://localhost:5000/api/tags \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create a new tag:
```bash
curl -X POST http://localhost:5000/api/tags \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "important"}'
```

### Get tags for specific content:
```bash
curl -X GET http://localhost:5000/api/tags/content/CONTENT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 10. Version Operations

### List versions for content:
```bash
curl -X GET http://localhost:5000/api/versions/content/CONTENT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create a new version:
```bash
curl -X POST http://localhost:5000/api/versions/content/CONTENT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "Updated prompt text",
    "file_url": null
  }'
```

## Complete Test Script

Here's a bash script that runs through the complete flow:

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:5000"
EMAIL="test@example.com"
PASSWORD="password123"
USERNAME="testuser"

# 1. Health check
echo "1. Testing health endpoint..."
curl -s $BASE_URL/api/health | python -m json.tool
echo ""

# 2. Register
echo "2. Registering user..."
curl -s -X POST $BASE_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}"
echo ""

# 3. Login and get token
echo "3. Logging in..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
TOKEN=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token obtained: ${TOKEN:0:50}..."
echo ""

# 4. Create project
echo "4. Creating project..."
PROJECT_RESPONSE=$(curl -s -X POST $BASE_URL/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Test Project", "description": "Auto-created"}')
PROJECT_ID=$(echo $PROJECT_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "Project created with ID: $PROJECT_ID"
echo ""

# 5. Create content
echo "5. Creating content..."
curl -s -X POST $BASE_URL/api/contents/project/$PROJECT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Content",
    "prompt": "What is AI?",
    "response": "AI is artificial intelligence",
    "tags": ["test", "ai"]
  }' | python -m json.tool
echo ""

# 6. Get content
echo "6. Retrieving content..."
curl -s -X GET $BASE_URL/api/contents/project/$PROJECT_ID \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

echo "✅ All tests completed!"
```

Save this as `test_api.sh`, make it executable with `chmod +x test_api.sh`, and run it with `./test_api.sh`.

## Troubleshooting

### Backend won't start
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (need 3.8+)
- Check the console for error messages

### Authentication errors
- Ensure token is being sent in the Authorization header
- Token expires after 24 hours - login again to get a new one
- Check that the token format is: `Bearer YOUR_TOKEN`

### Database errors
- If using SQLite, ensure `instance/` directory exists
- Run the migration script: `python migrate_db.py`
- Check database file permissions

### CORS errors (from frontend)
- Ensure backend has Flask-CORS installed
- Verify backend is running on the correct port (5000)
- Check browser console for specific CORS error messages

## Database Migration

If you're using an existing database, run the migration script to add missing columns:

```bash
cd ai-content-platform-backend
python migrate_db.py
```

This will add:
- `created_at` to project table
- `original_prompt` and `generated_content` to content table
- `response` and `response_ref` to content_version table

## Frontend Testing

To test the frontend with the backend:

1. Start the backend: `cd ai-content-platform-backend && python run.py`
2. In a new terminal, start the frontend: `cd ai-content-platform && npm run dev`
3. Open browser to `http://localhost:5173`
4. Test the UI:
   - Register a new account
   - Login
   - Create a project
   - Add content to the project
   - Search for content
   - Add tags

## Success Criteria

All tests pass if:
- ✅ Health endpoint returns 200 OK
- ✅ User can register successfully
- ✅ User can login and receive a valid JWT token
- ✅ User can create a project
- ✅ User can create content in the project
- ✅ User can retrieve content
- ✅ Tags and versions work correctly
- ✅ Frontend can communicate with backend through proxy
