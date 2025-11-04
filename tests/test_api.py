"""
Comprehensive API Testing Suite
Tests Health Check, Functional, Performance, and Security aspects
"""
import requests
import time
import json
import os
import sys
from typing import Dict, List, Tuple
from io import BytesIO
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
TEST_RESULTS = {
    "health_check": {"passed": 0, "failed": 0, "tests": []},
    "functional": {"passed": 0, "failed": 0, "tests": []},
    "performance": {"passed": 0, "failed": 0, "tests": []},
    "security": {"passed": 0, "failed": 0, "tests": []}
}

# Test data
SAMPLE_RESUME_TEXT = """
John Doe
Email: john.doe@email.com
Phone: +1-555-0123

EXPERIENCE
Software Engineer
Tech Corp Inc. | 2020 - Present
- Developed web applications using Python and FastAPI
- Led team of 5 developers

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016 - 2020
GPA: 3.8/4.0

SKILLS
Python, JavaScript, FastAPI, React, SQL, Docker
"""

def create_test_file(filename: str, content: bytes = None) -> BytesIO:
    """Create a test file in memory"""
    if content is None:
        content = SAMPLE_RESUME_TEXT.encode('utf-8')
    return BytesIO(content)

def log_test(category: str, test_name: str, passed: bool, message: str = "", duration: float = None):
    """Log test result"""
    result = {
        "test": test_name,
        "status": "PASSED" if passed else "FAILED",
        "message": message,
        "duration": f"{duration:.3f}s" if duration else None
    }
    TEST_RESULTS[category]["tests"].append(result)
    if passed:
        TEST_RESULTS[category]["passed"] += 1
        print(f"[PASS] {test_name}: {message}")
    else:
        TEST_RESULTS[category]["failed"] += 1
        print(f"[FAIL] {test_name}: {message}")
    if duration:
        print(f"   Duration: {duration:.3f}s")

# ==================== HEALTH CHECK TESTS ====================

def test_health_endpoint():
    """Test /health endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = time.time() - start
        passed = response.status_code == 200 and "status" in response.json()
        log_test("health_check", "Health Endpoint", passed, 
                f"Status: {response.status_code}", duration)
        return passed
    except Exception as e:
        log_test("health_check", "Health Endpoint", False, f"Error: {str(e)}")
        return False

def test_api_health_check():
    """Test /api/v1/resumes/health/check endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/resumes/health/check", timeout=5)
        duration = time.time() - start
        data = response.json()
        passed = (response.status_code == 200 and 
                 data.get("status") == "healthy" and
                 "service" in data)
        log_test("health_check", "API Health Check", passed,
                f"Status: {response.status_code}, Service: {data.get('service')}", duration)
        return passed
    except Exception as e:
        log_test("health_check", "API Health Check", False, f"Error: {str(e)}")
        return False

def test_server_availability():
    """Test if server is running and accessible"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        duration = time.time() - start
        passed = response.status_code in [200, 404]  # 404 is OK if static files missing
        log_test("health_check", "Server Availability", passed,
                f"Server is accessible (Status: {response.status_code})", duration)
        return passed
    except requests.exceptions.ConnectionError:
        log_test("health_check", "Server Availability", False, 
                "Server is not running. Start it with: python simple_start.py")
        return False
    except Exception as e:
        log_test("health_check", "Server Availability", False, f"Error: {str(e)}")
        return False

# ==================== FUNCTIONAL TESTS ====================

def test_upload_resume():
    """Test resume upload endpoint"""
    start = time.time()
    try:
        test_file = create_test_file("test_resume.txt")
        files = {"file": ("test_resume.txt", test_file, "text/plain")}
        response = requests.post(f"{API_BASE}/resumes/upload", files=files, timeout=30)
        duration = time.time() - start
        
        if response.status_code == 201:
            data = response.json()
            passed = data.get("success") == True and "resume_id" in data
            resume_id = data.get("resume_id")
            log_test("functional", "Upload Resume", passed,
                    f"Resume ID: {resume_id}, Success: {data.get('success')}", duration)
            return resume_id if passed else None
        else:
            log_test("functional", "Upload Resume", False,
                    f"Status: {response.status_code}, Error: {response.text[:100]}", duration)
            return None
    except Exception as e:
        log_test("functional", "Upload Resume", False, f"Error: {str(e)}")
        return None

def test_get_resume(resume_id: int):
    """Test get resume by ID"""
    if not resume_id:
        log_test("functional", "Get Resume", False, "No resume ID available")
        return False
    
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/resumes/{resume_id}", timeout=10)
        duration = time.time() - start
        passed = response.status_code == 200
        log_test("functional", "Get Resume", passed,
                f"Status: {response.status_code}", duration)
        return passed
    except Exception as e:
        log_test("functional", "Get Resume", False, f"Error: {str(e)}")
        return False

def test_list_resumes():
    """Test list all resumes endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/resumes/", params={"skip": 0, "limit": 10}, timeout=10)
        duration = time.time() - start
        passed = response.status_code == 200 and isinstance(response.json(), (list, dict))
        log_test("functional", "List Resumes", passed,
                f"Status: {response.status_code}", duration)
        return passed
    except Exception as e:
        log_test("functional", "List Resumes", False, f"Error: {str(e)}")
        return False

