#!/bin/bash

###############################################################################
# Unity Catalog Chatbot - Automated Deployment Script
# This script will guide you through the complete setup and deployment
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# STEP 1: PRE-FLIGHT CHECKS
###############################################################################

print_header "Step 1: Pre-flight Checks"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check pip
if command_exists pip3; then
    print_success "pip3 found"
else
    print_error "pip3 is not installed"
    exit 1
fi

# Check Docker (optional)
if command_exists docker; then
    print_success "Docker found: $(docker --version)"
    DOCKER_AVAILABLE=true
else
    print_warning "Docker not found. Docker deployment will not be available."
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose (optional)
if command_exists docker-compose; then
    print_success "Docker Compose found: $(docker-compose --version)"
    COMPOSE_AVAILABLE=true
else
    print_warning "Docker Compose not found"
    COMPOSE_AVAILABLE=false
fi

###############################################################################
# STEP 2: GATHER CREDENTIALS
###############################################################################

print_header "Step 2: Configuration Setup"

# Check if .env exists
if [ -f .env ]; then
    print_warning ".env file already exists"
    read -p "Do you want to overwrite it? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        print_info "Using existing .env file"
        ENV_CONFIGURED=true
    else
        ENV_CONFIGURED=false
    fi
else
    ENV_CONFIGURED=false
fi

if [ "$ENV_CONFIGURED" = false ]; then
    print_info "Let's configure your credentials..."
    
    # Databricks configuration
    echo ""
    print_info "DATABRICKS CONFIGURATION"
    read -p "Enter your Databricks workspace URL (e.g., https://adb-xxx.azuredatabricks.net): " DATABRICKS_HOST
    read -p "Enter your Databricks personal access token: " DATABRICKS_TOKEN
    read -p "Enter your SQL Warehouse ID (optional, press Enter to skip): " DATABRICKS_WAREHOUSE_ID
    
    # Anthropic configuration
    echo ""
    print_info "ANTHROPIC CONFIGURATION"
    read -p "Enter your Anthropic API key (sk-ant-...): " ANTHROPIC_API_KEY
    
    # Create .env file
    cat > .env << EOF
# Databricks Configuration
DATABRICKS_HOST=$DATABRICKS_HOST
DATABRICKS_TOKEN=$DATABRICKS_TOKEN
DATABRICKS_WAREHOUSE_ID=$DATABRICKS_WAREHOUSE_ID

# Anthropic API Configuration
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
FLASK_ENV=development
LOG_LEVEL=INFO

# Features
ENABLE_SQL_EXECUTION=false
ENABLE_BATCH_OPS=true
ENABLE_AUDIT_LOG=true
ENABLE_CACHING=false
EOF
    
    print_success ".env file created successfully"
fi

###############################################################################
# STEP 3: CHOOSE DEPLOYMENT METHOD
###############################################################################

print_header "Step 3: Choose Deployment Method"

echo "Available deployment options:"
echo "1) Local Python (recommended for testing)"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "2) Docker"
fi
if [ "$COMPOSE_AVAILABLE" = true ]; then
    echo "3) Docker Compose (full stack)"
fi

read -p "Enter your choice (1-3): " DEPLOY_CHOICE

###############################################################################
# STEP 4: DEPLOYMENT
###############################################################################

print_header "Step 4: Deployment"

