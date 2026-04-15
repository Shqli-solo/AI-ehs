#!/bin/bash
# EHS Monorepo - Setup Script
# 初始化开发环境

set -e

echo "======================================"
echo "EHS Monorepo - Setup Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo -e "${YELLOW}Detected Windows environment${NC}"
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[→]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    echo ""

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_status "Node.js installed: $NODE_VERSION"
    else
        print_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm -v)
        print_status "npm installed: $NPM_VERSION"
    else
        print_error "npm not found"
        exit 1
    fi

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_status "Python installed: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version)
        print_status "Python installed: $PYTHON_VERSION"
    else
        print_error "Python not found. Please install Python 3.11+"
        exit 1
    fi

    # Check Poetry
    if command -v poetry &> /dev/null; then
        POETRY_VERSION=$(poetry --version)
        print_status "Poetry installed: $POETRY_VERSION"
    else
        print_error "Poetry not found. Installing..."
        if [[ "$IS_WINDOWS" == true ]]; then
            print_info "Windows detected. Please install Poetry using one of these methods:"
            print_info "  Method 1 (using pip): pip install poetry"
            print_info "  Method 2 (PowerShell): (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
            print_info "  Method 3 (WSL recommended): Use WSL (Windows Subsystem for Linux) for better compatibility"
            print_info "After installing Poetry, re-run this setup script."
            exit 1
        else
            curl -sSL https://install.python-poetry.org | python3 -
        fi
    fi

    # Check Java (for Maven)
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | head -n 1)
        print_status "Java installed: $JAVA_VERSION"
    else
        print_info "Java not found. Install Java 17+ for Java business service"
    fi

    # Check Maven
    if command -v mvn &> /dev/null; then
        MAVEN_VERSION=$(mvn -v | head -n 1)
        print_status "Maven installed: $MAVEN_VERSION"
    else
        print_info "Maven not found. Install Maven for Java business service"
    fi

    echo ""
}

# Install frontend dependencies
install_frontend() {
    print_info "Installing frontend dependencies..."

    if [[ -d "apps/admin-console" ]]; then
        cd apps/admin-console
        npm install
        cd ../..
        print_status "Frontend dependencies installed"
    else
        print_error "apps/admin-console directory not found"
    fi

    echo ""
}

# Install Python dependencies
install_python() {
    print_info "Installing Python AI service dependencies..."

    if [[ -d "apps/ehs-ai" ]]; then
        cd apps/ehs-ai
        poetry install
        cd ../..
        print_status "Python dependencies installed"
    else
        print_error "apps/ehs-ai directory not found"
    fi

    echo ""
}

# Setup environment files
setup_env() {
    print_info "Setting up environment files..."

    # Frontend env
    if [[ -f "apps/admin-console/.env.example" ]]; then
        cp "apps/admin-console/.env.example" "apps/admin-console/.env.local"
        print_status "Frontend environment file created"
    fi

    # Python env
    if [[ -f "apps/ehs-ai/.env.example" ]]; then
        cp "apps/ehs-ai/.env.example" "apps/ehs-ai/.env"
        print_status "Python environment file created"
    fi

    echo ""
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."

    mkdir -p apps/admin-console
    mkdir -p apps/ehs-business
    mkdir -p apps/ehs-ai
    mkdir -p scripts
    mkdir -p tests

    print_status "Directory structure verified"
    echo ""
}

# Main setup process
main() {
    echo ""
    check_prerequisites
    create_directories
    setup_env
    install_frontend
    install_python

    echo "======================================"
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "  1. Configure environment variables in apps/admin-console/.env.local"
    echo "  2. Configure environment variables in apps/ehs-ai/.env"
    echo "  3. Run 'make dev' to start frontend development server"
    echo "  4. Run 'make dev:backend' to start Python AI service"
    echo "  5. Run 'make test' to run all tests"
    echo ""
}

# Run main function
main
