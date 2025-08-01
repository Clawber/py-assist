import json
import base64
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and return Gmail service object"""
    creds = None
    
    # Load existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to download credentials.json from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, body, sender_email):
    """Create email message"""
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message['from'] = sender_email
    
    message.attach(MIMEText(body, 'plain'))
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def parse_datetime(datetime_str):
    """Parse datetime string to timestamp"""
    try:
        # Try parsing format: "2025-08-15 14:30"
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        # Convert to UTC timestamp in milliseconds
        return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
    except ValueError:
        try:
            # Try parsing format: "2025-08-15 14:30:00"
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {datetime_str}. Use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'")

def schedule_email(service, email_data, sender_email):
    """Schedule an email using Gmail API"""
    try:
        # Create the email message
        message = create_message(
            email_data['to'], 
            email_data['subject'], 
            email_data['body'],
            sender_email
        )
        
        # Parse the scheduled send time
        scheduled_time = parse_datetime(email_data['send_time'])
        
        # Add scheduling information
        message['scheduleTime'] = scheduled_time
        
        # Send the scheduled message
        result = service.users().messages().send(
            userId='me', 
            body=message
        ).execute()
        
        print(f"✅ Email scheduled successfully!")
        print(f"   To: {email_data['to']}")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Scheduled for: {email_data['send_time']}")
        print(f"   Message ID: {result['id']}")
        return result
        
    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None
    except Exception as error:
        print(f"❌ Error: {error}")
        return None

def load_emails_from_file(filename):
    """Load email data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Handle both single email and multiple emails
        if isinstance(data, dict):
            return [data]  # Single email
        elif isinstance(data, list):
            return data    # Multiple emails
        else:
            raise ValueError("JSON file must contain either a single email object or an array of email objects")
            
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def main():
    """Main function to schedule emails"""
    print("🚀 Gmail Scheduled Email Sender")
    print("=" * 40)
    
    # Get email file path
    email_file = input("Enter the path to your email JSON file (default: 'emails.json'): ").strip()
    if not email_file:
        email_file = 'emails.json'
    
    # Load emails from file
    emails = load_emails_from_file(email_file)
    
    if not emails:
        print("No emails to process. Exiting.")
        return
    
    try:
        # Authenticate Gmail
        print("\n🔐 Authenticating with Gmail...")
        service = authenticate_gmail()
        
        # Get sender email (your Gmail address) - alternative method
        try:
            profile = service.users().getProfile(userId='me').execute()
            sender_email = profile['emailAddress']
        except:
            # Fallback: ask user for their email address
            sender_email = input("Enter your Gmail address: ").strip()
        
        print(f"✅ Authenticated as: {sender_email}")
        
        # Schedule each email
        print(f"\n📧 Processing {len(emails)} email(s)...")
        successful = 0
        
        for i, email_data in enumerate(emails, 1):
            print(f"\n--- Email {i}/{len(emails)} ---")
            
            # Validate required fields
            required_fields = ['to', 'subject', 'body', 'send_time']
            missing_fields = [field for field in required_fields if field not in email_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
                continue
            
            # Schedule the email
            result = schedule_email(service, email_data, sender_email)
            if result:
                successful += 1
        
        print(f"\n✅ Successfully scheduled {successful} out of {len(emails)} emails!")
        
    except Exception as error:
        print(f"❌ Fatal error: {error}")

if __name__ == '__main__':
    main()