case $DEPLOY_CHOICE in
    1)
        # Local Python deployment
        print_info "Setting up local Python environment..."
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            print_info "Creating virtual environment..."
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        # Activate virtual environment
        print_info "Activating virtual environment..."
        source venv/bin/activate
        
        # Upgrade pip
        print_info "Upgrading pip..."
        pip install --upgrade pip > /dev/null 2>&1
        
        # Install dependencies
        print_info "Installing dependencies..."
        pip install -r requirements.txt
        print_success "Dependencies installed"
        
        # Start the application in background
        print_info "Starting application..."
        nohup python app.py > app.log 2>&1 &
        APP_PID=$!
        echo $APP_PID > app.pid
        
        # Wait for startup
        sleep 5
        
        if ps -p $APP_PID > /dev/null; then
            print_success "Application started successfully (PID: $APP_PID)"
            DEPLOYMENT_TYPE="local"
        else
            print_error "Application failed to start. Check app.log for details."
            exit 1
        fi
        ;;
        
    2)
        # Docker deployment
        if [ "$DOCKER_AVAILABLE" = false ]; then
            print_error "Docker is not available"
            exit 1
        fi
        
        print_info "Building Docker image..."
        docker build -t unity-catalog-chatbot:latest .
        print_success "Docker image built"
        
        print_info "Starting Docker container..."
        docker run -d \
            --name unity-catalog-chatbot \
            -p 5000:5000 \
            --env-file .env \
            unity-catalog-chatbot:latest
        
        print_success "Docker container started"
        DEPLOYMENT_TYPE="docker"
        ;;
        
    3)
        # Docker Compose deployment
        if [ "$COMPOSE_AVAILABLE" = false ]; then
            print_error "Docker Compose is not available"
            exit 1
        fi
        
        print_info "Starting services with Docker Compose..."
        docker-compose up -d
        print_success "Services started"
        DEPLOYMENT_TYPE="compose"
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

###############################################################################
# STEP 5: HEALTH CHECK
###############################################################################

print_header "Step 5: Health Check"

print_info "Waiting for application to be ready..."
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        print_success "Application is healthy!"
        
        # Get health check response
        HEALTH_RESPONSE=$(curl -s http://localhost:5000/api/health)
        echo -e "${GREEN}Health Check Response:${NC}"
        echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Application failed health check"
    
    if [ "$DEPLOYMENT_TYPE" = "local" ]; then
        print_info "Check app.log for error details:"
        tail -n 20 app.log
    elif [ "$DEPLOYMENT_TYPE" = "docker" ]; then
        print_info "Check Docker logs:"
        docker logs unity-catalog-chatbot
    elif [ "$DEPLOYMENT_TYPE" = "compose" ]; then
        print_info "Check Docker Compose logs:"
        docker-compose logs
    fi
    
    exit 1
fi

###############################################################################
# STEP 6: AUTOMATED TESTING
###############################################################################

print_header "Step 6: Automated Testing"

print_info "Running automated tests..."

# Test 1: Health endpoint
print_info "Test 1: Health endpoint"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)
if [ "$HEALTH_STATUS" = "200" ]; then
    print_success "Health endpoint: PASSED"
else
    print_error "Health endpoint: FAILED (Status: $HEALTH_STATUS)"
fi

# Test 2: Chat endpoint with help command
print_info "Test 2: Chat endpoint (help command)"
CHAT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "help"}' \
    -w "\n%{http_code}")

CHAT_STATUS=$(echo "$CHAT_RESPONSE" | tail -n 1)
CHAT_BODY=$(echo "$CHAT_RESPONSE" | head -n -1)

if [ "$CHAT_STATUS" = "200" ]; then
    print_success "Chat endpoint: PASSED"
    echo -e "${BLUE}Response:${NC}"
    echo "$CHAT_BODY" | python3 -m json.tool 2>/dev/null | head -n 20
else
    print_error "Chat endpoint: FAILED (Status: $CHAT_STATUS)"
fi

# Test 3: List catalogs
print_info "Test 3: List catalogs"
CATALOGS_RESPONSE=$(curl -s -X POST http://localhost:5000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "list all catalogs"}' \
    -w "\n%{http_code}")

CATALOGS_STATUS=$(echo "$CATALOGS_RESPONSE" | tail -n 1)
if [ "$CATALOGS_STATUS" = "200" ]; then
    print_success "List catalogs: PASSED"
else
    print_error "List catalogs: FAILED (Status: $CATALOGS_STATUS)"
fi

###############################################################################
# STEP 7: INTERACTIVE TESTING
###############################################################################

print_header "Step 7: Interactive Testing"

echo ""
print_info "Application is ready for interactive testing!"
echo ""
echo -e "${GREEN}Access URLs:${NC}"
echo "  API Backend:  http://localhost:5000"
echo "  Health Check: http://localhost:5000/api/health"
echo "  Swagger Docs: http://localhost:5000/docs (if enabled)"
echo ""