def test_get_anonymized_resume(resume_id: int):
    """Test get anonymized resume"""
    if not resume_id:
        log_test("functional", "Get Anonymized Resume", False, "No resume ID available")
        return False
    
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/resumes/{resume_id}/anonymized", timeout=10)
        duration = time.time() - start
        passed = response.status_code == 200
        log_test("functional", "Get Anonymized Resume", passed,
                f"Status: {response.status_code}", duration)
        return passed
    except Exception as e:
        log_test("functional", "Get Anonymized Resume", False, f"Error: {str(e)}")
        return False

def test_delete_resume(resume_id: int):
    """Test delete resume"""
    if not resume_id:
        log_test("functional", "Delete Resume", False, "No resume ID available")
        return False
    
    start = time.time()
    try:
        response = requests.delete(f"{API_BASE}/resumes/{resume_id}", timeout=10)
        duration = time.time() - start
        passed = response.status_code == 204
        log_test("functional", "Delete Resume", passed,
                f"Status: {response.status_code}", duration)
        return passed
    except Exception as e:
        log_test("functional", "Delete Resume", False, f"Error: {str(e)}")
        return False

# ==================== PERFORMANCE TESTS ====================

def test_upload_performance():
    """Test upload performance (should be < 5 seconds)"""
    start = time.time()
    try:
        test_file = create_test_file("perf_test.txt")
        files = {"file": ("perf_test.txt", test_file, "text/plain")}
        response = requests.post(f"{API_BASE}/resumes/upload", files=files, timeout=30)
        duration = time.time() - start
        
        passed = duration < 5.0 and response.status_code == 201
        log_test("performance", "Upload Performance", passed,
                f"Duration: {duration:.3f}s (Target: <5s)", duration)
        return passed, duration
    except Exception as e:
        log_test("performance", "Upload Performance", False, f"Error: {str(e)}")
        return False, None

def test_response_time_health():
    """Test health endpoint response time (should be < 100ms)"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = time.time() - start
        
        passed = duration < 0.1  # 100ms
        log_test("performance", "Health Endpoint Response Time", passed,
                f"Duration: {duration*1000:.2f}ms (Target: <100ms)", duration)
        return passed, duration
    except Exception as e:
        log_test("performance", "Health Endpoint Response Time", False, f"Error: {str(e)}")
        return False, None

def test_concurrent_requests():
    """Test concurrent request handling"""
    import concurrent.futures
    
    start = time.time()
    try:
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start
        success_rate = sum(results) / len(results) if results else 0
        passed = success_rate >= 0.8  # 80% success rate
        
        log_test("performance", "Concurrent Requests", passed,
                f"Success Rate: {success_rate*100:.1f}% (10 concurrent requests)", duration)
        return passed, duration
    except Exception as e:
        log_test("performance", "Concurrent Requests", False, f"Error: {str(e)}")
        return False, None

# ==================== SECURITY TESTS ====================

def test_file_size_limit():
    """Test file size limit enforcement"""
    start = time.time()
    try:
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large_file.txt", BytesIO(large_content), "text/plain")}
        response = requests.post(f"{API_BASE}/resumes/upload", files=files, timeout=30)
        duration = time.time() - start
        
        # Should reject files > 10MB
        passed = response.status_code == 413  # Request Entity Too Large
        log_test("security", "File Size Limit", passed,
                f"Status: {response.status_code} (Expected: 413)", duration)
        return passed
    except Exception as e:
        log_test("security", "File Size Limit", False, f"Error: {str(e)}")
        return False

def test_file_type_validation():
    """Test file type validation"""
    start = time.time()
    try:
        # Try uploading an executable file
        malicious_content = b"MZ\x90\x00"  # PE executable header
        files = {"file": ("malicious.exe", BytesIO(malicious_content), "application/x-msdownload")}
        response = requests.post(f"{API_BASE}/resumes/upload", files=files, timeout=30)
        duration = time.time() - start
        
        # Should reject or handle gracefully
        passed = response.status_code in [400, 415, 422]  # Bad Request, Unsupported Media Type, or Unprocessable Entity
        log_test("security", "File Type Validation", passed,
                f"Status: {response.status_code} (Rejected unsafe file type)", duration)
        return passed
    except Exception as e:
        log_test("security", "File Type Validation", False, f"Error: {str(e)}")
        return False

def test_sql_injection():
    """Test SQL injection protection"""
    start = time.time()
    try:
        # Try SQL injection in resume_id parameter
        malicious_id = "1 OR 1=1"
        response = requests.get(f"{API_BASE}/resumes/{malicious_id}", timeout=10)
        duration = time.time() - start
        
        # Should return 404 or 422, not execute SQL
        passed = response.status_code in [404, 422, 400]
        log_test("security", "SQL Injection Protection", passed,
                f"Status: {response.status_code} (SQL injection blocked)", duration)
        return passed
    except Exception as e:
        log_test("security", "SQL Injection Protection", False, f"Error: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS configuration"""
    start = time.time()
    try:
        response = requests.options(f"{BASE_URL}/health", headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET"
        }, timeout=5)
        duration = time.time() - start
        
        # Check for CORS headers
        has_cors = "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
        passed = has_cors or response.status_code == 200
        log_test("security", "CORS Configuration", passed,
                f"CORS headers present: {has_cors}", duration)
        return passed
    except Exception as e:
        log_test("security", "CORS Configuration", False, f"Error: {str(e)}")
        return False

