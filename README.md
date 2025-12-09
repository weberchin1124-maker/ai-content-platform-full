# AI Content Platform

Full-stack AI content management platform with React frontend and Flask backend.

## Project Structure

```
ai-content-platform-full/
├── ai-content-platform/          # Frontend (React + Vite)
└── ai-content-platform-backend/  # Backend (Flask REST API)
```

## Quick Start

### Prerequisites

- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 16+, npm

### Running Locally (Development)

#### 1. Start the Backend

```bash
cd ai-content-platform-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional - uses SQLite by default)
cp .env.example .env
# Edit .env if you want to use PostgreSQL

# Run the server
python run.py
```

Backend will be available at `http://localhost:5000`

#### 2. Start the Frontend

In a **separate terminal**:

```bash
cd ai-content-platform

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Testing the Application

1. Open browser to `http://localhost:5173`
2. Register a new user account
3. Login with your credentials
4. Create a project
5. Add content to your project

## Features

- **User Authentication**: Register, login, and profile management with JWT
- **Project Management**: Create and organize projects
- **Content Management**: Create, edit, and delete content with AI-generated responses
- **Tagging System**: Organize content with tags
- **Version Control**: Track content versions
- **Search**: Search across your content
- **MongoDB Integration**: Optional NoSQL storage for large content

## API Documentation

See `ai-content-platform-backend/README.md` for detailed API documentation.

### Key Endpoints

- `GET /api/health` - Health check
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/contents/project/<id>` - Get project contents
- `POST /api/contents/project/<id>` - Create content

## Database Configuration

### Development (Default)
Uses SQLite database (`instance/dev.db`) - no configuration needed.

### Production (PostgreSQL)
Create a `.env` file in `ai-content-platform-backend/`:

```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key
```

### MongoDB (Optional)
For storing large content in NoSQL:

```env
MONGO_URI=mongodb://localhost:27017/your_database
```

## Architecture

### Backend
- **Framework**: Flask
- **Database ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: Flask-Bcrypt
- **CORS**: Flask-CORS
- **Primary DB**: PostgreSQL or SQLite
- **NoSQL DB**: MongoDB (optional)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS
- **HTTP Client**: Fetch API
- **Routing**: React Router (if implemented)

## Development Workflow

1. Backend changes:
   - Modify code in `ai-content-platform-backend/app/`
   - Flask auto-reloads in debug mode
   - Test with curl or Postman

2. Frontend changes:
   - Modify code in `ai-content-platform/src/`
   - Vite hot-reloads automatically
   - Test in browser

3. Database changes:
   - Update models in `app/models.py`
   - Create migration: `flask db migrate -m "description"`
   - Apply migration: `flask db upgrade`

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check database connection in `.env`

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Install dependencies: `npm install`
- Clear npm cache: `npm cache clean --force`

### API requests failing
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify JWT token is being sent
- Check CORS configuration

### Database errors
- For SQLite: Ensure `instance/` directory exists
- For PostgreSQL: Verify connection string and database exists
- Run migrations: `flask db upgrade`

## Production Deployment

### Backend
1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Use PostgreSQL for database
4. Enable HTTPS
5. Set strong `SECRET_KEY`

### Frontend
1. Build for production: `npm run build`
2. Serve static files with a web server (e.g., Nginx)
3. Configure API proxy for production backend URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Check documentation in subdirectory READMEs
- Review API endpoints in backend README
- Check browser console and server logs for errors
