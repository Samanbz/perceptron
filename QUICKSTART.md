# 🚀 Signal Radar - Hackathon Cheat Sheet

## Instant Start

```bash
./start-all.sh          # Starts both backend + frontend
```

## Individual Services

```bash
cd backend && ./run.sh   # Backend only (port 8000)
cd frontend && ./run.sh  # Frontend only (port 5173)
```

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc

## Format Code

```bash
./format-all.sh         # Format everything
cd backend && ./format.sh   # Python only (black + isort)
cd frontend && ./format.sh  # React only (Prettier + ESLint)
```

## Testing API

```bash
curl http://localhost:8000/api/hello
curl http://localhost:8000/api/health
```

## Common Issues

**Frontend: patch-package error?**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --ignore-scripts
```

**Backend not starting?**

```bash
cd backend
rm -rf venv
./run.sh
```

**Frontend not starting?**

```bash
cd frontend
rm -rf node_modules
npm install --ignore-scripts
npm run dev
```

**Port already in use?**

- Backend: Edit `backend/run.sh` change `--port 8000`
- Frontend: Edit `frontend/vite.config.js` change `port: 5173`

## Dependencies

**Backend:** FastAPI, Uvicorn, Black, isort
**Frontend:** React, Vite, Prettier, ESLint

## File Structure

```
backend/app.py          # Add API endpoints here
frontend/src/App.jsx    # Main React component
backend/pyproject.toml  # Python deps & config
frontend/package.json   # Node deps & scripts
```

## Next Steps

1. Add NLP processing agents (SpaCy, VADER, etc.)
2. Implement data ingestion layer
3. Build the radar visualization
4. Add persona switching logic

---

**Need help?** Check README.md or individual README files in backend/ and frontend/
