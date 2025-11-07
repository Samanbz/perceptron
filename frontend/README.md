# Signal Radar Frontend

React + Vite frontend for the Deutsche Bank Signal Radar intelligence dashboard.

## Quick Start (Hackathon Mode 🏃‍♂️)

```bash
# Make scripts executable (first time only)
chmod +x run.sh format.sh

# Start the frontend (handles npm install and dev server)
./run.sh
```

The app will be available at `http://localhost:5173`

## Manual Setup

If you prefer to set up manually:

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run format` - Format code with Prettier & ESLint
- `npm run lint` - Check code quality
- `npm run lint:fix` - Fix linting issues

## Code Formatting

This project uses **Prettier** and **ESLint** for code formatting and linting.

### Format Code

```bash
./format.sh
# or
npm run format
```

Configuration files:

- `.prettierrc` - Prettier config
- `.eslintrc.json` - ESLint config

## Tech Stack

- ⚛️ **React 18** - Modern React with hooks
- ⚡ **Vite** - Lightning-fast build tool and dev server
- 🎨 **Prettier** - Opinionated code formatter
- 🔍 **ESLint** - Code quality and error checking

## Features

- Hot Module Replacement (HMR) for instant updates
- Proxy setup for backend API calls
- Pre-configured formatters and linters
- Production-ready build pipeline

## Development

The dev server runs with HMR enabled. Changes to your code will be reflected instantly in the browser.

### Backend Integration

The app connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before starting the frontend.

API proxy is configured in `vite.config.js` to route `/api/*` requests to the backend.

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx         # Main application component
│   ├── App.css         # Application styles
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite configuration
├── .prettierrc         # Prettier configuration
├── .eslintrc.json      # ESLint configuration
├── run.sh              # Quick start script
└── format.sh           # Code formatting script
```

## Why Vite?

- **Fast:** Native ES modules for instant server start
- **Modern:** Built for the modern web with ES6+
- **Optimized:** Rollup-based production builds
- **Simple:** Zero-config for most use cases
