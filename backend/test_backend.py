"""
Comprehensive test script for ACI Dashboard backend
Tests all endpoints and functionality
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Test users
TEST_USERS = {
    "superuser": {"username": "tony967", "password": "AhFnrAASWN0a"},
    "manager": {"username": "max463", "password": "CCiYxAAxyR0z"},
    "user": {"username": "pratiksha649", "password": "hUDcvxtL26I9"},
    "operator": {"username": "cathy596", "password": "KOLCsB4kTzow"},
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test("Health Check", success, f"Status: {data.get('status', 'unknown')}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = self.session.get(BASE_URL)
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_test("Root Endpoint", success, f"Message: {data.get('message', '')}")
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, str(e))
            return False
    
    def test_login(self, user_type, credentials):
        """Test login endpoint"""
        try:
            response = self.session.post(
                f"{API_V1}/auth/login",
                json=credentials
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.tokens[user_type] = {
                    "access_token": data["access_token"],
                    "refresh_token": data["refresh_token"],
                    "user": data["user"]
                }
                message = f"User: {data['user']['full_name']}, Roles: {[r['name'] for r in data['user']['roles']]}"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_test(f"Login ({user_type})", success, message)
            return success
        except Exception as e:
            self.log_test(f"Login ({user_type})", False, str(e))
            return False
    
    def test_refresh_token(self, user_type):
        """Test refresh token endpoint"""
        if user_type not in self.tokens:
            self.log_test(f"Refresh Token ({user_type})", False, "No token available")
            return False
        
        try:
            response = self.session.post(
                f"{API_V1}/auth/refresh",
                json={"refresh_token": self.tokens[user_type]["refresh_token"]}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Update access token
                self.tokens[user_type]["access_token"] = data["access_token"]
                message = "New access token received"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_test(f"Refresh Token ({user_type})", success, message)
            return success
        except Exception as e:
            self.log_test(f"Refresh Token ({user_type})", False, str(e))
            return False
    
    def test_protected_endpoint(self, user_type, endpoint, expected_status=200):
        """Test protected endpoint with authentication"""
        if user_type not in self.tokens:
            self.log_test(f"Protected Endpoint ({endpoint})", False, f"No token for {user_type}")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[user_type]['access_token']}"}
            response = self.session.get(f"{API_V1}{endpoint}", headers=headers)
            success = response.status_code == expected_status
            
            message = f"Status: {response.status_code}"
            if success and response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        message += f", Items: {len(data)}"
                    elif isinstance(data, dict) and "message" in data:
                        message += f", Message: {data['message']}"
                except:
                    pass
            
            self.log_test(f"Protected Endpoint ({endpoint}) - {user_type}", success, message)
            return success
        except Exception as e:
            self.log_test(f"Protected Endpoint ({endpoint}) - {user_type}", False, str(e))
            return False
    
    def test_user_tools_access(self, user_type):
        """Test user tools access"""
        if user_type not in self.tokens:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[user_type]['access_token']}"}
            response = self.session.get(f"{API_V1}/users/me/tools", headers=headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                tools = data.get("tools", [])
                tool_names = [t["display_name"] for t in tools]
                message = f"Tools: {', '.join(tool_names) if tool_names else 'None'}"
            else:
                message = f"Status: {response.status_code}"
            
            self.log_test(f"User Tools Access ({user_type})", success, message)
            return success
        except Exception as e:
            self.log_test(f"User Tools Access ({user_type})", False, str(e))
            return False
    
    def test_tool_access(self, user_type, tool_name):
        """Test specific tool access"""
        if user_type not in self.tokens:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens[user_type]['access_token']}"}
            response = self.session.get(f"{API_V1}/tools/{tool_name}/access", headers=headers)
            
            # Different users should have different access levels
            expected_status = 200 if self.should_have_tool_access(user_type, tool_name) else 403
            success = response.status_code == expected_status
            
            message = f"Status: {response.status_code} (expected: {expected_status})"
            if response.status_code == 200:
                data = response.json()
                message += f", Message: {data.get('message', '')}"
            
            self.log_test(f"Tool Access ({tool_name}) - {user_type}", success, message)
            return success
        except Exception as e:
            self.log_test(f"Tool Access ({tool_name}) - {user_type}", False, str(e))
            return False
    
    def should_have_tool_access(self, user_type, tool_name):
        """Determine if user should have access to tool based on our seed data"""
        access_map = {
            "superuser": ["compare", "x-tool", "y-tool"],  # SuperUsers have all tools
            "manager": ["compare", "x-tool"],  # Max has compare and x-tool
            "user": ["compare"],  # Pratiksha has only compare tool
            "operator": ["compare"]  # Cathy has only compare tool
        }
        return tool_name in access_map.get(user_type, [])
    
    def test_admin_endpoints(self):
        """Test admin endpoints (superuser only)"""
        if "superuser" not in self.tokens:
            self.log_test("Admin Endpoints", False, "No superuser token")
            return False
        
        headers = {"Authorization": f"Bearer {self.tokens['superuser']['access_token']}"}
        
        admin_endpoints = [
            "/admin/users",
            "/admin/roles", 
            "/admin/tools"
        ]
        
        all_passed = True
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{API_V1}{endpoint}", headers=headers)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    message = f"Items: {len(data) if isinstance(data, list) else 'N/A'}"
                else:
                    message = f"Status: {response.status_code}"
                
                self.log_test(f"Admin Endpoint ({endpoint})", success, message)
                all_passed = all_passed and success
            except Exception as e:
                self.log_test(f"Admin Endpoint ({endpoint})", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_unauthorized_admin_access(self, user_type):
        """Test that non-superusers cannot access admin endpoints"""
        if user_type not in self.tokens or user_type == "superuser":
            return True
        
        headers = {"Authorization": f"Bearer {self.tokens[user_type]['access_token']}"}
        
        try:
            response = self.session.get(f"{API_V1}/admin/users", headers=headers)
            success = response.status_code == 403  # Should be forbidden
            
            message = f"Status: {response.status_code} (expected: 403)"
            self.log_test(f"Unauthorized Admin Access ({user_type})", success, message)
            return success
        except Exception as e:
            self.log_test(f"Unauthorized Admin Access ({user_type})", False, str(e))
            return False
    
    def run_comprehensive_tests(self):
        """Run all tests"""
        print("🧪 Starting comprehensive backend tests...")
        print("="*70)
        
        # Basic connectivity tests
        print("\n📡 CONNECTIVITY TESTS")
        print("-" * 30)
        self.test_health_check()
        self.test_root_endpoint()
        
        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        for user_type, credentials in TEST_USERS.items():
            self.test_login(user_type, credentials)
        
        # Refresh token tests
        print("\n🔄 REFRESH TOKEN TESTS")
        print("-" * 30)
        for user_type in TEST_USERS.keys():
            self.test_refresh_token(user_type)
        
        # User profile tests
        print("\n👤 USER PROFILE TESTS")
        print("-" * 30)
        for user_type in TEST_USERS.keys():
            self.test_protected_endpoint(user_type, "/users/me")
            self.test_user_tools_access(user_type)
        
        # Tool access tests
        print("\n🔧 TOOL ACCESS TESTS")
        print("-" * 30)
        tools = ["compare", "x-tool", "y-tool"]
        for user_type in TEST_USERS.keys():
            for tool in tools:
                self.test_tool_access(user_type, tool)
        
        # Admin tests
        print("\n👑 ADMIN ACCESS TESTS")
        print("-" * 30)
        self.test_admin_endpoints()
        
        # Unauthorized access tests
        print("\n🚫 UNAUTHORIZED ACCESS TESTS")
        print("-" * 30)
        for user_type in ["manager", "user", "operator"]:
            self.test_unauthorized_admin_access(user_type)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "="*70)
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Backend is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the issues above.")
        print("="*70)

def main():
    """Main test function"""
    print("🚀 ACI Dashboard Backend Test Suite")
    print("="*70)
    print("This script tests all backend functionality including:")
    print("• Health checks and connectivity")
    print("• Authentication and JWT tokens") 
    print("• Role-based access control")
    print("• Tool-based permissions")
    print("• Admin functionality")
    print("• Security boundaries")
    print("\nMake sure the backend is running on http://localhost:8000")
    
    input("\nPress Enter to start testing...")
    
    tester = BackendTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()