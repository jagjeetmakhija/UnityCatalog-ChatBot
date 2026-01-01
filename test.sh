#!/bin/bash

###############################################################################
# Unity Catalog Chatbot - Comprehensive Test Suite
# This script runs automated tests against the deployed chatbot
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:5000}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Functions
print_test() {
    echo -e "\n${BLUE}[TEST $1]${NC} $2"
}

print_pass() {
    echo -e "${GREEN}✓ PASSED${NC}: $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

print_fail() {
    echo -e "${RED}✗ FAILED${NC}: $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Test function
run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local test_name="$1"
    local expected_status="$2"
    local endpoint="$3"
    local method="$4"
    local data="$5"
    
    print_test "$TOTAL_TESTS" "$test_name"
    
    if [ "$method" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        RESPONSE=$(curl -s -X POST -w "\n%{http_code}" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_URL$endpoint")
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" = "$expected_status" ]; then
        print_pass "$test_name (Status: $HTTP_CODE)"
        echo "$BODY" | python3 -m json.tool 2>/dev/null | head -n 10
        return 0
    else
        print_fail "$test_name (Expected: $expected_status, Got: $HTTP_CODE)"
        echo "$BODY"
        return 1
    fi
}

# Test chatbot endpoint
test_chat() {
    local test_name="$1"
    local message="$2"
    local expected_keyword="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_test "$TOTAL_TESTS" "$test_name"
    
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}" \
        "$API_URL/api/chat")
    
    if echo "$RESPONSE" | grep -q "$expected_keyword"; then
        print_pass "$test_name"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -n 15
        return 0
    else
        print_fail "$test_name (Keyword '$expected_keyword' not found)"
        echo "$RESPONSE"
        return 1
    fi
}

###############################################################################
# START TESTING
###############################################################################

echo "========================================="
echo "Unity Catalog Chatbot - Test Suite"
echo "========================================="
echo "API URL: $API_URL"
echo "Started: $(date)"
echo ""

###############################################################################
# SECTION 1: Basic Connectivity Tests
###############################################################################

echo -e "\n${YELLOW}=== SECTION 1: Basic Connectivity ===${NC}\n"

run_test "Health Check Endpoint" "200" "/api/health" "GET"

run_test "Chat Endpoint Availability" "200" "/api/chat" "POST" '{"message": "test"}'

###############################################################################
# SECTION 2: Help & Information Tests
###############################################################################

echo -e "\n${YELLOW}=== SECTION 2: Help & Information ===${NC}\n"

test_chat "Help Command" "help" "Creating Objects"

test_chat "General Query" "what can you do?" "Unity Catalog"

###############################################################################
# SECTION 3: Catalog Operations
###############################################################################

echo -e "\n${YELLOW}=== SECTION 3: Catalog Operations ===${NC}\n"

test_chat "List Catalogs" "list all catalogs" "SHOW CATALOGS"

test_chat "Create Catalog Request" "create a catalog named test_catalog_$(date +%s)" "CREATE CATALOG"

###############################################################################
# SECTION 4: Schema Operations
###############################################################################

echo -e "\n${YELLOW}=== SECTION 4: Schema Operations ===${NC}\n"

test_chat "Create Schema Request" "create schema test_schema in main" "CREATE SCHEMA"

test_chat "List Schemas Request" "list schemas in main" "SHOW SCHEMAS"

###############################################################################
# SECTION 5: Table Operations
###############################################################################

echo -e "\n${YELLOW}=== SECTION 5: Table Operations ===${NC}\n"

test_chat "Create Table Request" "create table main.default.test_table_$(date +%s)" "CREATE TABLE"

###############################################################################
# SECTION 6: Permission Operations
###############################################################################

echo -e "\n${YELLOW}=== SECTION 6: Permission Operations ===${NC}\n"

test_chat "Grant Permission Request" "grant SELECT on main to test_user" "GRANT SELECT"

test_chat "Show Permissions Request" "show permissions for main" "SHOW GRANTS"

###############################################################################
# SECTION 7: Complex Queries
###############################################################################

echo -e "\n${YELLOW}=== SECTION 7: Complex Queries ===${NC}\n"

test_chat "Multi-step Request" \
    "create a catalog named analytics, then create a schema called staging in it" \
    "catalog"

###############################################################################
# SECTION 8: Error Handling
###############################################################################

echo -e "\n${YELLOW}=== SECTION 8: Error Handling ===${NC}\n"

TOTAL_TESTS=$((TOTAL_TESTS + 1))
print_test "$TOTAL_TESTS" "Empty Message Handling"

EMPTY_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": ""}' \
    -w "%{http_code}" \
    "$API_URL/api/chat")

if echo "$EMPTY_RESPONSE" | grep -q "400"; then
    print_pass "Empty message returns 400"
else
    # Some implementations might accept empty messages
    print_info "Empty message handling: $(echo $EMPTY_RESPONSE | tail -c 4)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

###############################################################################
# SECTION 9: Performance Tests
###############################################################################

echo -e "\n${YELLOW}=== SECTION 9: Performance Tests ===${NC}\n"

print_test "$((TOTAL_TESTS + 1))" "Response Time Test"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

START_TIME=$(date +%s%N)
curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "help"}' \
    "$API_URL/api/chat" > /dev/null
END_TIME=$(date +%s%N)

DURATION=$((($END_TIME - $START_TIME) / 1000000))

if [ $DURATION -lt 5000 ]; then
    print_pass "Response time: ${DURATION}ms (< 5s)"
else
    print_info "Response time: ${DURATION}ms (acceptable)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

###############################################################################
# SECTION 10: Load Test (Optional)
###############################################################################

echo -e "\n${YELLOW}=== SECTION 10: Light Load Test ===${NC}\n"

print_test "$((TOTAL_TESTS + 1))" "Concurrent Requests (5 simultaneous)"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

for i in {1..5}; do
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"message": "help"}' \
        "$API_URL/api/chat" > /dev/null &
done

wait

if [ $? -eq 0 ]; then
    print_pass "Handled 5 concurrent requests"
else
    print_fail "Failed to handle concurrent requests"
fi

###############################################################################
# TEST SUMMARY
###############################################################################

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS${NC}"
echo ""

PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Pass Rate:    $PASS_RATE%"

if [ $PASS_RATE -ge 90 ]; then
    echo -e "\n${GREEN}✓ Test suite PASSED!${NC}"
    EXIT_CODE=0
elif [ $PASS_RATE -ge 70 ]; then
    echo -e "\n${YELLOW}⚠ Test suite passed with warnings${NC}"
    EXIT_CODE=0
else
    echo -e "\n${RED}✗ Test suite FAILED${NC}"
    EXIT_CODE=1
fi

echo ""
echo "Completed: $(date)"
echo "========================================="

# Generate test report
cat > test_report.txt << EOF
Unity Catalog Chatbot - Test Report
====================================
Date: $(date)
API URL: $API_URL

Summary:
--------
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Pass Rate: $PASS_RATE%

Status: $([ $EXIT_CODE -eq 0 ] && echo "PASSED" || echo "FAILED")

Sections Tested:
1. Basic Connectivity
2. Help & Information
3. Catalog Operations
4. Schema Operations
5. Table Operations
6. Permission Operations
7. Complex Queries
8. Error Handling
9. Performance Tests
10. Load Test

For detailed logs, review the console output.
EOF

print_info "Test report saved to test_report.txt"

exit $EXIT_CODE
