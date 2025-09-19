"""
SQL Injection Prevention Forms and Utilities
Implements comprehensive protection against SQL injection attacks according to ACI Security Standards
"""

from typing import Any, Dict, List, Optional, Union
import re
import html
from sqlalchemy import text
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import Query, Session
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class SQLInjectionError(Exception):
    """Raised when potential SQL injection attempt is detected"""
    pass

class SecureSQLValidator:
    """Validates and sanitizes SQL inputs to prevent injection attacks"""
    
    # Dangerous SQL patterns that indicate injection attempts
    DANGEROUS_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
        r"(--|/\*|\*/|;|'|\"|\\)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
        r"(\bUNION\s+(ALL\s+)?SELECT\b)",
        r"(\bSELECT\s+.*\bFROM\s+)",
        r"(\bINSERT\s+INTO\s+)",
        r"(\bUPDATE\s+.*\bSET\s+)",
        r"(\bDELETE\s+FROM\s+)",
        r"(\bDROP\s+(TABLE|DATABASE|INDEX)\s+)",
        r"(\bCREATE\s+(TABLE|DATABASE|INDEX)\s+)",
        r"(\bALTER\s+(TABLE|DATABASE)\s+)",
        r"(\bEXEC\s*\()",
        r"(\bEXECUTE\s*\()",
        r"(\bSP_\w+)",
        r"(\bXP_\w+)",
        r"(\bSLEEP\s*\()",
        r"(\bWAITFOR\s+DELAY\s+)",
        r"(\bBENCHMARK\s*\()",
        r"(\bPG_SLEEP\s*\()",
        r"(\bINFORMATION_SCHEMA\b)",
        r"(\bSYS\.\w+)",
        r"(\bMASTER\.\w+)",
        r"(\bSYSCOLUMNS\b)",
        r"(\bSYSTABLES\b)",
        r"(\bLOAD_FILE\s*\()",
        r"(\bINTO\s+OUTFILE\s+)",
        r"(\bINTO\s+DUMPFILE\s+)",
    ]
    
    @staticmethod
    def validate_input(user_input: str, field_name: str = "input") -> str:
        """
        Validates user input for SQL injection patterns
        
        Args:
            user_input: The input string to validate
            field_name: Name of the field for logging purposes
            
        Returns:
            Sanitized input string
            
        Raises:
            SQLInjectionError: If potential injection attempt is detected
        """
        if not isinstance(user_input, str):
            return str(user_input)
        
        # Check for dangerous patterns
        for pattern in SecureSQLValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE | re.MULTILINE):
                logger.warning(f"Potential SQL injection attempt detected in {field_name}: {user_input[:100]}")
                raise SQLInjectionError(f"Invalid characters detected in {field_name}")
        
        # Additional sanitization
        sanitized = html.escape(user_input)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Log if significant sanitization occurred
        if sanitized != user_input:
            logger.info(f"Input sanitized for {field_name}")
        
        return sanitized
    
    @staticmethod
    def validate_identifier(identifier: str, field_name: str = "identifier") -> str:
        """
        Validates SQL identifiers (table names, column names, etc.)
        
        Args:
            identifier: The identifier to validate
            field_name: Name of the field for logging purposes
            
        Returns:
            Validated identifier
            
        Raises:
            SQLInjectionError: If identifier is invalid
        """
        if not identifier:
            raise SQLInjectionError(f"Empty {field_name} not allowed")
        
        # Only allow alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise SQLInjectionError(f"Invalid {field_name}: {identifier}")
        
        # Check against reserved words
        reserved_words = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'TABLE', 'DATABASE', 'INDEX', 'VIEW', 'TRIGGER', 'PROCEDURE',
            'FUNCTION', 'UNION', 'WHERE', 'ORDER', 'GROUP', 'HAVING', 'FROM'
        }
        
        if identifier.upper() in reserved_words:
            raise SQLInjectionError(f"Reserved word not allowed as {field_name}: {identifier}")
        
        return identifier

