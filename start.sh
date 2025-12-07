#!/bin/bash

# AI Event Planner - One-Command Startup Script
# This script validates environment configuration and launches both frontend and backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AI Event Planner - Startup Script                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. CHECK REQUIRED ENVIRONMENT VARIABLES
# ============================================================================
echo -e "${YELLOW}[1/5] Checking environment variables...${NC}"
echo ""

MISSING_VARS=()

# Check OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    MISSING_VARS+=("OPENAI_API_KEY")
    echo -e "${RED}✗ OPENAI_API_KEY${NC} - Not set"
else
    # Show first and last 4 chars
    KEY_PREVIEW="${OPENAI_API_KEY:0:4}...${OPENAI_API_KEY: -4}"
    echo -e "${GREEN}✓ OPENAI_API_KEY${NC} - $KEY_PREVIEW"
fi

# Check TALLY_API_KEY (optional but recommended)
if [ -z "$TALLY_API_KEY" ]; then
    echo -e "${YELLOW}⚠ TALLY_API_KEY${NC} - Not set (Optional, form creation will not work)"
else
    KEY_PREVIEW="${TALLY_API_KEY:0:4}...${TALLY_API_KEY: -4}"
    echo -e "${GREEN}✓ TALLY_API_KEY${NC} - $KEY_PREVIEW"
fi

echo ""

# ============================================================================
# 2. CHECK PYTHON ENVIRONMENT
# ============================================================================
echo -e "${YELLOW}[2/5] Checking Python environment...${NC}"
echo ""

# Check if .venv exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

# Activate venv
source "$SCRIPT_DIR/.venv/bin/activate"
echo -e "${GREEN}✓ Python venv activated${NC}"

# Check for required Python packages
REQUIRED_PACKAGES=("fastapi" "uvicorn" "pydantic" "openai")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import ${package}" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    else
        echo -e "${GREEN}✓${NC} $package"
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing packages: ${MISSING_PACKAGES[*]}...${NC}"
    pip install -q "${MISSING_PACKAGES[@]}"
    echo -e "${GREEN}✓ Packages installed${NC}"
fi

echo ""

# ============================================================================
# 3. CHECK NODE/NPM ENVIRONMENT
# ============================================================================
echo -e "${YELLOW}[3/5] Checking Node.js environment...${NC}"
echo ""

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js (v16+)${NC}"
    exit 1
fi

NODE_VERSION=$(node -v)
echo -e "${GREEN}✓ Node.js${NC} - $NODE_VERSION"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found.${NC}"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo -e "${GREEN}✓ npm${NC} - $NPM_VERSION"

# Check frontend dependencies
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd "$SCRIPT_DIR/frontend"
    npm install -q
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies${NC} - Already installed"
fi

echo ""

# ============================================================================
# 4. CHECK FRONTEND CONFIGURATION
# ============================================================================
echo -e "${YELLOW}[4/5] Checking frontend configuration...${NC}"
echo ""

FRONTEND_ENV="$SCRIPT_DIR/frontend/.env"
if [ ! -f "$FRONTEND_ENV" ]; then
    echo -e "${YELLOW}Creating frontend .env file...${NC}"
    cat > "$FRONTEND_ENV" << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✓ Frontend .env created${NC}"
else
    API_URL=$(grep "VITE_API_BASE_URL" "$FRONTEND_ENV" | cut -d'=' -f2)
    if [ -z "$API_URL" ]; then
        echo "VITE_API_BASE_URL=http://localhost:8000" >> "$FRONTEND_ENV"
        echo -e "${GREEN}✓ Added VITE_API_BASE_URL to .env${NC}"
    else
        echo -e "${GREEN}✓ VITE_API_BASE_URL${NC} - $API_URL"
    fi
fi

echo ""

# ============================================================================
# 5. FINAL VALIDATION
# ============================================================================
echo -e "${YELLOW}[5/5] Final validation...${NC}"
echo ""

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo -e "${YELLOW}Please set these variables:${NC}"
    echo "   export OPENAI_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""

# ============================================================================
# START SERVICES
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting services...                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Services stopped${NC}"
}

trap cleanup EXIT

# Start Backend
echo -e "${BLUE}Starting Backend (port 8000)...${NC}"
cd "$SCRIPT_DIR"
source .venv/bin/activate
uvicorn server:app --reload --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
sleep 2

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start. Check logs:${NC}"
    cat /tmp/backend.log
    exit 1
fi

# Start Frontend
echo -e "${BLUE}Starting Frontend (port 8081)...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Frontend failed to start. Check logs:${NC}"
    cat /tmp/frontend.log
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   All services running!                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:8081"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep the script running
wait
