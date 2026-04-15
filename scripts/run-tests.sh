#!/bin/bash
# EHS Monorepo - Test Runner Script
# 运行所有测试

set -e

echo "======================================"
echo "EHS Monorepo - Test Runner"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

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

# Run frontend tests
run_frontend_tests() {
    echo "--------------------------------------"
    print_info "Running Frontend Tests..."
    echo "--------------------------------------"

    if [[ -d "apps/admin-console" ]] && [[ -f "apps/admin-console/package.json" ]]; then
        cd apps/admin-console

        if npm test; then
            print_status "Frontend tests passed"
            ((TESTS_PASSED++))
        else
            print_error "Frontend tests failed"
            ((TESTS_FAILED++))
        fi

        cd ../..
    else
        print_info "Frontend app not found, skipping..."
    fi

    echo ""
}

# Run Python tests
run_python_tests() {
    echo "--------------------------------------"
    print_info "Running Python AI Service Tests..."
    echo "--------------------------------------"

    if [[ -d "apps/ehs-ai" ]] && [[ -f "apps/ehs-ai/pyproject.toml" ]]; then
        cd apps/ehs-ai

        if poetry run pytest; then
            print_status "Python tests passed"
            ((TESTS_PASSED++))
        else
            print_error "Python tests failed"
            ((TESTS_FAILED++))
        fi

        cd ../..
    else
        print_info "Python AI service not found, skipping..."
    fi

    echo ""
}

# Run Java tests
run_java_tests() {
    echo "--------------------------------------"
    print_info "Running Java Business Service Tests..."
    echo "--------------------------------------"

    if [[ -d "apps/ehs-business" ]] && [[ -f "apps/ehs-business/pom.xml" ]]; then
        cd apps/ehs-business

        if mvn test; then
            print_status "Java tests passed"
            ((TESTS_PASSED++))
        else
            print_error "Java tests failed"
            ((TESTS_FAILED++))
        fi

        cd ../..
    else
        print_info "Java business service not found, skipping..."
    fi

    echo ""
}

# Run monorepo structure tests
run_structure_tests() {
    echo "--------------------------------------"
    print_info "Running Monorepo Structure Tests..."
    echo "--------------------------------------"

    ERRORS=0

    # Check directory structure
    for dir in "apps/admin-console" "apps/ehs-business" "apps/ehs-ai" "scripts" "tests"; do
        if [[ -d "$dir" ]]; then
            print_status "Directory exists: $dir"
        else
            print_error "Missing directory: $dir"
            ((ERRORS++))
        fi
    done

    # Check configuration files
    if [[ -f "apps/admin-console/package.json" ]]; then
        print_status "Frontend config exists"
    else
        print_error "Missing apps/admin-console/package.json"
        ((ERRORS++))
    fi

    if [[ -f "apps/ehs-business/pom.xml" ]]; then
        print_status "Java config exists"
    else
        print_error "Missing apps/ehs-business/pom.xml"
        ((ERRORS++))
    fi

    if [[ -f "apps/ehs-ai/pyproject.toml" ]]; then
        print_status "Python config exists"
    else
        print_error "Missing apps/ehs-ai/pyproject.toml"
        ((ERRORS++))
    fi

    if [[ -f "package.json" ]]; then
        print_status "Root package.json exists"
    else
        print_error "Missing root package.json"
        ((ERRORS++))
    fi

    if [[ -f "Makefile" ]]; then
        print_status "Makefile exists"
    else
        print_error "Missing Makefile"
        ((ERRORS++))
    fi

    if [[ -f "scripts/setup.sh" ]]; then
        print_status "Setup script exists"
    else
        print_error "Missing scripts/setup.sh"
        ((ERRORS++))
    fi

    if [[ -f "scripts/run-tests.sh" ]]; then
        print_status "Test runner script exists"
    else
        print_error "Missing scripts/run-tests.sh"
        ((ERRORS++))
    fi

    if [[ $ERRORS -eq 0 ]]; then
        print_status "Monorepo structure tests passed"
        ((TESTS_PASSED++))
    else
        print_error "Monorepo structure tests failed with $ERRORS errors"
        ((TESTS_FAILED++))
    fi

    echo ""
}

# Main test runner
main() {
    echo "Starting test suite..."
    echo ""

    run_structure_tests
    run_frontend_tests
    run_python_tests
    # run_java_tests  # Commented out by default as Java may not be installed

    echo "======================================"
    echo "Test Summary"
    echo "======================================"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main