class SecureQueryBuilder:
    """Builds secure SQL queries using parameterized statements"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def safe_select(self, table: str, columns: List[str], where_conditions: Dict[str, Any] = None,
                   order_by: str = None, limit: int = None) -> Query:
        """
        Builds a safe SELECT query using parameterized statements
        
        Args:
            table: Table name (will be validated)
            columns: List of column names (will be validated)
            where_conditions: Dictionary of column:value conditions
            order_by: Column to order by (will be validated)
            limit: Maximum number of results
            
        Returns:
            SQLAlchemy Query object
        """
        # Validate table name
        table = SecureSQLValidator.validate_identifier(table, "table name")
        
        # Validate column names
        validated_columns = []
        for col in columns:
            validated_columns.append(SecureSQLValidator.validate_identifier(col, "column name"))
        
        # Build base query
        columns_str = ', '.join(validated_columns)
        query_str = f"SELECT {columns_str} FROM {table}"
        params = {}
        
        # Add WHERE conditions
        if where_conditions:
            where_parts = []
            for i, (column, value) in enumerate(where_conditions.items()):
                column = SecureSQLValidator.validate_identifier(column, "where column")
                param_name = f"param_{i}"
                where_parts.append(f"{column} = :{param_name}")
                params[param_name] = SecureSQLValidator.validate_input(str(value), f"where value for {column}")
            
            query_str += " WHERE " + " AND ".join(where_parts)
        
        # Add ORDER BY
        if order_by:
            order_by = SecureSQLValidator.validate_identifier(order_by, "order by column")
            query_str += f" ORDER BY {order_by}"
        
        # Add LIMIT
        if limit:
            if not isinstance(limit, int) or limit <= 0:
                raise SQLInjectionError("Invalid limit value")
            query_str += f" LIMIT {limit}"
        
        return self.session.execute(text(query_str), params)
    
    def safe_insert(self, table: str, data: Dict[str, Any]) -> Any:
        """
        Builds a safe INSERT query using parameterized statements
        
        Args:
            table: Table name (will be validated)
            data: Dictionary of column:value pairs
            
        Returns:
            Result of the insert operation
        """
        if not data:
            raise SQLInjectionError("No data provided for insert")
        
        # Validate table name
        table = SecureSQLValidator.validate_identifier(table, "table name")
        
        # Validate columns and prepare data
        validated_columns = []
        params = {}
        placeholders = []
        
        for i, (column, value) in enumerate(data.items()):
            column = SecureSQLValidator.validate_identifier(column, "column name")
            validated_columns.append(column)
            
            param_name = f"param_{i}"
            placeholders.append(f":{param_name}")
            params[param_name] = SecureSQLValidator.validate_input(str(value), f"insert value for {column}")
        
        # Build query
        columns_str = ', '.join(validated_columns)
        placeholders_str = ', '.join(placeholders)
        query_str = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})"
        
        return self.session.execute(text(query_str), params)
    
    def safe_update(self, table: str, data: Dict[str, Any], where_conditions: Dict[str, Any]) -> Any:
        """
        Builds a safe UPDATE query using parameterized statements
        
        Args:
            table: Table name (will be validated)
            data: Dictionary of column:value pairs to update
            where_conditions: Dictionary of column:value conditions
            
        Returns:
            Result of the update operation
        """
        if not data:
            raise SQLInjectionError("No data provided for update")
        if not where_conditions:
            raise SQLInjectionError("No where conditions provided for update")
        
        # Validate table name
        table = SecureSQLValidator.validate_identifier(table, "table name")
        
        params = {}
        set_parts = []
        
        # Build SET clause
        for i, (column, value) in enumerate(data.items()):
            column = SecureSQLValidator.validate_identifier(column, "column name")
            param_name = f"set_param_{i}"
            set_parts.append(f"{column} = :{param_name}")
            params[param_name] = SecureSQLValidator.validate_input(str(value), f"update value for {column}")
        
        # Build WHERE clause
        where_parts = []
        for i, (column, value) in enumerate(where_conditions.items()):
            column = SecureSQLValidator.validate_identifier(column, "where column")
            param_name = f"where_param_{i}"
            where_parts.append(f"{column} = :{param_name}")
            params[param_name] = SecureSQLValidator.validate_input(str(value), f"where value for {column}")
        
        # Build query
        set_str = ', '.join(set_parts)
        where_str = ' AND '.join(where_parts)
        query_str = f"UPDATE {table} SET {set_str} WHERE {where_str}"
        
        return self.session.execute(text(query_str), params)

class SecureSearchForm(BaseModel):
    """Secure form for search operations with SQL injection protection"""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    field: Optional[str] = Field(None, pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$', description="Field to search in")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum results")
    offset: Optional[int] = Field(0, ge=0, description="Results offset")
    
    @validator('query')
    def validate_query(cls, v):
        return SecureSQLValidator.validate_input(v, "search query")
    
    @validator('field')
    def validate_field(cls, v):
        if v is not None:
            return SecureSQLValidator.validate_identifier(v, "search field")
        return v

class SecureUserForm(BaseModel):
    """Secure form for user operations with SQL injection protection"""
    
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_.-]+$')
    full_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @validator('username')
    def validate_username(cls, v):
        return SecureSQLValidator.validate_input(v, "username")
    
    @validator('full_name')
    def validate_full_name(cls, v):
        return SecureSQLValidator.validate_input(v, "full name")
    
    @validator('email')
    def validate_email(cls, v):
        return SecureSQLValidator.validate_input(v, "email")

class SecurePasswordForm(BaseModel):
    """Secure form for password operations"""
    
    password: str = Field(..., min_length=12, max_length=128)
    confirm_password: Optional[str] = Field(None, min_length=12, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        # Check password strength
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        
        return SecureSQLValidator.validate_input(v, "password")
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if v is not None and 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class SecureFilterForm(BaseModel):
    """Secure form for filtering operations"""
    
    filter_field: str = Field(..., pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    filter_value: str = Field(..., min_length=1, max_length=100)
    filter_operator: str = Field('eq', pattern=r'^(eq|ne|lt|le|gt|ge|like|in)$')
    
    @validator('filter_field')
    def validate_filter_field(cls, v):
        return SecureSQLValidator.validate_identifier(v, "filter field")
    
    @validator('filter_value')
    def validate_filter_value(cls, v):
        return SecureSQLValidator.validate_input(v, "filter value")

# Decorator for secure database operations
def secure_db_operation(func):
    """Decorator that adds SQL injection protection to database operations"""
    def wrapper(*args, **kwargs):
        try:
            # Validate all string arguments
            validated_args = []
            for arg in args:
                if isinstance(arg, str):
                    validated_args.append(SecureSQLValidator.validate_input(arg))
                else:
                    validated_args.append(arg)
            
            # Validate string values in kwargs
            validated_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    validated_kwargs[key] = SecureSQLValidator.validate_input(value, key)
                else:
                    validated_kwargs[key] = value
            
            return func(*validated_args, **validated_kwargs)
        
        except SQLInjectionError:
            logger.error(f"SQL injection attempt blocked in {func.__name__}")
            raise
        except Exception as e:
            logger.error(f"Database operation error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

# Context manager for secure database sessions
class SecureDatabaseSession:
    """Context manager for secure database operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.query_builder = SecureQueryBuilder(session)
    
    def __enter__(self):
        return self.query_builder
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Database error: {exc_val}")
            self.session.rollback()
        else:
            self.session.commit()
        return False

