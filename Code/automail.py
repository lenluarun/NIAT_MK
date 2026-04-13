import yagmail
import os
from datetime import datetime


def print_header(title):
    """Print stylish header"""
    print("\n" + "═" * 55)
    print(f"  {title}")
    print("═" * 55)


def send_email():
    print_header("📧 EMAIL REPORT - Attendance Sender")
    
    try:
        sender_email = input("\n  ➤ Enter Your Email: ")
        sender_password = input("  ➤ Enter Your App Password: ")
        receiver_email = input("  ➤ Enter Receiver Email: ")
        
        print("\n  ⏳ Connecting to email server...")
        
        yag = yagmail.SMTP(sender_email, sender_password)
        
        filename = input("\n  ➤ Enter Attendance File Path (or press Enter for latest): ")
        
        if not filename:
            attendance_folder = "Attendance"
            files = [f for f in os.listdir(attendance_folder) if f.endswith('.csv')]
            if files:
                filename = os.path.join(attendance_folder, sorted(files)[-1])
            else:
                print("\n  ⚠ No attendance files found!")
                return
        
        print(f"\n  ✓ Sending from: {sender_email}")
        print(f"  ✓ Sending to: {receiver_email}")
        print("  ⏳ Sending email...")
        
        yag.send(
            to=receiver_email,
            subject="Attendance Report - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            contents="Please find the attendance report attached below.\n\nPowered by E2C TEAM",
            attachments=filename,
        )
        
        print("\n  ✓ Email sent successfully!")
        print("  ═ Powered by E2C TEAM ═\n")
        
    except Exception as e:
        print(f"\n  ⚠ Error occurred: {str(e)}")
        print("  ═ Powered by E2C TEAM ═\n")


if __name__ == "__main__":
    send_email()

