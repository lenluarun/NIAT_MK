import os
import requests

def send_attendance_email(student_name, student_email, time_marked):
    if not student_email:
        print(f"Skipping email for {student_name}: No email address provided.")
        return False
        
    try:
        subject = f"Attendance Confirmed - {student_name}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'DM Sans', Arial, sans-serif;
                    background-color: #F0F2F8;
                    color: #0A0E1A;
                    margin: 0;
                    padding: 40px 20px;
                }}
                .container {{
                    max-width: 560px;
                    margin: 0 auto;
                    background-color: #FFFFFF;
                    border-radius: 18px;
                    overflow: hidden;
                    box-shadow: 0 8px 24px rgba(10, 14, 26, 0.08);
                    border: 1px solid rgba(100, 116, 180, 0.14);
                }}
                .header {{
                    background: linear-gradient(135deg, #4F46E5, #818CF8);
                    padding: 32px 24px;
                    text-align: center;
                    color: white;
                }}
                .header-title {{
                    font-family: 'Syne', sans-serif;
                    font-size: 24px;
                    font-weight: 800;
                    margin: 0;
                    letter-spacing: -0.5px;
                }}
                .header-subtitle {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 8px;
                }}
                .content {{
                    padding: 32px 32px;
                }}
                .greeting {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 24px;
                }}
                .status-card {{
                    background-color: #ECFDF5;
                    border: 1px solid #6EE7B7;
                    border-radius: 12px;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    margin-bottom: 24px;
                }}
                .status-icon {{
                    background-color: #10B981;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin-right: 16px;
                }}
                .status-text h4 {{
                    margin: 0 0 4px 0;
                    color: #059669;
                    font-family: 'Syne', sans-serif;
                    font-size: 16px;
                }}
                .status-text p {{
                    margin: 0;
                    font-size: 14px;
                    color: #047857;
                }}
                .details-grid {{
                    background-color: #F8FAFC;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 24px;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 12px;
                    font-size: 14px;
                }}
                .detail-row:last-child {{
                    margin-bottom: 0;
                }}
                .detail-label {{
                    color: #6B7280;
                    font-weight: 500;
                }}
                .detail-value {{
                    font-weight: 600;
                    color: #0A0E1A;
                }}
                .footer {{
                    text-align: center;
                    padding: 24px;
                    font-size: 12px;
                    color: #9CA3AF;
                    border-top: 1px solid rgba(100, 116, 180, 0.14);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="header-title">E2C Authentication</h1>
                    <div class="header-subtitle">Smart Face & Biometric Attendance System</div>
                </div>
                <div class="content">
                    <div class="greeting">Hello {student_name},</div>
                    <p style="color: #475569; font-size: 15px; line-height: 1.6; margin-top: 0;">This email is to confirm that your attendance has been successfully recorded in our system.</p>
                    
                    <div class="status-card">
                        <div class="status-icon">✓</div>
                        <div class="status-text">
                            <h4>Attendance Verified</h4>
                            <p>You have been marked as present.</p>
                        </div>
                    </div>
                    
                    <div class="details-grid">
                        <div class="detail-row">
                            <span class="detail-label">Name</span>
                            <span class="detail-value">{student_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Status</span>
                            <span class="detail-value" style="color: #10B981;">Present</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Timestamp</span>
                            <span class="detail-value">{time_marked}</span>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    This is an automated message generated by the E2C Smart Attendance System.<br>
                    Please do not reply to this email.
                </div>
            </div>
        </body>
        </html>
        """

        url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # We send all variables securely to EmailJS.
        # It's now capable of sending directly to the student's email, completely bypassing the Resend sandbox!
        payload = {
            "service_id": "service_8i4q55c",
            "template_id": "template_7behmnn",
            "user_id": "zPGy3NhwATeqVIuDU",
            "accessToken": "vXBGhvnyLv2Xq_1Gv976b",
            "template_params": {
                "to_email": student_email,
                "student_name": student_name,
                "time_marked": time_marked,
                "subject": subject,
                "html_content": html_content
            }
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Attendance email sent successfully to {student_email} via EmailJS.")
            return True
        else:
            print(f"Failed to send email via EmailJS: {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send email to {student_email}: {str(e)}")
        return False

def send_absent_email(student_name, student_email, date_marked):
    if not student_email:
        print(f"Skipping absent email for {student_name}: No email address provided.")
        return False
        
    try:
        subject = f"Absence Notice - {student_name}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'DM Sans', Arial, sans-serif;
                    background-color: #F0F2F8;
                    color: #0A0E1A;
                    margin: 0;
                    padding: 40px 20px;
                }}
                .container {{
                    max-width: 560px;
                    margin: 0 auto;
                    background-color: #FFFFFF;
                    border-radius: 18px;
                    overflow: hidden;
                    box-shadow: 0 8px 24px rgba(10, 14, 26, 0.08);
                    border: 1px solid rgba(100, 116, 180, 0.14);
                }}
                .header {{
                    background: linear-gradient(135deg, #F43F5E, #FDA4AF);
                    padding: 32px 24px;
                    text-align: center;
                    color: white;
                }}
                .header-title {{
                    font-family: 'Syne', sans-serif;
                    font-size: 24px;
                    font-weight: 800;
                    margin: 0;
                    letter-spacing: -0.5px;
                }}
                .header-subtitle {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 8px;
                }}
                .content {{
                    padding: 32px 32px;
                }}
                .greeting {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 24px;
                }}
                .status-card {{
                    background-color: #FFF1F2;
                    border: 1px solid #FDA4AF;
                    border-radius: 12px;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    margin-bottom: 24px;
                }}
                .status-icon {{
                    background-color: #E11D48;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin-right: 16px;
                }}
                .status-text h4 {{
                    margin: 0 0 4px 0;
                    color: #BE123C;
                    font-family: 'Syne', sans-serif;
                    font-size: 16px;
                }}
                .status-text p {{
                    margin: 0;
                    font-size: 14px;
                    color: #9F1239;
                }}
                .details-grid {{
                    background-color: #F8FAFC;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 24px;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 12px;
                    font-size: 14px;
                }}
                .detail-row:last-child {{
                    margin-bottom: 0;
                }}
                .detail-label {{
                    color: #6B7280;
                    font-weight: 500;
                }}
                .detail-value {{
                    font-weight: 600;
                    color: #0A0E1A;
                }}
                .footer {{
                    text-align: center;
                    padding: 24px;
                    font-size: 12px;
                    color: #9CA3AF;
                    border-top: 1px solid rgba(100, 116, 180, 0.14);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="header-title">E2C Authentication</h1>
                    <div class="header-subtitle">Smart Face & Biometric Attendance System</div>
                </div>
                <div class="content">
                    <div class="greeting">Hello {student_name},</div>
                    <p style="color: #475569; font-size: 15px; line-height: 1.6; margin-top: 0;">This email is to notify you that your attendance was not recorded during the recent session.</p>
                    
                    <div class="status-card">
                        <div class="status-icon">!</div>
                        <div class="status-text">
                            <h4>Absence Recorded</h4>
                            <p>You have been marked as absent.</p>
                        </div>
                    </div>
                    
                    <div class="details-grid">
                        <div class="detail-row">
                            <span class="detail-label">Name</span>
                            <span class="detail-value">{student_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Status</span>
                            <span class="detail-value" style="color: #E11D48;">Absent</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date</span>
                            <span class="detail-value">{date_marked}</span>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    This is an automated message generated by the E2C Smart Attendance System.<br>
                    Please do not reply to this email.
                </div>
            </div>
        </body>
        </html>
        """

        url = "https://api.emailjs.com/api/v1.0/email/send"
        
        payload = {
            "service_id": "service_8i4q55c",
            "template_id": "template_7behmnn",
            "user_id": "zPGy3NhwATeqVIuDU",
            "accessToken": "vXBGhvnyLv2Xq_1Gv976b",
            "template_params": {
                "to_email": student_email,
                "student_name": student_name,
                "time_marked": date_marked,
                "subject": subject,
                "html_content": html_content
            }
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"Absent email sent successfully to {student_email} via EmailJS.")
            return True
        else:
            print(f"Failed to send absent email via EmailJS: {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send absent email to {student_email}: {str(e)}")
        return False