# AI Content Platform - Frontend

React + Vite frontend for the AI Content Platform.

## Prerequisites

- Node.js 16+
- npm or yarn

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Backend Connection

The frontend is already configured to proxy API requests to the backend server.

Vite proxy configuration in `vite.config.js`:
- All requests to `/api` are forwarded to `http://127.0.0.1:5000`
- Make sure the backend is running on port 5000

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Running with Backend

To run the full application locally:

1. **Start the backend** (in a separate terminal):
   ```bash
   cd ../ai-content-platform-backend
   python run.py
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Project Structure

- `src/services/api.js` - API service layer for backend communication
- `src/mockData.js` - Mock data for development
- All API calls use the `/api` prefix which is proxied to the backend

## Development Notes

- The application uses Vite for fast development and HMR (Hot Module Replacement)
- ESLint is configured for code quality
- React Fast Refresh is enabled for component hot reloading

## API Integration

The frontend communicates with the backend through the API service layer:

- Authentication: Login, Register, Update Profile
- Projects: Create, List, Delete
- Content: Create, Update, Delete, Search
- Tags: Create, List, Add to Content
- Versions: Create, List

All API endpoints require authentication via JWT token stored in localStorage.

## Troubleshooting

### Backend Connection Issues
- Ensure backend is running on `http://localhost:5000`
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.js`

### Port Already in Use
- Change the port in Vite configuration or kill the process using port 5173

---

## React + Vite Template Information

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