read -p "Would you like to test the chatbot interactively? (y/n): " INTERACTIVE

if [ "$INTERACTIVE" = "y" ]; then
    print_info "Interactive Chatbot Test"
    echo ""
    echo "Enter your commands (or 'exit' to quit):"
    echo "Examples:"
    echo "  - Create a catalog named test_catalog"
    echo "  - List all catalogs"
    echo "  - Grant SELECT on test_catalog to data_analysts"
    echo ""
    
    while true; do
        read -p "You: " USER_INPUT
        
        if [ "$USER_INPUT" = "exit" ]; then
            break
        fi
        
        # Make API call
        RESPONSE=$(curl -s -X POST http://localhost:5000/api/chat \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"$USER_INPUT\"}")
        
        # Extract message from JSON
        MESSAGE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'No response'))" 2>/dev/null)
        SQL=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('sql', ''))" 2>/dev/null)
        
        echo -e "${BLUE}Assistant:${NC} $MESSAGE"
        
        if [ ! -z "$SQL" ]; then
            echo -e "${YELLOW}SQL:${NC} $SQL"
        fi
        echo ""
    done
fi

###############################################################################
# STEP 8: DEPLOYMENT SUMMARY
###############################################################################

print_header "Deployment Summary"

echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo "Deployment Type: $DEPLOYMENT_TYPE"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Access the API at: http://localhost:5000"
echo "2. Review the logs:"

case $DEPLOYMENT_TYPE in
    "local")
        echo "   - Application logs: tail -f app.log"
        echo "3. Stop the application:"
        echo "   - kill \$(cat app.pid)"
        ;;
    "docker")
        echo "   - Docker logs: docker logs -f unity-catalog-chatbot"
        echo "3. Stop the application:"
        echo "   - docker stop unity-catalog-chatbot"
        ;;
    "compose")
        echo "   - Docker Compose logs: docker-compose logs -f"
        echo "3. Stop the application:"
        echo "   - docker-compose down"
        ;;
esac

echo ""
echo "4. Run tests: pytest test_chatbot.py"
echo "5. View documentation: cat README.md"
echo ""

# Create quick reference file
cat > QUICK_REFERENCE.txt << EOF
Unity Catalog Chatbot - Quick Reference
========================================

Deployment Type: $DEPLOYMENT_TYPE

URLs:
- API: http://localhost:5000
- Health: http://localhost:5000/api/health

Logs:
EOF

case $DEPLOYMENT_TYPE in
    "local")
        echo "- Application: tail -f app.log" >> QUICK_REFERENCE.txt
        echo "" >> QUICK_REFERENCE.txt
        echo "Stop Application:" >> QUICK_REFERENCE.txt
        echo "kill \$(cat app.pid)" >> QUICK_REFERENCE.txt
        ;;
    "docker")
        echo "- Docker: docker logs -f unity-catalog-chatbot" >> QUICK_REFERENCE.txt
        echo "" >> QUICK_REFERENCE.txt
        echo "Stop Application:" >> QUICK_REFERENCE.txt
        echo "docker stop unity-catalog-chatbot" >> QUICK_REFERENCE.txt
        ;;
    "compose")
        echo "- Docker Compose: docker-compose logs -f" >> QUICK_REFERENCE.txt
        echo "" >> QUICK_REFERENCE.txt
        echo "Stop Application:" >> QUICK_REFERENCE.txt
        echo "docker-compose down" >> QUICK_REFERENCE.txt
        ;;
esac

cat >> QUICK_REFERENCE.txt << EOF

Sample Commands:
- Create catalog: "Create a catalog named test_catalog"
- Create schema: "Create schema analytics in test_catalog"
- Grant permission: "Grant SELECT on test_catalog to user@example.com"
- List catalogs: "List all catalogs"

For detailed documentation, see README.md
EOF

print_success "Quick reference saved to QUICK_REFERENCE.txt"

echo ""
print_success "Deployment complete! Happy chatting! 🎉"
