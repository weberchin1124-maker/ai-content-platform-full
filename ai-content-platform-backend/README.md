# AI Content Platform Backend

Flask-based REST API backend for the AI Content Platform.

## Prerequisites

- Python 3.8+
- pip

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
- For **PostgreSQL** (e.g., Supabase): Set `DATABASE_URL` to your connection string
- For **SQLite** (local development): Use `sqlite:///instance/dev.db` (default)

### 3. Initialize Database

If using SQLite for the first time, the database file will be created automatically when you run the app.

If using PostgreSQL, ensure your database is created and accessible.

### 4. Run the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `PUT /api/auth/update` - Update user profile (requires auth)

### Projects
- `GET /api/projects` - Get user's projects (requires auth)
- `POST /api/projects` - Create a new project (requires auth)
- `DELETE /api/projects/<id>` - Delete a project (requires auth)

### Content
- `GET /api/contents/project/<project_id>` - Get contents for a project (requires auth)
- `POST /api/contents/project/<project_id>` - Create content in a project (requires auth)
- `PUT /api/contents/<content_id>` - Update content (requires auth)
- `DELETE /api/contents/<content_id>` - Delete content (requires auth)

### Tags
- `GET /api/tags` - List all tags (requires auth)
- `POST /api/tags` - Create a new tag (requires auth)
- `GET /api/tags/content/<content_id>` - Get tags for content (requires auth)
- `POST /api/tags/content/<content_id>` - Add tags to content (requires auth)

### Versions
- `GET /api/versions/content/<content_id>` - List versions for content (requires auth)
- `POST /api/versions/content/<content_id>` - Create new version (requires auth)

### Search
- `GET /api/search?q=<query>` - Search content (requires auth)

## Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Save the `access_token` from the response.

### 3. Create a Project

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "My First Project", "description": "Test project"}'
```

### 4. Create Content

```bash
curl -X POST http://localhost:5000/api/contents/project/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"title": "Test Content", "prompt": "Hello", "response": "World", "tags": ["test"]}'
```

## Development

- The application runs in debug mode by default
- Changes to Python files will trigger an automatic reload
- Check console output for errors and logs

## Database Configuration

### Using PostgreSQL (Recommended for production)
Set in `.env`:
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### Using SQLite (Local development)
Set in `.env` or use default:
```
DATABASE_URL=sqlite:///instance/dev.db
```

## Troubleshooting

### Database Connection Issues
- Verify your `DATABASE_URL` is correct in `.env`
- For PostgreSQL, ensure the database exists and is accessible
- For SQLite, ensure the `instance/` directory exists

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Port Already in Use
- Change the port in `run.py` or kill the process using port 5000
