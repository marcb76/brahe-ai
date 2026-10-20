#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
brahe-ai: AI Agent based on Gemini
Main Orchestrator
"""

import os
import shutil
import sys
import pandas as pd
from datetime import datetime




###############################################################
# General variables
AGENT_NAME = "brahe-ai"
AGENT_VERSION = "0.0.1"
AGENT_DESCRIPTION = "AI Agent based on Gemini for meta-information insights based on raw data."
configuration_service = None  # This will hold the instance of the ConfigService once it's instantiated
google_service = None         # This will hold the instance of the GoogleService once it's instantiated
notification_service = None   # This will hold the instance of the NotificationService once it's instantiated
gemini_service = None         # This will hold the instance of the GeminiService once it's instantiated
agent_service = None          # This will hold the instance of the AgentService once it's instantiated








###############################################################
# Load and set environment variables (.env)
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv is not installed. Install it with: pip install python-dotenv")
    print("")
    print("")
    print("")
    sys.exit(1)
load_dotenv()








###############################################################
# Import services
try:
    from services.configuration_service import ConfigurationService
except ImportError as e:
    print(f"❌ Unable to import service configuration_service from services: {e}")
    print("PANIC: Configuration Service is required for loading and validating the agent's configuration. We could not even report this issue via email. Please check the services/configuration_service.py file and ensure it exists and is correctly implemented.")
    print("")
    print("")
    print("")
    sys.exit(1)
try:
    from services.google_service import GoogleService
except ImportError as e:
    print(f"❌ Unable to import service google_service from services: {e}")
    print("PANIC: Google Service is required for error notification via email. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
    print("")
    print("")
    print("")
    sys.exit(1)
try:
    from services.notification_service import NotificationService
except ImportError as e:
    print(f"❌ Unable to import service notification_service from services: {e}")
    print("PANIC: Notification Service is required for error notification via email. Please check the services/notification_service.py file and ensure it exists and is correctly implemented.")
    print("")
    print("")
    print("")
    sys.exit(1)
try:
    from services.gemini_service import GeminiService
except ImportError as e:
    print(f"❌ Unable to import service gemini_service from services: {e}")
    print("PANIC: Gemini Service is required for the core functionality of this agent. Please check the services/gemini_service.py file and ensure it exists and is correctly implemented.")
    print("")
    print("")
    print("")
    sys.exit(1)
try:
    from services.agent_service import AgentService
except ImportError as e:
    print(f"❌ Unable to import service agent_service from services: {e}")
    print("PANIC: Agent Service is required for the core functionality of this agent. Please check the services/agent_service.py file and ensure it exists and is correctly implemented.")
    print("")
    print("")
    print("")
    sys.exit(1)








###############################################################
# Main function
def main():
    print("")
    print("")
    print("")
    print("-------------------------------------------------------------------")
    print(f"-- {AGENT_NAME}-{AGENT_VERSION}: AI Agent based on Gemini")
    print(f"-- {AGENT_DESCRIPTION}")
    print("-- 🪐 Tycho Brahe would be proud! 🪐")
    print("-- https://en.wikipedia.org/wiki/Tycho_Brahe")
    print("--")
    print("--")
    print("--")
    print("--")
    print("-- Marc Bonet")
    print(f"-- Version {AGENT_VERSION}")
    print("-- Designed for Python and Google/Gemini APIs")
    print("-- May 2026")
    print("-------------------------------------------------------------------")
    print("")
    print("")
    print("")
    print("")
    print("-------------------------------------------------------------------")
    print("Instantiating basic services...")
    print("  ConfigurationService...")
    try:
        global configuration_service
        configuration_service = ConfigurationService()
    except Exception as e:
        print(f"    ❌ Error instanciating ConfigurationService: {e}")
        print("    PANIC: Configuration Service is required for loading and validating the agent's configuration. We could not even report this issue via email. Please check the services/configuration_service.py file and ensure it exists and is correctly implemented.")
        print("    Exiting with error code 1 due to ConfigurationService initialization failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print("✅ Basic services instanciated successfully!")
    print("  Validating configuration...")
    missing_configuration = configuration_service.validate_configuration()
    if missing_configuration:
        print("    ❌ Error: Missed values in configuration: " + ", ".join(missing_configuration))
        print("    Please set the missing configuration(s) in the .env file and try again.")
        print("    PANIC: Missing configuration values are required for the agent to run properly. We could not even report this issue via email. Please check the services/configuration_service.py file and ensure it exists and is correctly implemented.")
        print("    Exiting with error code 1 due to missing configuration.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print("  Configuration validated successfully!")
    print("  🤖 Agent initialized with the following configuration: ")
    print(f"    📂 Log folder:                         {configuration_service.LOG_FOLDER}")
    print(f"    📂 Temp folder:                        {configuration_service.TEMP_FOLDER}")
    print(f"    📂 Processing folder:                  {configuration_service.PROCESSING_FOLDER}")
    print(f"    📂 Processed folder:                   {configuration_service.PROCESSED_FOLDER}")
    print(f"    🔑 Google Credentials file:            {'*********' if configuration_service.GOOGLE_CREDENTIALS_FILE else 'Not Set'}")
    print(f"    🔑 Google Token file:                  {'*********' if configuration_service.GOOGLE_TOKEN_FILE else 'Not Set'}")
    print(f"    📂 Google Drive Rules folder ID:       {configuration_service.GOOGLE_DRIVE_RULES_FOLDER_ID}")
    print(f"    📂 Google Drive Input folder ID:       {configuration_service.GOOGLE_DRIVE_INPUT_FOLDER_ID}")
    print(f"    📂 Google Drive Output folder ID:      {configuration_service.GOOGLE_DRIVE_OUTPUT_FOLDER_ID}")
    print(f"    🤖 Gemini Model:                       {configuration_service.GEMINI_MODEL}")
    print(f"    🔑 Gemini API Key:                     {'*********' if configuration_service.GEMINI_API_KEY else 'Not Set'}")
    print(f"    📂 General Rules file name:            {configuration_service.GENERAL_RULES_FILE_NAME}")
    print(f"    📂 Department Rules file name pattern: {configuration_service.DEPARTMENT_RULES_FILE_NAME_PATTERN}")
    print(f"    📂 Raw Data Report input file name:    {configuration_service.RAW_DATA_REPORT_INPUT_FILE_NAME}")
    print(f"    📂 Processing file name pattern:       {configuration_service.PROCESSING_FILE_NAME_PATTERN}")
    print(f"    📂 Processed file name pattern:        {configuration_service.PROCESSED_FILE_NAME_PATTERN}")
    print(f"    📂 Output file name pattern:           {configuration_service.OUTPUT_FILE_NAME_PATTERN}")
    print(f"    📧 On Error Notification Emails:       {configuration_service.ON_ERROR_NOTIFICATION_EMAILS}")
    print(f"    📧 On Success Notification Emails:     {configuration_service.ON_SUCCESS_NOTIFICATION_EMAILS}")
    print("-------------------------------------------------------------------")
    print("")
    print("")
    print("")
    print("")




    print("Instanciating additional services...")
    print("  GoogleService...")
    try:
        global google_service
        google_service = GoogleService(credentials_path=configuration_service.GOOGLE_CREDENTIALS_FILE, token_path=configuration_service.GOOGLE_TOKEN_FILE)
    except Exception as e:
        print(f"    ❌ Error instanciating GoogleService: {e}")
        print("    PANIC: Google Service is required for GoogleDrive integration and error notification via Gmail. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
        print("    Exiting with error code 1 due to GoogleService initialization failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print("  NotificationService...")
    try:
        global notification_service
        notification_service = NotificationService(google_service=google_service)
    except Exception as e:
        print(f"    ❌ Error instanciating NotificationService: {e}")
        print("    PANIC: Notification Service is required for error notification via email. We could not even report this issue via email. Please check the services/notification_service.py file and ensure it exists and is correctly implemented.")
        print("    Exiting with error code 1 due to NotificationService initialization failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print("  GeminiService...")
    try:
        global gemini_service
        gemini_service = GeminiService(gemini_model=configuration_service.GEMINI_MODEL, gemini_api_key=configuration_service.GEMINI_API_KEY, debugMode=configuration_service.GEMINI_DEBUG_MODE)
    except Exception as e:
        print(f"    ❌ Error instanciating GeminiService: {e}")
        notification_service.send_email(subject=f"{AGENT_NAME} Initialization Error", body=f"Unable to initialize GeminiService: {e}. Please check the services/gemini_service.py file and ensure it exists and is correctly implemented.", to_emails=configuration_service.ON_ERROR_NOTIFICATION_EMAILS)
        print("    Exiting with error code 1 due to GeminiService initialization failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print ("  AgentService...")
    try:
        global agent_service
        agent_service = AgentService(google_service=google_service, 
                                     gemini_service=gemini_service,
                                     configuration_service=configuration_service)
    except Exception as e:
        print(f"    ❌ Error instanciating AgentService: {e}")
        notification_service.send_email(subject=f"{AGENT_NAME} Initialization Error", body=f"Unable to initialize AgentService: {e}. Please check the services/agent_service.py file and ensure it exists and is correctly implemented.", to_emails=configuration_service.ON_ERROR_NOTIFICATION_EMAILS)
        print("    Exiting with error code 1 due to AgentService initialization failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    print("✅ Additional services instanciated successfully!")
    print("Ready to process data and generate insights with Gemini! 🪄✨")
    print("")
    print("")




    # Execute the agent
    print("-------------------------------------------------------------------")
    print(f"Executing {AGENT_NAME}-{AGENT_VERSION}...")
    agent_execution_start_dt = datetime.now()
    agent_execution_start = agent_execution_start_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"   Agent execution started at: {agent_execution_start}")
    try:
        # This is where the main logic of the agent is executed, including downloading files, processing with Gemini, and uploading results to Google Drive.
        agent_status = agent_service.execute(agent_execution_start_dt)
    except Exception as e:
        print(f"❌ Error during agent execution: {e}")
        notification_service.send_email(subject=f"{AGENT_NAME} Execution Error", body=f"An error occurred during agent execution: {e}. Please check the agent's log folder for details and investigate the issue.", to_emails=configuration_service.ON_ERROR_NOTIFICATION_EMAILS)
        print("Exiting with error code 1 due to execution failure.")
        print("")
        print("")
        print("")
        sys.exit(1)
    agent_execution_end_dt = datetime.now()
    agent_execution_end = agent_execution_end_dt.strftime("%Y-%m-%d %H:%M:%S")
    agent_execution_time = agent_execution_end_dt - agent_execution_start_dt
    total_seconds = int(agent_execution_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    agent_execution_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    print("✅ Agent execution completed successfully!")
    print(f"   Agent execution ended at:   {agent_execution_end}")
    print(f"   Total execution time:       {total_seconds} seconds or {agent_execution_time}")
    print("-------------------------------------------------------------------")
    print("")
    print("")
    print("Sending success notification email...")
    emailSubject = f"{AGENT_NAME} Execution Success"
    emailBody = f"The {AGENT_NAME} agent has completed its execution successfully!\n"
    emailBody+= f"  Agent execution started at:    {agent_execution_start}\n"
    emailBody+= f"  Agent execution ended at:      {agent_execution_end}\n"
    emailBody+= f"  Total execution time:          {total_seconds} seconds or {agent_execution_time}\n\n"
    emailBody+= f"  Google drive input folder ID:  {configuration_service.GOOGLE_DRIVE_RULES_FOLDER_ID}\n"
    emailBody+= f"  Input file name:               {configuration_service.RAW_DATA_REPORT_INPUT_FILE_NAME}\n"
    emailBody+= f"  Google drive output folder ID: {configuration_service.GOOGLE_DRIVE_OUTPUT_FOLDER_ID}\n"
    emailBody+= f"  Agent status:                  {agent_status['status']}\n"
    emailBody+= f"  Agent message:                 {agent_status['message']}\n"
    emailBody+= f"  Agent output files:            {agent_status['output_files']}\n\n\n\n"
    emailBody+= "Please check the agent's local log folder for details and the google drive output folder for results!\n"
    emailBody+= "Have a great day! 🪐"
    notification_service.send_email(subject=emailSubject, body=emailBody, to_emails=configuration_service.ON_SUCCESS_NOTIFICATION_EMAILS)
    print("✅ Success notification email sent!")
    print("")
    print("")
    print("")
    print("")
    print("-------------------------------------------------------------------")
    print(f"🪐 {AGENT_NAME} execution completed. Check the log folder for details and the output folder for results!")
    print("   Exiting normally. Error code: 0")
    print("")
    print("")
    print("")








###############################################################
# Entry point
if __name__ == "__main__":
    main()
    sys.exit(0)