# Utility functions for common secure operations
def sanitize_search_term(search_term: str) -> str:
    """Sanitizes search terms for safe use in database queries"""
    if not search_term:
        return ""
    
    # Remove SQL injection patterns
    search_term = SecureSQLValidator.validate_input(search_term, "search term")
    
    # Remove wildcards that could be used maliciously
    search_term = search_term.replace('%', '').replace('_', '')
    
    # Limit length
    if len(search_term) > 100:
        search_term = search_term[:100]
    
    return search_term

def build_safe_like_pattern(term: str) -> str:
    """Builds a safe LIKE pattern for database searches"""
    term = sanitize_search_term(term)
    # Escape special characters and wrap with wildcards
    term = term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return f"%{term}%"

def validate_sort_column(column: str, allowed_columns: List[str]) -> str:
    """Validates a sort column against a whitelist of allowed columns"""
    column = SecureSQLValidator.validate_identifier(column, "sort column")
    
    if column not in allowed_columns:
        raise SQLInjectionError(f"Sort column '{column}' not in allowed list")
    
    return column

def validate_sort_direction(direction: str) -> str:
    """Validates sort direction"""
    direction = direction.upper().strip()
    if direction not in ['ASC', 'DESC']:
        raise SQLInjectionError(f"Invalid sort direction: {direction}")
    return direction