import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Environment, BaseLoader
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    def _get_smtp_connection(self):
        """Get SMTP connection with enhanced Microsoft support"""
        try:
            # Create connection with explicit timeout
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            
            # Enable debug mode for troubleshooting
            server.set_debuglevel(1)
            
            # Say hello to server
            server.ehlo()
            
            # Start TLS encryption
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()  # Re-identify after STARTTLS
            
            # Authenticate
            server.login(self.smtp_username, self.smtp_password)
            
            # Disable debug mode after successful connection
            server.set_debuglevel(0)
            
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise
    
    def _create_welcome_email_html(self, user_name: str, username: str, password: str, login_url: str) -> str:
        """Create HTML email content for welcome email"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to ACI Dashboard</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin-bottom: 10px;">Welcome to ACI Dashboard</h1>
                    <p style="color: #6b7280; font-size: 16px;">Your account has been created successfully</p>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <h2 style="color: #1f2937; margin-top: 0;">Hello {{ user_name }}!</h2>
                    <p style="color: #4b5563; margin-bottom: 15px;">
                        Your account has been created for the ACI Dashboard system. You can now access all the tools and features assigned to your role.
                    </p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; border-left: 4px solid #2563eb; margin-bottom: 10px;">
                        <p style="margin: 0 0 8px 0; color: #1f2937;"><strong>Username:</strong> {{ username }}</p>
                        <p style="margin: 0; color: #1f2937;"><strong>Temporary Password:</strong> <code style="background-color: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{{ password }}</code></p>
                    </div>
                    
                    <div style="background-color: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b; margin-top: 15px;">
                        <p style="margin: 0 0 8px 0; color: #92400e; font-weight: bold;">🔐 Important Security Notice:</p>
                        <p style="margin: 0; color: #92400e; font-size: 14px;">
                            This is a temporary password. <strong>You must change your password</strong> after your first login for security reasons.
                        </p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <a href="{{ login_url }}" 
                       style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">
                        Access Dashboard
                    </a>
                </div>
                
                <div style="text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p>This is an automated message from ACI Dashboard.</p>
                    <p>If you have any questions, please contact your system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        env = Environment(loader=BaseLoader())
        template = env.from_string(html_template)
        return template.render(
            user_name=user_name,
            username=username,
            password=password,
            login_url=login_url
        )
    
    def _create_credentials_email_html(self, user_name: str, username: str, password: str, login_url: str) -> str:
        """Create HTML email content for credentials email"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ACI Dashboard - Account Access Information</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin-bottom: 10px;">ACI Dashboard</h1>
                    <p style="color: #6b7280; font-size: 16px;">Account Access Information</p>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <h2 style="color: #1f2937; margin-top: 0;">Hello {{ user_name }}!</h2>
                    <p style="color: #4b5563; margin-bottom: 15px;">
                        Here are your login credentials for accessing the ACI Dashboard system:
                    </p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; border-left: 4px solid #10b981; margin-bottom: 15px;">
                        <p style="margin: 0 0 8px 0; color: #1f2937;"><strong>Username:</strong> {{ username }}</p>
                        <p style="margin: 0; color: #1f2937;"><strong>Password:</strong> <code style="background-color: #f3f4f6; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{{ password }}</code></p>
                    </div>
                    
                    <div style="background-color: #fee2e2; padding: 15px; border-radius: 6px; border-left: 4px solid #dc2626; margin-bottom: 15px;">
                        <p style="margin: 0 0 8px 0; color: #991b1b; font-weight: bold;">🔒 Security Requirement:</p>
                        <p style="margin: 0; color: #991b1b; font-size: 14px;">
                            <strong>You MUST change your password immediately</strong> after your first login. This is mandatory for account security.
                        </p>
                    </div>
                    
                    <div style="background-color: #e0f2fe; padding: 15px; border-radius: 6px; border-left: 4px solid #0277bd;">
                        <p style="margin: 0 0 8px 0; color: #01579b; font-weight: bold;">📋 Login Instructions:</p>
                        <ol style="margin: 8px 0 0 20px; padding: 0; color: #01579b; font-size: 14px;">
                            <li>Click the login button below</li>
                            <li>Enter your username and password</li>
                            <li>You will be prompted to change your password</li>
                            <li>Choose a strong, secure new password</li>
                        </ol>
                    </div>
                </div>
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <a href="{{ login_url }}" 
                       style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">
                        Login to Dashboard
                    </a>
                </div>
                
                <div style="text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p>This is an automated message from ACI Dashboard.</p>
                    <p>If you have any questions, please contact your system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        env = Environment(loader=BaseLoader())
        template = env.from_string(html_template)
        return template.render(
            user_name=user_name,
            username=username,
            password=password,
            login_url=login_url
        )
    
    def send_welcome_email(self, to_email: str, user_name: str, username: str, password: str) -> bool:
        """Send welcome email to new user"""
        try:
            login_url = f"{self.frontend_url}/login"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Welcome to ACI Dashboard'
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create HTML content
            html_content = self._create_welcome_email_html(user_name, username, password, login_url)
            html_part = MIMEText(html_content, 'html')
            
            # Create plain text version
            text_content = f"""
Welcome to ACI Dashboard!

Hello {user_name},

Your account has been created successfully for the ACI Dashboard system.

Username: {username}
Temporary Password: {password}

IMPORTANT: You must change your password after your first login for security reasons.

You can access the dashboard at: {login_url}

If you have any questions, please contact your system administrator.

This is an automated message from ACI Dashboard.
            """
            text_part = MIMEText(text_content, 'plain')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Welcome email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {e}")
            return False
    
    def send_credentials_email(self, to_email: str, user_name: str, username: str, password: str) -> bool:
        """Send credentials email to user"""
        try:
            login_url = f"{self.frontend_url}/login"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'ACI Dashboard - Your Account Access Information'
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create HTML content
            html_content = self._create_credentials_email_html(user_name, username, password, login_url)
            html_part = MIMEText(html_content, 'html')
            
            # Create plain text version
            text_content = f"""
ACI Dashboard - Account Access Information

Hello {user_name},

Here are your login credentials for accessing the ACI Dashboard system:

Username: {username}
Password: {password}

SECURITY REQUIREMENT: You MUST change your password immediately after your first login. This is mandatory for account security.

You can access the dashboard at: {login_url}

Security Note: If you haven't received your password or need to reset it, please contact your system administrator.

This is an automated message from ACI Dashboard.
            """
            text_part = MIMEText(text_content, 'plain')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Credentials email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send credentials email to {to_email}: {e}")
            return False
    
    def send_bulk_credentials_emails(self, users: List[dict]) -> dict:
        """Send credentials emails to multiple users"""
        results = {
            "total_users": len(users),
            "successful_sends": 0,
            "failed_sends": 0,
            "failed_emails": []
        }
        
        for user in users:
            success = self.send_credentials_email(
                user['email'], 
                user['full_name'], 
                user['username'],
                user['password']
            )
            
            if success:
                results["successful_sends"] += 1
            else:
                results["failed_sends"] += 1
                results["failed_emails"].append(user['email'])
        
        return results

# Global email service instance
email_service = EmailService()