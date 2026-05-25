# services/configuration_service.py
import os
import sys




class ConfigurationService:
    def __init__(self):
        # Local Directories
        self.LOG_FOLDER = os.getenv("LOG_FOLDER", "log")
        self.TEMP_FOLDER = os.getenv("TEMP_FOLDER", "tmp")
        self.PROCESSING_FOLDER = os.getenv("PROCESSING_FOLDER", "processing")
        self.PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", "processed")

        # Google Configuration
        self.GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
        self.GOOGLE_DRIVE_RULES_FOLDER_ID = os.getenv("GOOGLE_DRIVE_RULES_FOLDER_ID")
        self.GOOGLE_DRIVE_INPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_INPUT_FOLDER_ID")
        self.GOOGLE_DRIVE_OUTPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_OUTPUT_FOLDER_ID")

        # Gemini Configuration
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GEMINI_DEBUG_MODE = os.getenv("GEMINI_DEBUG_MODE", "False").lower() in ("true", "1", "t", "yes", "y")

        # Input and Output Patterns
        self.GENERAL_RULES_FILE_NAME = os.getenv("GENERAL_RULES_FILE_NAME", "brahe-ai-general-rules.xlsx")
        self.DEPARTMENT_RULES_FILE_NAME_PATTERN = os.getenv("DEPARTMENT_RULES_FILE_NAME_PATTERN", "brahe-ai-department-{}-rules.xlsx")
        self.RAW_DATA_REPORT_INPUT_FILE_NAME = os.getenv("RAW_DATA_REPORT_INPUT_FILE_NAME", "data 2026 prueba 2.xlsx")
        self.PROCESSING_FILE_NAME_PATTERN = os.getenv("PROCESSING_FILE_NAME_PATTERN", "brahe-ai-processing-{}-{}.xlsx")
        self.PROCESSED_FILE_NAME_PATTERN = os.getenv("PROCESSED_FILE_NAME_PATTERN", "brahe-ai-processed-{}-{}.xlsx")
        self.OUTPUT_FILE_NAME_PATTERN = os.getenv("OUTPUT_FILE_NAME_PATTERN", "brahe-ai-output-{}-{}.xlsx")

        # Notifications
        self.ON_ERROR_NOTIFICATION_EMAILS = os.getenv("ON_ERROR_NOTIFICATION_EMAILS")
        self.ON_SUCCESS_NOTIFICATION_EMAILS = os.getenv("ON_SUCCESS_NOTIFICATION_EMAILS")




    def validate_configuration(self):
        missing_configs = []
        # Validate key attributes
        for key, value in self.__dict__.items():
            if not value:
                missing_configs.append(key)
        if missing_configs:
            return missing_configs
        return []
