import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class EscalationEmailInput(BaseModel):
    customer_email: str = Field(..., description="The email address of the frustrated customer.")
    issue_summary: str = Field(..., description="A detailed summary of the customer's problem and why it is being escalated.")

class EscalationEmailTool(BaseTool):
    name: str = "EscalationEmailTool"
    description: str = "Use this tool to automatically send an escalation email to the human Admin, AND a confirmation email to the customer, when an issue cannot be resolved or the customer is extremely frustrated."
    args_schema: type[BaseModel] = EscalationEmailInput
    has_escalated: bool = Field(default=False, description="Internal flag to prevent duplicate emails.")

    def _run(self, customer_email: str, issue_summary: str) -> str:
        if self.has_escalated:
            return "Error: An escalation email has already been sent during this conversation. Do not use this tool again."
            
        sender_email = os.getenv("EMAIL_SENDER_ADDRESS")
        app_password = os.getenv("EMAIL_APP_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL_ADDRESS")

        if not sender_email or not app_password or not admin_email:
            return "Error: Email credentials are not fully configured in the environment variables."

        try:
            # Connect to Gmail SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)

            # 1. Send Email to Admin
            admin_msg = MIMEMultipart()
            admin_msg['From'] = sender_email
            admin_msg['To'] = admin_email
            admin_msg['Subject'] = "URGENT: Customer Escalation Required"
            
            admin_body = f"""Hello Admin,

An AI Support Agent has escalated a customer issue that requires human intervention.

Customer Email: {customer_email}

Issue Summary:
{issue_summary}

Please review and contact the customer as soon as possible.

- NovaCart AI System
"""
            admin_msg.attach(MIMEText(admin_body, 'plain'))
            server.send_message(admin_msg)

            # 2. Send Confirmation Email to Customer
            cust_msg = MIMEMultipart()
            cust_msg['From'] = sender_email
            cust_msg['To'] = customer_email
            cust_msg['Subject'] = "NovaCart Support: Your Escalation Request"
            
            cust_body = f"""Dear Customer,

This is an automated confirmation that your issue has been successfully escalated to our human support team.

We apologize for any inconvenience you have experienced. A human support specialist will review your case and contact you at this email address within 24 hours.

Thank you for your patience,
NovaCart Support Team
"""
            cust_msg.attach(MIMEText(cust_body, 'plain'))
            server.send_message(cust_msg)

            server.quit()
            self.has_escalated = True
            return f"Successfully escalated the issue to the Admin and sent a confirmation email to {customer_email}."

        except Exception as e:
            return f"Failed to send escalation emails. Error: {str(e)}"
