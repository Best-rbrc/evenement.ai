# Local Development Setup

This guide explains how to set up and run the AI Event Planner Agent locally for development.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher and npm
- OpenAI API key
- (Optional) Tally API key for form generation
- (Optional) Twilio credentials for SMS notifications

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Adrien-Z/AI-Event-Planner-Agent.git
cd AI-Event-Planner-Agent
```

### 2. Install Python Dependencies

Using `uv` (recommended):

```bash
uv sync
```

Or using `pip`:

```bash
pip install -e .
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - Form generation
TALLY_API_KEY=your-tally-api-key
PLAN_EVENT_FORM_MODE=skip  # Options: skip, unsandboxed, sandboxed

# Optional - SMS notifications
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_PHONE=+1234567890
TWILIO_TO_PHONE=+0987654321
```

## Running the Application

### Backend Server

Start the FastAPI backend server:

```bash
uv run server.py
```

Or using Python directly:

```bash
python server.py
```

The server will start on `http://localhost:8000` by default.

### Frontend Development Server

In a separate terminal, navigate to the frontend directory and start the development server:

```bash
cd frontend
npm run dev
```

The frontend will typically start on `http://localhost:5173` (Vite default port).

### Accessing the Application

Once both servers are running:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Running the MCP Server

For MCP server setup and usage, see [MCP_USAGE.md](MCP_USAGE.md).

Quick start:

```bash
export OPENAI_API_KEY="sk-proj-..."
uv run event-planner-mcp
```

Or using Python module:

```bash
export OPENAI_API_KEY="sk-proj-..."
uv run python -m custom_mcp_servers.fastmcp_server
```

## Running Tests

Execute the test suite:

```bash
uv run pytest tests/
```

Run specific test files:

```bash
uv run pytest tests/test_scheduling.py
uv run pytest tests/test_coordinator_selection.py
```

## Command Line Interface

Run the CLI interface:

```bash
export OPENAI_API_KEY="sk-proj-..."
uv run python cli.py
```

## Development Workflow

### Typical Development Session

1. **Start Backend Server** (Terminal 1):
   ```bash
   uv run server.py
   ```

2. **Start Frontend Server** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Make Changes**:
   - Backend changes: Server auto-reloads (if enabled)
   - Frontend changes: Hot module replacement (HMR) updates automatically

4. **Test Changes**:
   - Access frontend at `http://localhost:5173`
   - Check backend API at `http://localhost:8000/docs`

### File Structure

```
AI-Event-Planner-Agent/
├── custom_agents/          # AI agent implementations
├── custom_mcp_servers/      # MCP server implementations
├── workflows/              # Core workflow logic
├── tools/                  # Utility tools
├── frontend/               # React frontend
│   ├── src/               # Source files
│   └── package.json       # Frontend dependencies
├── server.py              # FastAPI backend server
├── cli.py                 # Command-line interface
├── .env                   # Environment variables (create this)
└── pyproject.toml         # Python project configuration
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in server.py or set PORT environment variable
export PORT=8001
uv run server.py
```

**Missing dependencies:**
```bash
uv sync
# or
pip install -e .
```

**Import errors:**
- Ensure you're in the project root directory
- Verify virtual environment is activated
- Check that all dependencies are installed

### Frontend Issues

**Port already in use:**
```bash
cd frontend
npm run dev -- --port 5174
```

**Missing dependencies:**
```bash
cd frontend
npm install
```

**Build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Environment Variables

**API key not found:**
- Verify `.env` file exists in project root
- Check that `OPENAI_API_KEY` is set correctly
- Ensure no extra spaces or quotes around the key

**Form creation fails:**
- Set `PLAN_EVENT_FORM_MODE=skip` to disable forms
- Or provide valid `TALLY_API_KEY` for form creation

## Development Tips

### Hot Reloading

- Backend: FastAPI auto-reloads on code changes (if `reload=True` in uvicorn)
- Frontend: Vite HMR automatically updates the browser

### Debugging

- Backend: Use Python debugger or print statements
- Frontend: Use browser DevTools and React DevTools
- API: Use FastAPI docs at `/docs` for testing endpoints

### Logging

- Backend logs: Check console output
- Frontend logs: Check browser console
- Workflow logs: Check `logs/` directory

## Production Build

### Frontend Production Build

```bash
cd frontend
npm run build
```

Built files will be in `frontend/dist/`.

### Backend Production

For production deployment:
- Use a production WSGI server (e.g., Gunicorn)
- Set appropriate environment variables
- Configure proper logging
- Enable security features

## Additional Resources

- [README.md](README.md) - Project overview and features
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [MCP_USAGE.md](MCP_USAGE.md) - MCP server usage guide

