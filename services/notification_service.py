# services/notification_service.py
import sys




class NotificationService:
    def __init__(self, google_service=None, agent_name="brahe-ai"):
        self.google_service = google_service
        self.agent_name = agent_name




    def send_email(self, subject, body, to_emails, cc_emails=None, attachment_path=None):
        if not self.google_service:
            print("GoogleService is not initialized. Cannot send email.")
            print("PANIC: Google Service is required for error notification via email. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
            print("Attempted to send email with:")
            print(f"  To Emails: {to_emails}")
            print(f"  Subject: {subject}")
            print(f"  Body: {body}")
            if cc_emails:
                print(f"  CC Emails: {cc_emails}")
            if attachment_path:
                print(f"  Attachment Path: {attachment_path}")
            print("Exiting with error code 1 due to inability to send email notification.")
            sys.exit(1)
        try:
            self.google_service.send_email(to_emails=to_emails, subject=subject, body=body, cc_emails=cc_emails, attachment_path=attachment_path)
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            print("PANIC: Google Service is required for error notification via email. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
            print("Attempted to send email with:")
            print(f"  To Emails: {to_emails}")
            print(f"  Subject: {subject}")
            print(f"  Body: {body}")
            if cc_emails:
                print(f"  CC Emails: {cc_emails}")
            if attachment_path:
                print(f"  Attachment Path: {attachment_path}")
            print("Exiting with error code 1 due to inability to send email notification.")
            sys.exit(1)
