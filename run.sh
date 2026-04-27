#!/bin/bash
#
# Real-Time Analytics SaaS - Dev CLI
# Usage: ./run.sh [start|stop|restart|reset|status]
#

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# Load config
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

PORT=${PORT:-8001}
DASHBOARD_PORT=${DASHBOARD_PORT:-9999}

PID_DIR="$BASE_DIR/.pids"
mkdir -p "$PID_DIR"

BACKEND_PID_FILE="$PID_DIR/backend.pid"
DASHBOARD_PID_FILE="$PID_DIR/dashboard.pid"

BACKEND_LOG="/tmp/analytics_backend.log"
DASHBOARD_LOG="/tmp/analytics_dashboard.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[*]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

# Read PID from file
get_pid() {
    local file=$1
    [ -f "$file" ] && cat "$file"
}

# Check if process is running
is_running() {
    local pid=$(get_pid $1)
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# Save PID to file
save_pid() {
    echo "$1" > "$2"
}

# Stop a process
stop_process() {
    local pid=$(get_pid $1)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
        sleep 1
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null
        fi
    fi
    rm -f "$1"
}

# Cleanup handler
cleanup() {
    log "Stopping services..."
    stop_process "$BACKEND_PID_FILE"
    stop_process "$DASHBOARD_PID_FILE"
    log "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log "$name is ready!"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    echo ""
    return 1
}

# Start backend
start_backend() {
    log "Starting Backend API on port $PORT..."
    
    if is_running "$BACKEND_PID_FILE"; then
        warn "Backend already running"
        return 0
    fi
    
    setsid python3 -u server.py $PORT > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    sleep 2
    save_pid "$pid" "$BACKEND_PID_FILE"
    
    if ! wait_for_service "http://localhost:$PORT/health" "Backend"; then
        error "Backend failed to start. Check $BACKEND_LOG"
        rm -f "$BACKEND_PID_FILE"
        return 1
    fi
}

# Create demo data
create_demo_data() {
    log "Creating demo app and events..."
    
    APP=$(curl -s -X POST "http://localhost:$PORT/api/apps" -H "Content-Type: application/json" -d '{"name": "Demo App"}')
    API_KEY=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])" 2>/dev/null)
    SECRET=$(echo $APP | python3 -c "import sys,json; print(json.load(sys.stdin)['secret_key'])" 2>/dev/null)
    
    if [ -z "$API_KEY" ]; then
        warn "Could not create demo app"
        return 1
    fi
    
    # Send demo events
    for i in $(seq 1 25); do
        USER=$(( (i % 5) + 1 ))
        case $i in
            [1-9]|10) ET="page_view" ;;
            1[1-7]) ET="click" ;;
            1[8-9]|2[0-1]) ET="signup" ;;
            *) ET="purchase" ;;
        esac
        curl -s -X POST "http://localhost:$PORT/track" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -H "X-Secret-Key: $SECRET" \
            -d "{\"event_type\": \"$ET\", \"user_id\": \"user$USER\", \"properties\": {\"i\": $i}}" > /dev/null 2>&1
    done
    
    # Save API keys
    cat > "$BASE_DIR/.api_keys" << EOF
API_KEY=$API_KEY
SECRET_KEY=$SECRET
BACKEND=http://localhost:$PORT
DASHBOARD=http://localhost:$DASHBOARD_PORT/dashboard.html
EOF
    
    log "API Key: $API_KEY"
    log "Demo events: 25"
}

# Start dashboard
start_dashboard() {
    log "Starting Dashboard on port $DASHBOARD_PORT..."
    
    if is_running "$DASHBOARD_PID_FILE"; then
        warn "Dashboard already running"
        return 0
    fi
    
    # Check for Next.js dashboard
    if [ -d "dashboard-next" ] && [ -f "dashboard-next/package.json" ]; then
        cd dashboard-next
        if command -v npm &> /dev/null; then
            setsid npm run dev > "$DASHBOARD_LOG" 2>&1 &
            save_pid $! "$DASHBOARD_PID_FILE"
            wait_for_service "http://localhost:3000" "Next.js Frontend"
            cd "$BASE_DIR"
            return 0
        fi
    fi
    
    # Fallback to simple HTTP server
    setsid python3 -m http.server "$DASHBOARD_PORT" > "$DASHBOARD_LOG" 2>&1 &
    save_pid $! "$DASHBOARD_PID_FILE"
    
    if ! wait_for_service "http://localhost:$DASHBOARD_PORT" "Dashboard"; then
        error "Dashboard failed to start. Check $DASHBOARD_LOG"
        rm -f "$DASHBOARD_PID_FILE"
        cd "$BASE_DIR"
        return 1
    fi
    
    cd "$BASE_DIR"
}

# Open browser
open_browser() {
    log "Opening dashboard in browser..."
    xdg-open "http://localhost:$DASHBOARD_PORT/dashboard.html" >/dev/null 2>&1 &
    # Firefox fallback
    if ! pgrep -f "firefox" > /dev/null; then
        firefox "http://localhost:$DASHBOARD_PORT/dashboard.html" 2>/dev/null &
    fi
}

# Status command
do_status() {
    echo ""
    echo "=========================================="
    echo "  Analytics SaaS Status"
    echo "=========================================="
    echo ""
    
    if is_running "$BACKEND_PID_FILE"; then
        echo -e "  ${GREEN}●${NC} Backend API  : http://localhost:$PORT"
    else
        echo -e "  ${RED}●${NC} Backend API  : Not running"
    fi
    
    if is_running "$DASHBOARD_PID_FILE"; then
        echo -e "  ${GREEN}●${NC} Dashboard   : http://localhost:$DASHBOARD_PORT/dashboard.html"
    else
        echo -e "  ${RED}●${NC} Dashboard   : Not running"
    fi
    
    echo ""
    if [ -f "$BASE_DIR/.api_keys" ]; then
        echo "  API Keys:"
        cat "$BASE_DIR/.api_keys" | sed 's/^/    /'
    fi
    echo ""
}

# Main command router
case "${1:-start}" in
    start)
        echo ""
        echo "=========================================="
        echo "  Real-Time Analytics SaaS"
        echo "=========================================="
        echo ""
        
        start_backend || exit 1
        create_demo_data
        start_dashboard || exit 1
        open_browser
        
        echo ""
        echo "=========================================="
        echo "  Ready!"
        echo "=========================================="
        echo ""
        echo "  Backend : http://localhost:$PORT"
        echo "  Dashboard: http://localhost:$DASHBOARD_PORT/dashboard.html"
        echo ""
        echo "  Commands: ./run.sh stop | restart | status | reset"
        echo ""
        echo "Press Ctrl+C to stop all services."
        echo ""
        
        # Keep running (services are backgrounded)
        while true; do sleep 10; done
        ;;
    
    stop)
        log "Stopping services..."
        cleanup
        ;;
    
    restart)
        stop_process "$BACKEND_PID_FILE"
        stop_process "$DASHBOARD_PID_FILE"
        sleep 2
        exec "$0" start
        ;;
    
    reset)
        if [ -f "analytics.db" ]; then
            rm -f analytics.db
            log "Database reset."
        else
            warn "No database to reset."
        fi
        exit 0
        ;;
    
    status)
        do_status
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|reset|status}"
        echo ""
        echo "  start   - Start all services (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  reset   - Reset database"
        echo "  status  - Show service status"
        exit 1
        ;;
esac