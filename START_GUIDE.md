# Quick Start Guide

This project includes automated startup scripts that handle all configuration checks and launch both the frontend and backend simultaneously.

## 🚀 Quick Start

### macOS / Linux
```bash
./start.sh
```

### Windows
```batch
start.bat
```

## ✅ What the Script Does

The startup scripts automate the following checks:

1. **Environment Variables**
   - ✓ Verifies `OPENAI_API_KEY` is set
   - ⚠ Checks `TALLY_API_KEY` (optional)

2. **Python Environment**
   - ✓ Creates virtual environment if needed
   - ✓ Verifies required Python packages (fastapi, uvicorn, pydantic, openai)
   - ✓ Installs missing packages automatically

3. **Node.js Environment**
   - ✓ Checks Node.js v16+ is installed
   - ✓ Verifies npm is available
   - ✓ Installs frontend dependencies if needed

4. **Frontend Configuration**
   - ✓ Creates `.env` file if missing
   - ✓ Sets `VITE_API_BASE_URL=http://localhost:8000`

5. **Dependency Validation**
   - ✓ Confirms all services start correctly
   - ✓ Provides helpful error messages if something fails

## 📋 Prerequisites

Before running the startup script, ensure you have:

- **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
- **Node.js 16+** - Download from [nodejs.org](https://nodejs.org/)
- **OPENAI_API_KEY** - Get from [OpenAI API keys](https://platform.openai.com/api-keys)

## 🔑 Setting Environment Variables

### macOS / Linux

Add to your shell profile (`~/.bash_profile`, `~/.zshrc`, etc.):

```bash
export OPENAI_API_KEY="sk-..."
export TALLY_API_KEY="tally_..."  # Optional
```

Then reload:
```bash
source ~/.zshrc
```

### Windows

Set environment variables through System Properties or in Command Prompt:

```batch
set OPENAI_API_KEY=sk-...
set TALLY_API_KEY=tally_...
```

Or set them permanently through Control Panel → System → Environment Variables.

## 🌐 Access the Application

Once running, the script will display URLs for:

- **Frontend**: http://localhost:8081
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛑 Stopping Services

### macOS / Linux
Press `Ctrl+C` in the terminal running `start.sh`

### Windows
Close the command windows for Backend and Frontend

## 🐛 Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="your-key-here"
./start.sh
```

### "Port 8000 already in use"
Check if another process is using the port:
```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

Kill the process and restart the script.

### "npm command not found"
Install Node.js from [nodejs.org](https://nodejs.org/)

### Backend crashes on startup
Check the backend logs:
```bash
tail /tmp/backend.log  # macOS/Linux
type %TEMP%\backend.log  # Windows
```

## 📝 Manual Start (Alternative)

If you prefer to start services manually:

### Terminal 1 - Backend
```bash
source .venv/bin/activate
uvicorn server:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## 🔧 For Development

The scripts use `--reload` flag on the backend, meaning changes to Python files will automatically restart the server. Frontend changes with Vite also hot-reload automatically.

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