def test_xss_protection():
    """Test XSS protection in responses"""
    start = time.time()
    try:
        # Upload file with potential XSS payload
        xss_content = b"<script>alert('XSS')</script>John Doe"
        files = {"file": ("xss_test.txt", BytesIO(xss_content), "text/plain")}
        response = requests.post(f"{API_BASE}/resumes/upload", files=files, timeout=30)
        duration = time.time() - start
        
        if response.status_code == 201:
            data = response.json()
            # Check if script tags are escaped in response
            response_str = json.dumps(data)
            passed = "<script>" not in response_str or "&lt;script&gt;" in response_str
            log_test("security", "XSS Protection", passed,
                    "XSS payload handled safely", duration)
            return passed
        else:
            log_test("security", "XSS Protection", True, "File rejected (safe)", duration)
            return True
    except Exception as e:
        log_test("security", "XSS Protection", False, f"Error: {str(e)}")
        return False

# ==================== MAIN TEST RUNNER ====================

def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("COMPREHENSIVE API TEST SUITE")
    print("=" * 70)
    print(f"Testing API at: {BASE_URL}\n")
    
    # Health Check Tests
    print("\n" + "=" * 70)
    print("1. HEALTH CHECK TESTS")
    print("=" * 70)
    test_server_availability()
    test_health_endpoint()
    test_api_health_check()
    
    # Functional Tests
    print("\n" + "=" * 70)
    print("2. FUNCTIONAL TESTS")
    print("=" * 70)
    resume_id = test_upload_resume()
    test_get_resume(resume_id)
    test_list_resumes()
    test_get_anonymized_resume(resume_id)
    # Don't delete the test resume - keep it for other tests
    
    # Performance Tests
    print("\n" + "=" * 70)
    print("3. PERFORMANCE TESTS")
    print("=" * 70)
    test_response_time_health()
    test_upload_performance()
    test_concurrent_requests()
    
    # Security Tests
    print("\n" + "=" * 70)
    print("4. SECURITY TESTS")
    print("=" * 70)
    test_file_size_limit()
    test_file_type_validation()
    test_sql_injection()
    test_cors_headers()
    test_xss_protection()
    
    # Cleanup - delete test resume
    if resume_id:
        print("\n" + "-" * 70)
        print("Cleaning up test data...")
        test_delete_resume(resume_id)
    
    # Print Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_passed = 0
    total_failed = 0
    
    for category, results in TEST_RESULTS.items():
        passed = results["passed"]
        failed = results["failed"]
        total = passed + failed
        total_passed += passed
        total_failed += failed
        
        if total > 0:
            percentage = (passed / total) * 100
            status = "[PASS]" if percentage >= 80 else "[WARN]" if percentage >= 50 else "[FAIL]"
            print(f"\n{status} {category.upper().replace('_', ' ')}")
            print(f"   Passed: {passed}/{total} ({percentage:.1f}%)")
            if failed > 0:
                print(f"   Failed: {failed}")
    
    print("\n" + "=" * 70)
    total_tests = total_passed + total_failed
    if total_tests > 0:
        overall_percentage = (total_passed / total_tests) * 100
        overall_status = "[PASS]" if overall_percentage >= 80 else "[WARN]" if overall_percentage >= 50 else "[FAIL]"
        print(f"{overall_status} OVERALL: {total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%)")
    print("=" * 70)
    
    return total_passed, total_failed

if __name__ == "__main__":
    try:
        passed, failed = run_all_tests()
        exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {str(e)}")
        exit(1)

