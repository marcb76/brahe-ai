import os
import io
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload




# Required scopes for Google Drive and Gmail APIs
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]

class GoogleService:
    def __init__(self, credentials_path, token_path):
        """
        Initialize and authenticate Google services (Drive and Gmail).
        Parameters:
            - credentials_path: Path to the client secrets JSON file.
            - token_path: Path to the token JSON file.
        """
        self.creds = self._authenticate(credentials_path, token_path)
        self.drive_client = build('drive', 'v3', credentials=self.creds)
        self.gmail_client = build('gmail', 'v1', credentials=self.creds)




    def _authenticate(self, credentials_path, token_path):
        """
        Handles the standard Google OAuth2 token flow.
        Checks for existing token and its validity.
        If invalid or expired, initiates the OAuth flow to get a new token.
        Saves the new token for future use.
        Parameters:
            - credentials_path: Path to the client secrets JSON file.
            - token_path: Path to the token JSON file.
        Raises FileNotFoundError if credentials file is missing or empty, and HttpError for API issues.
        """

        creds = None
        if os.path.exists(token_path) and os.path.getsize(token_path) > 0:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path) or os.path.getsize(credentials_path) == 0:
                    raise FileNotFoundError(f"❌ The file '{credentials_path}' is empty or does not exist in the root directory. Please download your Desktop credentials from Google Cloud Console.")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds




    def download_file_by_name(self, folder_id: str, file_name: str, dest_folder: str) -> str:
        """
        Locate a file by name within a Drive folder and download it locally.
        Parameters:
            - folder_id: ID of the Drive folder to search within.
            - file_name: Name of the file to search for.
            - dest_folder: Local folder to save the downloaded file.
        Returns: Local path of the downloaded file.
        Raises: FileNotFoundError if the file is not found, RuntimeError for API issues.
        """
        try:
            # Query to search for the file by name, not in trash, and belonging to the parent folder
            query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
            results = self.drive_client.files().list(
                q=query, 
                spaces='drive', 
                fields='files(id, name)'
            ).execute()
            items = results.get('files', [])
            if not items:
                raise FileNotFoundError(f"⚠️ File '{file_name}' not found in the specified Drive folder '{folder_id}'.")

            # Binary download flow for the first matching file (assuming unique names within the folder)                
            file_id = items[0]['id']
            file_name = items[0]['name']
            local_path = os.path.join(dest_folder, file_name)
            request = self.drive_client.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            os.makedirs(dest_folder, exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            return local_path

        except HttpError as error:
            raise HttpError(f"❌ Google Drive API error while downloading '{file_name}': {error}")




    def upload_file(self, source_file: str, folder_id: str, file_name: str):
        """
        Upload a local file to a specified Drive folder with a given name.
        Parameters:
            - source_file: Local path of the file to upload.
            - folder_id: ID of the Drive folder to upload to.
            - file_name: Desired name of the file in Drive after upload.
        Returns: The uploaded file's metadata from Drive (including its ID and name).
        Raises: FileNotFoundError if the source file is missing, RuntimeError for API issues.
        """
        try:
            if not os.path.exists(source_file):
                raise FileNotFoundError(f"❌ The file '{source_file}' does not exist. Please check the path and try again.")
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            media = MediaIoBaseDownload(io.BytesIO(open(source_file, 'rb').read()), mimetype='application/octet-stream')
            uploaded_file = self.drive_client.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
            return uploaded_file
        except HttpError as error:
            raise RuntimeError(f"❌ Google Drive API error while uploading '{file_name}': {error}")
    
    
    
    
    def delete_file_by_name(self, folder_id: str, file_name: str):
        """
        Locate a file by name within a Drive folder and delete it.
        Parameters:
            - folder_id: ID of the Drive folder to search within.
            - file_name: Name of the file to search for and delete.
        Raises: FileNotFoundError if the file is not found, HttpError for API issues
        """
        try:
            # Query to search for the file by name, not in trash, and belonging to the parent folder
            query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
            results = self.drive_client.files().list(
                q=query, 
                spaces='drive', 
                fields='files(id, name)'
            ).execute()
            items = results.get('files', [])
            if not items:
                raise FileNotFoundError(f"⚠️ File '{file_name}' not found in the specified Drive folder '{folder_id}' for deletion.")
            
            # Delete the first matching file (assuming unique names within the folder)
            file_id = items[0]['id']
            self.drive_client.files().delete(fileId=file_id).execute()
        except HttpError as error:
            raise RuntimeError(f"❌ Google Drive API error while deleting '{file_name}': {error}")




    def send_email(self, to_emails: str, subject: str, body: str, cc_emails: str = None, attachment_path: str = None):
        """
        Send an email using the Gmail API, supporting multiple recipients, CC, and attachments.
        Parameters:
            - to_emails: Comma-separated string of recipient email addresses.
            - subject: Subject of the email.
            - body: Body content of the email.
            - cc_emails: Comma-separated string of CC email addresses (optional).
            - attachment_path: Path to the file to attach (optional).
        Raises: HttpError for API issues.
        """
        try:
            message = EmailMessage()
            message.set_content(body)
            message['Subject'] = subject
            message['To'] = to_emails
            
            # Create a real distribution list for Google servers by splitting the comma-separated emails and stripping whitespace
            recipient_list = [email.strip() for email in to_emails.split(',')]
            if cc_emails:
                message['Cc'] = cc_emails
                recipient_list.extend([email.strip() for email in cc_emails.split(',')])

            # Attach file if path is provided and file exists
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(attachment_path)
                message.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            self.gmail_client.users().messages().send(userId="me", body=create_message).execute()
            
        except HttpError as error:
            raise HttpError(f"❌ Gmail API error: {error}")