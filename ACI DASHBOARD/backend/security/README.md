# ACI Dashboard Security

This directory contains security-related configurations and documentation for the ACI Dashboard application.

## Directory Structure

```
backend/security/
├── README.md                   # This file
├── .env.security              # Security environment template
└── security_policies/         # Security policy documents
```

## Security Configuration

### Environment Variables
Copy `.env.security` to `../.env` and modify the values for your environment:

```bash
cp .env.security ../.env
# Edit ../.env with your secure values
```

### Key Security Settings

**JWT Configuration**:
- `SECRET_KEY`: Strong secret key for JWT signing (32+ characters)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)

**Password Policy**:
- `PASSWORD_MIN_LENGTH`: Minimum password length (default: 12)
- `PASSWORD_REQUIRE_UPPERCASE`: Require uppercase letters
- `PASSWORD_REQUIRE_LOWERCASE`: Require lowercase letters
- `PASSWORD_REQUIRE_DIGIT`: Require digits
- `PASSWORD_REQUIRE_SPECIAL`: Require special characters

**Rate Limiting**:
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)

## Security Features Implemented

✅ OWASP Top 10 Protection
✅ SOC II Compliance
✅ Input Sanitization
✅ Rate Limiting
✅ Security Headers
✅ Audit Logging
✅ Container Security
✅ Password Security

## Security Testing

Run the security test suite from the backend directory:

```bash
cd backend
python tests/security/security_test.py --url http://localhost:8000
```

## Security Monitoring

Monitor security events in the application logs:
- Authentication attempts
- Rate limiting violations
- Input validation errors
- Authorization failures

## Compliance

This implementation meets:
- ACI Security Standards v1.0
- SOC II Type 1 & Type 2 requirements
- OWASP Top 10 (2021) protection
- NIST Cybersecurity Framework alignment

For detailed security documentation, see `../docs/security/SECURITY_IMPLEMENTATION.md`