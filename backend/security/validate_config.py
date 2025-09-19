#!/usr/bin/env python3
"""
ACI Dashboard Security Configuration Validator
Validates security settings against ACI Security Standards v1.0
"""

import os
import sys
import re
from typing import Dict, List, Any
from pathlib import Path

class SecurityConfigValidator:
    def __init__(self):
        self.validation_results = []
        self.warnings = []
        self.errors = []
    
    def log_result(self, check: str, status: str, message: str, severity: str = "INFO"):
        """Log validation result"""
        result = {
            "check": check,
            "status": status,  # PASS, FAIL, WARN
            "message": message,
            "severity": severity
        }
        self.validation_results.append(result)
        
        if status == "FAIL":
            self.errors.append(result)
        elif status == "WARN":
            self.warnings.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {check}: {message}")
    
    def validate_jwt_configuration(self, env_vars: Dict[str, str]):
        """Validate JWT security configuration"""
        print("\n🔐 Validating JWT Configuration...")
        
        # Secret Key validation
        secret_key = env_vars.get("SECRET_KEY", "")
        if not secret_key or secret_key == "your-secret-key-here":
            self.log_result("JWT Secret Key", "FAIL", 
                          "SECRET_KEY not set or using default value", "CRITICAL")
        elif len(secret_key) < 32:
            self.log_result("JWT Secret Key", "FAIL", 
                          f"SECRET_KEY too short ({len(secret_key)} chars, minimum 32)", "HIGH")
        else:
            self.log_result("JWT Secret Key", "PASS", 
                          f"SECRET_KEY properly configured ({len(secret_key)} chars)")
        
        # JWT specific keys
        jwt_secret = env_vars.get("JWT_SECRET_KEY", "")
        if not jwt_secret:
            self.log_result("JWT Secret", "WARN", 
                          "JWT_SECRET_KEY not set, using SECRET_KEY", "MEDIUM")
        elif len(jwt_secret) < 32:
            self.log_result("JWT Secret", "FAIL", 
                          f"JWT_SECRET_KEY too short ({len(jwt_secret)} chars)", "HIGH")
        else:
            self.log_result("JWT Secret", "PASS", 
                          f"JWT_SECRET_KEY properly configured")
        
        # Token expiration
        token_expire = env_vars.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        try:
            expire_minutes = int(token_expire)
            if expire_minutes > 60:
                self.log_result("Token Expiration", "WARN", 
                              f"Token expiration too long ({expire_minutes} min)", "MEDIUM")
            elif expire_minutes < 5:
                self.log_result("Token Expiration", "WARN", 
                              f"Token expiration too short ({expire_minutes} min)", "LOW")
            else:
                self.log_result("Token Expiration", "PASS", 
                              f"Token expiration configured ({expire_minutes} min)")
        except ValueError:
            self.log_result("Token Expiration", "FAIL", 
                          "Invalid ACCESS_TOKEN_EXPIRE_MINUTES value", "MEDIUM")
    
    def validate_password_policy(self, env_vars: Dict[str, str]):
        """Validate password policy configuration"""
        print("\n🔒 Validating Password Policy...")
        
        min_length = env_vars.get("PASSWORD_MIN_LENGTH", "12")
        try:
            length = int(min_length)
            if length < 8:
                self.log_result("Password Length", "FAIL", 
                              f"Minimum password length too short ({length})", "HIGH")
            elif length < 12:
                self.log_result("Password Length", "WARN", 
                              f"Password length below recommended ({length})", "MEDIUM")
            else:
                self.log_result("Password Length", "PASS", 
                              f"Password minimum length ({length} chars)")
        except ValueError:
            self.log_result("Password Length", "FAIL", 
                          "Invalid PASSWORD_MIN_LENGTH value", "MEDIUM")
        
        # Password complexity requirements
        requirements = {
            "PASSWORD_REQUIRE_UPPERCASE": "Uppercase letters",
            "PASSWORD_REQUIRE_LOWERCASE": "Lowercase letters", 
            "PASSWORD_REQUIRE_DIGIT": "Digits",
            "PASSWORD_REQUIRE_SPECIAL": "Special characters"
        }
        
        for env_var, description in requirements.items():
            value = env_vars.get(env_var, "true").lower()
            if value in ["true", "1", "yes"]:
                self.log_result(f"Password Policy - {description}", "PASS", 
                              f"{description} required")
            else:
                self.log_result(f"Password Policy - {description}", "WARN", 
                              f"{description} not required", "LOW")
    
    def validate_database_security(self, env_vars: Dict[str, str]):
        """Validate database security configuration"""
        print("\n🗃️ Validating Database Security...")
        
        db_url = env_vars.get("DATABASE_URL", "")
        if not db_url:
            self.log_result("Database URL", "FAIL", 
                          "DATABASE_URL not configured", "CRITICAL")
            return
        
        # Check for weak database passwords
        if "password" in db_url.lower() or "123" in db_url:
            self.log_result("Database Password", "FAIL", 
                          "Weak database password detected", "HIGH")
        elif "postgres:postgres" in db_url:
            self.log_result("Database Password", "FAIL", 
                          "Default postgres password detected", "HIGH")
        else:
            self.log_result("Database Password", "PASS", 
                          "Database password appears secure")
        
        # Check for SSL requirement
        if "sslmode=" not in db_url:
            self.log_result("Database SSL", "WARN", 
                          "SSL mode not specified in DATABASE_URL", "MEDIUM")
        elif "sslmode=require" in db_url or "sslmode=verify" in db_url:
            self.log_result("Database SSL", "PASS", 
                          "Database SSL properly configured")
        else:
            self.log_result("Database SSL", "WARN", 
                          "Database SSL not required", "MEDIUM")
    
    def validate_cors_configuration(self, env_vars: Dict[str, str]):
        """Validate CORS configuration"""
        print("\n🌐 Validating CORS Configuration...")
        
        allowed_origins = env_vars.get("ALLOWED_ORIGINS", "")
        if not allowed_origins:
            self.log_result("CORS Origins", "WARN", 
                          "No ALLOWED_ORIGINS specified", "MEDIUM")
            return
        
        origins = [origin.strip() for origin in allowed_origins.split(",")]
        
        # Check for wildcard origins
        if "*" in origins:
            self.log_result("CORS Wildcard", "FAIL", 
                          "Wildcard (*) in allowed origins", "HIGH")
        else:
            self.log_result("CORS Wildcard", "PASS", 
                          "No wildcard origins detected")
        
        # Check for insecure origins
        insecure_origins = [origin for origin in origins if origin.startswith("http://") 
                          and not origin.startswith("http://localhost") 
                          and not origin.startswith("http://127.0.0.1")]
        
        if insecure_origins:
            self.log_result("CORS HTTP Origins", "WARN", 
                          f"HTTP origins detected: {insecure_origins}", "MEDIUM")
        else:
            self.log_result("CORS HTTP Origins", "PASS", 
                          "All origins use HTTPS or localhost")
    
    def validate_rate_limiting(self, env_vars: Dict[str, str]):
        """Validate rate limiting configuration"""
        print("\n⏱️ Validating Rate Limiting...")
        
        rate_limit = env_vars.get("RATE_LIMIT_REQUESTS", "100")
        try:
            requests = int(rate_limit)
            if requests > 1000:
                self.log_result("Rate Limit", "WARN", 
                              f"Rate limit very high ({requests} req)", "LOW")
            elif requests < 10:
                self.log_result("Rate Limit", "WARN", 
                              f"Rate limit very low ({requests} req)", "LOW")
            else:
                self.log_result("Rate Limit", "PASS", 
                              f"Rate limit configured ({requests} requests)")
        except ValueError:
            self.log_result("Rate Limit", "FAIL", 
                          "Invalid RATE_LIMIT_REQUESTS value", "MEDIUM")
        
        window = env_vars.get("RATE_LIMIT_WINDOW", "60")
        try:
            seconds = int(window)
            if seconds < 1:
                self.log_result("Rate Limit Window", "FAIL", 
                              f"Rate limit window too short ({seconds}s)", "MEDIUM")
            else:
                self.log_result("Rate Limit Window", "PASS", 
                              f"Rate limit window ({seconds} seconds)")
        except ValueError:
            self.log_result("Rate Limit Window", "FAIL", 
                          "Invalid RATE_LIMIT_WINDOW value", "MEDIUM")
    
    def validate_environment_security(self, env_vars: Dict[str, str]):
        """Validate environment-specific security"""
        print("\n🏗️ Validating Environment Security...")
        
        environment = env_vars.get("ENVIRONMENT", "development")
        
        if environment == "production":
            self.log_result("Production Environment", "PASS", 
                          "Running in production mode")
            
            # Additional production checks
            if env_vars.get("DEBUG", "").lower() in ["true", "1"]:
                self.log_result("Debug Mode", "FAIL", 
                              "Debug mode enabled in production", "HIGH")
            else:
                self.log_result("Debug Mode", "PASS", 
                              "Debug mode disabled")
        else:
            self.log_result("Environment", "INFO", 
                          f"Running in {environment} mode")
    
    def validate_file_permissions(self):
        """Validate file permissions for security files"""
        print("\n📁 Validating File Permissions...")
        
        security_files = [
            ".env",
            "security/.env.security",
            "app/core/security.py",
            "app/core/security_middleware.py"
        ]
        
        for file_path in security_files:
            full_path = Path(file_path)
            if full_path.exists():
                # On Windows, file permission checks are different
                if os.name == 'nt':  # Windows
                    self.log_result(f"File Exists - {file_path}", "PASS", 
                                  "Security file exists")
                else:  # Unix-like systems
                    stat = full_path.stat()
                    permissions = oct(stat.st_mode)[-3:]
                    if permissions in ['600', '644', '640']:
                        self.log_result(f"File Permissions - {file_path}", "PASS", 
                                      f"Secure permissions ({permissions})")
                    else:
                        self.log_result(f"File Permissions - {file_path}", "WARN", 
                                      f"Permissions may be too open ({permissions})", "MEDIUM")
            else:
                self.log_result(f"File Missing - {file_path}", "WARN", 
                              f"Security file not found", "LOW")
    
    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        env_file = Path(".env")
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"\'')
        
        # Also include OS environment variables
        env_vars.update(os.environ)
        
        return env_vars
    
    def run_validation(self):
        """Run all security configuration validations"""
        print("🔍 ACI Dashboard Security Configuration Validator")
        print("=" * 55)
        
        # Load environment variables
        env_vars = self.load_env_vars()
        
        # Run all validation checks
        self.validate_jwt_configuration(env_vars)
        self.validate_password_policy(env_vars)
        self.validate_database_security(env_vars)
        self.validate_cors_configuration(env_vars)
        self.validate_rate_limiting(env_vars)
        self.validate_environment_security(env_vars)
        self.validate_file_permissions()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate validation summary"""
        print("\n" + "=" * 55)
        print("📊 SECURITY CONFIGURATION SUMMARY")
        print("=" * 55)
        
        total_checks = len(self.validation_results)
        passed = len([r for r in self.validation_results if r["status"] == "PASS"])
        warnings = len(self.warnings)
        errors = len(self.errors)
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed}")
        print(f"Warnings: {warnings}")
        print(f"Errors: {errors}")
        
        if errors > 0:
            print(f"\n❌ CRITICAL ISSUES ({errors}):")
            for error in self.errors:
                print(f"  - {error['check']}: {error['message']}")
        
        if warnings > 0:
            print(f"\n⚠️ WARNINGS ({warnings}):")
            for warning in self.warnings:
                print(f"  - {warning['check']}: {warning['message']}")
        
        if errors == 0 and warnings == 0:
            print("\n✅ All security configurations are properly set!")
        elif errors == 0:
            print(f"\n✅ No critical issues found. Please review {warnings} warnings.")
        else:
            print(f"\n❌ Please address {errors} critical security issues.")
        
        return errors == 0

def main():
    """Main function"""
    validator = SecurityConfigValidator()
    
    # Change to backend directory if not already there
    if not Path("app").exists() and Path("backend/app").exists():
        os.chdir("backend")
    
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()