# curl http://localhost:8000/

# ==============================test with form data==========================

# curl -X POST " http://localhost:8000/submit-form" \

# -F "name=John Doe" \

# -F "email=john@example.com" \

# -F "subject=Test Subject" \

# -F "message=This is a test message from curl"

#==================================test with json data===========================
# curl -X POST " http://localhost:8000/submit-form-json" \

# -H "Content-Type: application/json" \

# -d '{

# "name": "Jane Smith",

# "email": "jane@example.com",

# "subject": "JSON Test",

# "message": "This is a test message using JSON format"

# }'

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

app = FastAPI(title="Form to Email API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email configuration - set these as environment variables
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT =587
EMAIL_USER = "toneystirk@gmail.com"
EMAIL_PASSWORD = "uijdtfrzbolzwhws"
RECIPIENT_EMAIL = "toneystirk@gmail.com"



class FormData(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


def send_email(form_data: FormData) -> bool:
    """Send email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Contact Form: {form_data.subject}"
        
        # Email body
        body = f"""
        New contact form submission:
        
        Name: {form_data.name}
        Email: {form_data.email}
        Subject: {form_data.subject}
        
        Message:
        {form_data.message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@app.get("/")
async def root():
    return {"message": "Form to Email API is running"}


@app.post("/submit-form")
async def submit_form(
    name: str = Form(...),
    email: EmailStr = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    """
    Endpoint to receive form data and send email
    """
    form_data = FormData(
        name=name,
        email=email,
        subject=subject,
        message=message
    )
    
    # Send email
    success = send_email(form_data)
    
    if success:
        return {
            "status": "success",
            "message": "Form submitted successfully! Email sent."
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Please try again later."
        )


@app.post("/submit-form-json")
async def submit_form_json(form_data: FormData):
    """
    Alternative endpoint that accepts JSON data
    """
    success = send_email(form_data)
    
    if success:
        return {
            "status": "success",
            "message": "Form submitted successfully! Email sent."
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Please try again later."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)