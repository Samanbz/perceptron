# Signal Radar 🎯

Deutsche Bank Intelligence Dashboard - A multi-persona intelligence platform for detecting emerging reputational risks and opportunities.

## Hackathon Quick Start 🏃‍♂️💨

**One command to rule them all:**

```bash
# Make scripts executable and start everything
chmod +x start-all.sh format-all.sh && ./start-all.sh
```

This starts both backend and frontend. Access:

- 🎨 **Frontend:** http://localhost:5173
- 📡 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

Press `CTRL+C` to stop both services.

## Project Structure

```
perceptron/
├── backend/           # FastAPI backend
│   ├── app.py        # Main API application
│   ├── pyproject.toml # Dependencies & config
│   ├── run.sh        # Start backend
│   └── README.md     # Backend docs
├── frontend/          # React + Vite frontend
│   ├── src/          # React components
│   ├── package.json  # Dependencies & scripts
│   ├── run.sh        # Start frontend
│   └── README.md     # Frontend docs
├── start-all.sh       # Start both services
└── format-all.sh      # Format all code
```

## Individual Setup

### Backend (Python + FastAPI)

```bash
cd backend
chmod +x run.sh
./run.sh
```

See [backend/README.md](./backend/README.md) for details.

### Frontend (React + Vite)

```bash
cd frontend
chmod +x run.sh
./run.sh
```

See [frontend/README.md](./frontend/README.md) for details.

## Code Formatting

Format all code (both backend and frontend):

```bash
./format-all.sh
```

Or individually:

- **Backend:** `cd backend && ./format.sh` (black + isort)
- **Frontend:** `cd frontend && ./format.sh` (Prettier + ESLint)

## Tech Stack

### Backend

- ⚡ **FastAPI** - Modern Python web framework
- 🔄 **Uvicorn** - ASGI server with auto-reload
- 🎨 **Black** - Python code formatter
- 📦 **isort** - Import organizer

### Frontend

- ⚛️ **React 18** - UI library
- ⚡ **Vite** - Build tool and dev server
- 🎨 **Prettier** - Code formatter
- 🔍 **ESLint** - Linter

## Development Tips

### Backend

- Auto-reload enabled - save files to restart server
- Interactive API docs at `/docs` (Swagger UI)
- Alternative docs at `/redoc`

### Frontend

- Hot Module Replacement (HMR) - instant updates
- Proxy configured for API calls to backend
- React DevTools recommended for debugging

## Useful Commands

```bash
# Start everything
./start-all.sh

# Format all code
./format-all.sh

# Backend only
cd backend && ./run.sh

# Frontend only
cd frontend && ./run.sh

# Backend API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:5173
```

## Project Goals

Building a multi-persona intelligence dashboard that:

- Ingests public data sources (news, social media, regulatory)
- Detects emerging risks and opportunities
- Provides role-based views (Regulatory vs Communications teams)
- Uses NLP pipelines for signal detection

See [.github/instructions/requirements.instructions.md](.github/instructions/requirements.instructions.md) for full requirements.

## Troubleshooting

**Backend won't start:**

- Ensure Python 3.11+ is installed: `python3 --version`
- Delete `backend/venv` and restart

**Frontend won't start:**

- Ensure Node.js is installed: `node --version`
- Delete `frontend/node_modules` and run `npm install`

**CORS errors:**

- Backend must be running on port 8000
- Frontend must be running on port 5173
- Check CORS settings in `backend/app.py`

**Can't connect to API:**

- Ensure backend is running: `curl http://localhost:8000/api/health`
- Check browser console for errors

---

Built for Deutsche Bank Hackathon | Made with ⚡ FastAPI + ⚛️ React
