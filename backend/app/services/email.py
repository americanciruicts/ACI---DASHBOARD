"""
Email service for sending password reset and other emails
"""

import smtplib
import ssl
import email.mime.text
import email.mime.multipart
from typing import Optional
import os
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME or ""
        self.smtp_password = settings.SMTP_PASSWORD or ""
        self.from_email = settings.FROM_EMAIL or self.smtp_username
        
        # Alternative SMTP configurations to try
        self.smtp_configs = [
            # Primary configuration
            {
                "server": "smtp.americancircuits.com",
                "port": 587,
                "use_tls": True
            },
            # Alternative configurations
            {
                "server": "mail.americancircuits.com", 
                "port": 587,
                "use_tls": True
            },
            {
                "server": "americancircuits-com.mail.protection.outlook.com",
                "port": 587, 
                "use_tls": True
            },
            {
                "server": "smtp.americancircuits.com",
                "port": 25,
                "use_tls": False
            },
            {
                "server": "smtp.americancircuits.com",
                "port": 465,
                "use_tls": True
            }
        ]
        
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """Send password reset email to user"""
        try:
            # Create reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            # Email content
            subject = "ACI Dashboard - Password Reset Request"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2563eb;">ACI Dashboard</h1>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h2 style="color: #1e40af; margin-top: 0;">Password Reset Request</h2>
                            <p>Hello {user_name},</p>
                            <p>We received a request to reset your password for your ACI Dashboard account.</p>
                            <p>Click the button below to reset your password:</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_url}" 
                                   style="background: #2563eb; color: white; padding: 12px 24px; 
                                          text-decoration: none; border-radius: 6px; display: inline-block;
                                          font-weight: bold;">
                                    Reset Password
                                </a>
                            </div>
                            
                            <p><strong>Important:</strong></p>
                            <ul>
                                <li>This link will expire in 1 hour</li>
                                <li>If you didn't request this password reset, please ignore this email</li>
                                <li>For security reasons, this link can only be used once</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; color: #6b7280; font-size: 14px;">
                            <p>If the button doesn't work, copy and paste this link into your browser:</p>
                            <p style="word-break: break-all;">{reset_url}</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px;">
                            <p>This is an automated email from ACI Dashboard. Please do not reply to this email.</p>
                            <p>&copy; 2024 ACI Dashboard. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            ACI Dashboard - Password Reset Request
            
            Hello {user_name},
            
            We received a request to reset your password for your ACI Dashboard account.
            
            To reset your password, please visit the following link:
            {reset_url}
            
            Important:
            - This link will expire in 1 hour
            - If you didn't request this password reset, please ignore this email
            - For security reasons, this link can only be used once
            
            If the link doesn't work, copy and paste it into your browser.
            
            This is an automated email from ACI Dashboard. Please do not reply to this email.
            
            © 2024 ACI Dashboard. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False
    
    def send_password_changed_notification(self, to_email: str, user_name: str) -> bool:
        """Send notification when password is successfully changed"""
        try:
            subject = "ACI Dashboard - Password Changed Successfully"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2563eb;">ACI Dashboard</h1>
                        </div>
                        
                        <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #22c55e;">
                            <h2 style="color: #15803d; margin-top: 0;">Password Changed Successfully</h2>
                            <p>Hello {user_name},</p>
                            <p>Your password has been successfully changed for your ACI Dashboard account.</p>
                            <p>If you did not make this change, please contact your administrator immediately.</p>
                        </div>
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px;">
                            <p>This is an automated email from ACI Dashboard. Please do not reply to this email.</p>
                            <p>&copy; 2024 ACI Dashboard. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            ACI Dashboard - Password Changed Successfully
            
            Hello {user_name},
            
            Your password has been successfully changed for your ACI Dashboard account.
            
            If you did not make this change, please contact your administrator immediately.
            
            This is an automated email from ACI Dashboard. Please do not reply to this email.
            
            © 2024 ACI Dashboard. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            print(f"Error sending password changed notification: {e}")
            return False
    
    def send_new_user_credentials(self, to_email: str, user_name: str, username: str, temporary_password: str, assigned_roles: list = None, assigned_tools: list = None) -> bool:
        """Send credentials to new user created by admin"""
        try:
            login_url = f"{settings.FRONTEND_URL}/login"
            
            subject = "ACI Dashboard - Your Account Has Been Created"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2563eb;">ACI Dashboard</h1>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h2 style="color: #1e40af; margin-top: 0;">Welcome to ACI Dashboard!</h2>
                            <p>Hello {user_name},</p>
                            <p>An administrator has created an account for you on ACI Dashboard.</p>
                            
                            <div style="background: #e0f2fe; padding: 15px; border-radius: 6px; margin: 20px 0;">
                                <h3 style="color: #0277bd; margin-top: 0;">Your Login Credentials:</h3>
                                <p><strong>Username:</strong> {username}</p>
                                <p><strong>Temporary Password:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 3px;">{temporary_password}</code></p>
                            </div>
                            
                            {self._generate_roles_section(assigned_roles)}
                            {self._generate_tools_section(assigned_tools)}
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" 
                                   style="background: #2563eb; color: white; padding: 12px 24px; 
                                          text-decoration: none; border-radius: 6px; display: inline-block;
                                          font-weight: bold;">
                                    Login to ACI Dashboard
                                </a>
                            </div>
                            
                            <p><strong>Important Security Notes:</strong></p>
                            <ul>
                                <li>Please change your password after your first login</li>
                                <li>Keep your credentials secure and do not share them</li>
                                <li>Use a strong, unique password for your account</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; color: #6b7280; font-size: 14px;">
                            <p>If the button doesn't work, copy and paste this link into your browser:</p>
                            <p style="word-break: break-all;">{login_url}</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px;">
                            <p>This is an automated email from ACI Dashboard. Please do not reply to this email.</p>
                            <p>&copy; 2024 ACI Dashboard. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            ACI Dashboard - Your Account Has Been Created
            
            Hello {user_name},
            
            An administrator has created an account for you on ACI Dashboard.
            
            Your Login Credentials:
            Username: {username}
            Temporary Password: {temporary_password}
            
            Please login at: {login_url}
            
            Important Security Notes:
            - Please change your password after your first login
            - Keep your credentials secure and do not share them
            - Use a strong, unique password for your account
            
            This is an automated email from ACI Dashboard. Please do not reply to this email.
            
            © 2024 ACI Dashboard. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            print(f"Error sending new user credentials: {e}")
            return False
    
    def _generate_roles_section(self, assigned_roles: list) -> str:
        """Generate HTML section for assigned roles"""
        if not assigned_roles:
            return ""
        
        roles_html = """
        <div style="background: #f0fdf4; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #22c55e;">
            <h3 style="color: #15803d; margin-top: 0;">🛡️ Your Assigned Roles:</h3>
        """
        
        for role in assigned_roles:
            role_name = role.get('name', '').replace('_', ' ').title()
            if role_name.lower() == 'super user':
                role_name = 'SUPER USER'
            else:
                role_name = role_name.upper()
            
            roles_html += f"""
            <div style="background: #dcfce7; padding: 8px 12px; border-radius: 4px; margin: 5px 0; display: inline-block;">
                <strong>{role_name}</strong>
            </div>
            """
        
        roles_html += "</div>"
        return roles_html
    
    def _generate_tools_section(self, assigned_tools: list) -> str:
        """Generate HTML section for assigned tools"""
        if not assigned_tools:
            return ""
        
        tools_html = """
        <div style="background: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #f59e0b;">
            <h3 style="color: #92400e; margin-top: 0;">🔧 Your Available Tools:</h3>
        """
        
        for tool in assigned_tools:
            tools_html += f"""
            <div style="background: #fef9c3; padding: 8px 12px; border-radius: 4px; margin: 5px 0;">
                <strong>{tool.get('display_name', tool.get('name', 'Unknown Tool'))}</strong>
                <br><small style="color: #78716c;">{tool.get('description', '')}</small>
            </div>
            """
        
        tools_html += "</div>"
        return tools_html
    
    def send_profile_creation_notification(self, to_email: str, user_name: str, admin_name: str) -> bool:
        """Send notification when profile creation begins"""
        try:
            subject = "🔄 ACI Dashboard - Your Account Is Being Created"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2563eb;">ACI Dashboard</h1>
                        </div>
                        
                        <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3b82f6;">
                            <h2 style="color: #1e40af; margin-top: 0;">🔄 Account Creation In Progress</h2>
                            <p>Hello {user_name},</p>
                            <p><strong>{admin_name}</strong> is currently creating your ACI Dashboard account.</p>
                            
                            <div style="background: #dbeafe; padding: 15px; border-radius: 6px; margin: 20px 0;">
                                <p style="margin: 0;"><strong>📧 What happens next:</strong></p>
                                <ul style="margin: 10px 0;">
                                    <li>Your account is being set up with appropriate roles and tools</li>
                                    <li>You will receive another email with your login credentials shortly</li>
                                    <li>Once complete, you'll have access to the ACI Dashboard</li>
                                </ul>
                            </div>
                            
                            <p style="color: #1e40af;"><strong>📍 Please wait for the completion email with your login details.</strong></p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px;">
                            <p>This is an automated notification from ACI Dashboard. Please do not reply to this email.</p>
                            <p>&copy; 2024 ACI Dashboard. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            ACI Dashboard - Your Account Is Being Created
            
            Hello {user_name},
            
            {admin_name} is currently creating your ACI Dashboard account.
            
            What happens next:
            - Your account is being set up with appropriate roles and tools
            - You will receive another email with your login credentials shortly
            - Once complete, you'll have access to the ACI Dashboard
            
            Please wait for the completion email with your login details.
            
            This is an automated notification from ACI Dashboard. Please do not reply to this email.
            
            © 2024 ACI Dashboard. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            print(f"Error sending profile creation notification: {e}")
            return False
    
    def send_existing_user_credentials(self, to_email: str, user_name: str, username: str, assigned_roles: list = None, assigned_tools: list = None) -> bool:
        """Send login information to existing user"""
        try:
            login_url = f"{settings.FRONTEND_URL}/login"
            
            subject = "🔑 ACI Dashboard - Your Account Information"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #2563eb;">ACI Dashboard</h1>
                        </div>
                        
                        <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #22c55e;">
                            <h2 style="color: #15803d; margin-top: 0;">🔑 Your Account Information</h2>
                            <p>Hello {user_name},</p>
                            <p>Here's your current ACI Dashboard account information and access details.</p>
                            
                            <div style="background: #dcfce7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                                <h3 style="color: #15803d; margin-top: 0;">Your Login Information:</h3>
                                <p><strong>Username:</strong> {username}</p>
                                <p><strong>Password:</strong> Your current password (if you forgot it, contact your administrator for a reset)</p>
                                <p><strong>Login URL:</strong> <a href="{login_url}">{login_url}</a></p>
                            </div>
                            
                            {self._generate_roles_section(assigned_roles)}
                            {self._generate_tools_section(assigned_tools)}
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{login_url}" 
                                   style="background: #15803d; color: white; padding: 12px 24px; 
                                          text-decoration: none; border-radius: 6px; display: inline-block;
                                          font-weight: bold;">
                                    Access ACI Dashboard
                                </a>
                            </div>
                            
                            <p><strong>Need Help?</strong></p>
                            <ul>
                                <li>If you forgot your password, use the "Forgot Password" link on the login page</li>
                                <li>Contact your administrator if you need access to additional tools or roles</li>
                                <li>Keep your login credentials secure and don't share them</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; color: #6b7280; font-size: 14px;">
                            <p>If the button doesn't work, copy and paste this link into your browser:</p>
                            <p style="word-break: break-all;">{login_url}</p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                        
                        <div style="text-align: center; color: #6b7280; font-size: 12px;">
                            <p>This is an automated email from ACI Dashboard. Please do not reply to this email.</p>
                            <p>&copy; 2024 ACI Dashboard. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            ACI Dashboard - Your Account Information
            
            Hello {user_name},
            
            Here's your current ACI Dashboard account information and access details.
            
            Your Login Information:
            Username: {username}
            Password: Your current password (if you forgot it, contact your administrator for a reset)
            Login URL: {login_url}
            
            Your Assigned Roles:
            {', '.join([role.get('name', '').upper().replace('_', ' ') for role in (assigned_roles or [])]) if assigned_roles else 'No roles assigned'}
            
            Your Available Tools:
            {', '.join([tool.get('display_name', tool.get('name', '')) for tool in (assigned_tools or [])]) if assigned_tools else 'No tools assigned'}
            
            Need Help?
            - If you forgot your password, use the "Forgot Password" link on the login page
            - Contact your administrator if you need access to additional tools or roles
            - Keep your login credentials secure and don't share them
            
            Access your dashboard at: {login_url}
            
            This is an automated email from ACI Dashboard. Please do not reply to this email.
            
            © 2024 ACI Dashboard. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            print(f"Error sending existing user credentials: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Internal method to send email"""
        try:
            # Check if SMTP is configured
            if not self.smtp_username or not self.smtp_password:
                print("="*80)
                print(f"📧 EMAIL SIMULATION MODE - Email to: {to_email}")
                print(f"📧 Subject: {subject}")
                print(f"📧 Content preview: {text_body[:300]}...")
                print("📧 Configure SMTP_USERNAME and SMTP_PASSWORD to send actual emails")
                print("="*80)
                return True
            
            print("="*80)
            print(f"📧 SENDING REAL EMAIL to: {to_email}")
            print(f"📧 Subject: {subject}")
            print(f"📧 SMTP Server: {self.smtp_server}:{self.smtp_port}")
            print(f"📧 From: {self.from_email}")
            print("="*80)
            
            # Create message
            message = email.mime.multipart.MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Create the plain-text and HTML version of your message
            part1 = email.mime.text.MIMEText(text_body, "plain")
            part2 = email.mime.text.MIMEText(html_body, "html")
            
            # Add HTML/plain-text parts to MimeMultipart message
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection with server and send email
            context = ssl.create_default_context()
            # Allow unverified certificates for corporate mail servers
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Try multiple SMTP configurations
            for i, config in enumerate(self.smtp_configs):
                try:
                    print(f"📧 Trying SMTP config {i+1}: {config['server']}:{config['port']} (TLS: {config['use_tls']})")
                    
                    if config['port'] == 465:
                        # Use SMTP_SSL for port 465
                        with smtplib.SMTP_SSL(config['server'], config['port'], context=context) as server:
                            print(f"📧 Connected via SSL. Authenticating...")
                            server.login(self.smtp_username, self.smtp_password)
                            print(f"📧 Sending email from {self.from_email} to {to_email}...")
                            server.sendmail(self.from_email, to_email, message.as_string())
                    else:
                        # Use regular SMTP
                        with smtplib.SMTP(config['server'], config['port']) as server:
                            if config['use_tls']:
                                print(f"📧 Starting TLS encryption...")
                                server.starttls(context=context)
                            print(f"📧 Authenticating with username: {self.smtp_username}")
                            server.login(self.smtp_username, self.smtp_password)
                            print(f"📧 Sending email from {self.from_email} to {to_email}...")
                            server.sendmail(self.from_email, to_email, message.as_string())
                    
                    print("="*80)
                    print(f"✅ EMAIL SENT SUCCESSFULLY to {to_email}")
                    print(f"✅ Using SMTP: {config['server']}:{config['port']}")
                    print("="*80)
                    return True
                    
                except Exception as config_error:
                    print(f"❌ Config {i+1} failed: {config_error}")
                    continue
            
            # If all configurations failed
            print("❌ All SMTP configurations failed!")
            return False
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService()