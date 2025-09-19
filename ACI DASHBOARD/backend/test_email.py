#!/usr/bin/env python3
"""
Test script to send a credentials email to Kanav to verify email functionality
"""

import os
from email_service import email_service

def test_kanav_email():
    """Send a test credentials email to Kanav"""
    try:
        print("🧪 Testing email functionality...")
        print("📧 Sending credentials email to Kanav...")
        
        # Kanav's information from USER_CREDENTIALS.md
        email = "kanav@americancircuits.com"
        full_name = "Kanav"
        username = "kanav"
        password = "XCSkRBUbQKdY"
        
        # Send email
        success = email_service.send_credentials_email(
            email, 
            full_name, 
            username,
            password
        )
        
        if success:
            print("✅ SUCCESS: Email sent successfully to Kanav!")
            print(f"📬 Email sent to: {email}")
            print(f"👤 Username included: {username}")
            print(f"🔐 Password included: {password}")
            print("📋 Email includes password reset instructions for first login")
        else:
            print("❌ FAILED: Email could not be sent")
            
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    test_kanav_email()