#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
brahe-ai: AI Agent based on Gemini
Main Orchestrator
"""

import os
import shutil
import sys
#import pandas as pd
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv is not installed. Install it with: pip install python-dotenv")
    sys.exit(1)




###############################################################
# Load and set environment variables (.env)
load_dotenv()
# Local Directories Configuration
LOG_FOLDER = os.getenv("LOG_FOLDER", "log")
TEMP_FOLDER = os.getenv("TEMP_FOLDER", "tmp")
PROCESSING_FOLDER = os.getenv("PROCESSING_FOLDER", "processing")
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", "processed")

# Google Drive Configuration (IDs de las carpetas en tu Drive)
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
GOOGLE_DRIVE_RULES_FOLDER_ID = os.getenv("GOOGLE_DRIVE_RULES_FOLDER_ID")
GOOGLE_DRIVE_INPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_INPUT_FOLDER_ID")
GOOGLE_DRIVE_OUTPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_OUTPUT_FOLDER_ID")

# Gemini API Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Input file names
GENERAL_RULES_FILE_NAME = os.getenv("GENERAL_RULES_FILE_NAME", "brahe-ai-general-rules.xlsx")
DEPARTMENT_RULES_FILE_NAME_PATTERN = os.getenv("DEPARTMENT_RULES_FILE_NAME_PATTERN", "brahe-ai-department-{}-rules.xlsx")
RAW_DATA_REPORT_INPUT_FILE_NAME = os.getenv("RAW_DATA_REPORT_INPUT_FILE_NAME", "data 2026 prueba 2.xlsx")

# Processing and output folder/file name pattern
PROCESSING_FILE_NAME_PATTERN = os.getenv("PROCESSING_FILE_NAME_PATTERN", "brahe-ai-processing-{}-{}.xlsx")
PROCESSED_FILE_NAME_PATTERN = os.getenv("PROCESSED_FILE_NAME_PATTERN", "brahe-ai-processed-{}-{}.xlsx")
OUTPUT_FILE_NAME_PATTERN = os.getenv("OUTPUT_FILE_NAME_PATTERN", "brahe-ai-output-{}-{}.xlsx")

# Notifications configuration
ON_ERROR_NOTIFICATION_EMAILS = os.getenv("ON_ERROR_NOTIFICATION_EMAILS")      # Comma-separated list of emails to notify on errors
ON_SUCCESS_NOTIFICATION_EMAILS = os.getenv("ON_SUCCESS_NOTIFICATION_EMAILS")  # Comma-separated list of emails to notify on errors


###############################################################
# General variables
AGENT_NAME = "brahe-ai"
AGENT_VERSION = "0.0.1"
AGENT_DESCRIPTION = "AI Agent based on Gemini, focused on processing data from Excel files and generating insights based on that data."
TIMESTAMP_FORMAT = "%Y.%m.%d-%H-%M-%S"
WORK_AREA_PROCESSING_FILE_NAME_PATTERN = "brahe-ai-processing-{}.xlsx"  # {} will be replaced with timestamp
google_service = None  # This will hold the instance of the GoogleService once it's instantiated
agent_execution_start_dt = None  # This will be set to the datetime when the agent starts running
processing_file_name = None # This will be set to the actual processing file name with timestamp when the agent runs
processed_file_name = None # This will be set to the actual processed file name with timestamp when the agent runs
temporary_processing_path = None # This will be set to the actual temporary processing file path when the agent runs
output_file_path = None # This will be set to the actual output file path (Google Drive folder ID) when the agent runs
output_file_name = None # This will be set to the actual output file name with timestamp when the agent runs








###############################################################
# Import services (Google, Gemini)
try:
    from services.google_service import GoogleService
except ImportError as e:
    print(f"❌ Unable to import service google_service from services: {e}")
    print("PANIC: Google Service is required for error notification via email. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
    sys.exit(1)
try:
    from services.gemini_service import GeminiService
except ImportError as e:
    print(f"❌ Unable to import service gemini_service from services: {e}")
    print("PANIC: Gemini Service is required for the core functionality of this agent. Please check the services/gemini_service.py file and ensure it exists and is correctly implemented.")
    sys.exit(1)








###############################################################
# sendEmail
def send_email(subject, body, to_emails, cc_emails: str = None, attachment_path: str = None):
    if not google_service:
        print("❌ GoogleService is not initialized. Cannot send email.")
        print("PANIC: Google Service is required for error notification via email. We could not even report this issue via email. Please check the services/google_service.py file and ensure it exists and is correctly implemented.")
        print("Attempted to send email with:")
        print(f"  To Emails: {to_emails}")
        print(f"  Subject: {subject}")
        print(f"  Body: {body}")
        print("Exiting with error code 1 due to inability to send email notification.")
        sys.exit(1)
    try:
        google_service.send_email(to_emails=to_emails, subject=subject, body=body, cc_emails=cc_emails, attachment_path=attachment_path)
    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")
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








###############################################################
# validateConfiguration
def validate_configuration():
    missing_configs = []
    if not LOG_FOLDER:
        missing_configs.append("LOG_FOLDER")
    if not TEMP_FOLDER:
        missing_configs.append("TEMP_FOLDER")
    if not PROCESSING_FOLDER:
        missing_configs.append("PROCESSING_FOLDER")
    if not PROCESSED_FOLDER:
        missing_configs.append("PROCESSED_FOLDER")
    if not GOOGLE_CREDENTIALS_FILE:
        missing_configs.append("GOOGLE_CREDENTIALS_FILE")
    if not GOOGLE_TOKEN_FILE:
        missing_configs.append("GOOGLE_TOKEN_FILE")
    if not GOOGLE_DRIVE_RULES_FOLDER_ID:
        missing_configs.append("GOOGLE_DRIVE_RULES_FOLDER_ID")
    if not GOOGLE_DRIVE_INPUT_FOLDER_ID:
        missing_configs.append("GOOGLE_DRIVE_INPUT_FOLDER_ID")
    if not GOOGLE_DRIVE_OUTPUT_FOLDER_ID:
        missing_configs.append("GOOGLE_DRIVE_OUTPUT_FOLDER_ID")
    if not GEMINI_MODEL:
        missing_configs.append("GEMINI_MODEL")
    if not GEMINI_API_KEY:
        missing_configs.append("GEMINI_API_KEY")
    if not GENERAL_RULES_FILE_NAME:
        missing_configs.append("GENERAL_RULES_FILE_NAME")
    if not DEPARTMENT_RULES_FILE_NAME_PATTERN:
        missing_configs.append("DEPARTMENT_RULES_FILE_NAME_PATTERN")
    if not RAW_DATA_REPORT_INPUT_FILE_NAME:
        missing_configs.append("RAW_DATA_REPORT_INPUT_FILE_NAME")
    if not PROCESSING_FILE_NAME_PATTERN:
        missing_configs.append("PROCESSING_FILE_NAME_PATTERN")
    if not PROCESSED_FILE_NAME_PATTERN:
        missing_configs.append("PROCESSED_FILE_NAME_PATTERN")
    if not OUTPUT_FILE_NAME_PATTERN:
        missing_configs.append("OUTPUT_FILE_NAME_PATTERN")
    if not ON_ERROR_NOTIFICATION_EMAILS:
        missing_configs.append("ON_ERROR_NOTIFICATION_EMAILS")
    if not ON_SUCCESS_NOTIFICATION_EMAILS:
        missing_configs.append("ON_SUCCESS_NOTIFICATION_EMAILS")

    if missing_configs:
        print("  ❌ Missing configuration(s): " + ", ".join(missing_configs))
        print("  Please set the missing configuration(s) in the .env file and try again.")
        send_email(subject=f"{AGENT_NAME} Configuration Error", body=f"The following configuration(s) are missing: {', '.join(missing_configs)}. Please set them in the .env file and try again.", to_emails=ON_ERROR_NOTIFICATION_EMAILS)
        print("Exiting with error code 1 due to missing configuration.")
        sys.exit(1)








###############################################################
# executeAgent
def execute_agent():
    # Apply patterns to runtime generataed file names
    fileTimespan = agent_execution_start_dt.strftime(TIMESTAMP_FORMAT)
    global processing_file_name, temporary_path, processed_file_name, output_file_path, output_file_name
    processing_file_name = os.path.join(PROCESSING_FOLDER, PROCESSING_FILE_NAME_PATTERN.format(RAW_DATA_REPORT_INPUT_FILE_NAME, fileTimespan))
    temporary_path = os.path.join(TEMP_FOLDER, f"exec_{fileTimespan}")
    workarea_file_name = os.path.join(temporary_path, WORK_AREA_PROCESSING_FILE_NAME_PATTERN.format(fileTimespan))
    processed_file_name = os.path.join(PROCESSED_FOLDER, PROCESSED_FILE_NAME_PATTERN.format(RAW_DATA_REPORT_INPUT_FILE_NAME, fileTimespan))
    output_file_path = GOOGLE_DRIVE_OUTPUT_FOLDER_ID
    output_file_name = OUTPUT_FILE_NAME_PATTERN.format(RAW_DATA_REPORT_INPUT_FILE_NAME, fileTimespan)
    
    # Remove any .xlsx inner extension from the runtime generated filenames
    if processing_file_name.count(".xlsx") > 1:
        processing_file_name = processing_file_name.replace(".xlsx", "", processing_file_name.count(".xlsx") - 1)
    if processed_file_name.count(".xlsx") > 1:
        processed_file_name = processed_file_name.replace(".xlsx", "", processed_file_name.count(".xlsx") - 1)
    if output_file_name.count(".xlsx") > 1:
        output_file_name = output_file_name.replace(".xlsx", "", output_file_name.count(".xlsx") - 1)

    # Check if any raw data report input file exists in the Google Drive input folder. If there is not file there, a FileNotFoundError will be raised.
    # If the file exists, it will be downloaded to a temporary folder, renamed with the processing file name pattern (including timestamp) and moved to the processing folder. 
    google_service.download_file_by_name(folder_id=GOOGLE_DRIVE_INPUT_FOLDER_ID, file_name=RAW_DATA_REPORT_INPUT_FILE_NAME, dest_folder=temporary_path)

    # Remove raw data report from google drive input folder to avoid re-processing the same file in subsequent runs (this is a design choice, we could also choose to keep it and just skip it if it already exists locally)
    # **** Uncomment next line (and delete this line) when dev phase is done!
    # google_service.delete_file_by_name(folder_id=GOOGLE_DRIVE_INPUT_FOLDER_ID, file_name=RAW_DATA_REPORT_INPUT_FILE_NAME)

    # Copy downloaded file from temporary folder to the processing folder with the processing file name with timestamp
    shutil.copy(os.path.join(temporary_path, RAW_DATA_REPORT_INPUT_FILE_NAME), processing_file_name)

    # Rename downloaded file in temporary folder to the workarea's processing file
    os.rename(os.path.join(temporary_path, RAW_DATA_REPORT_INPUT_FILE_NAME), workarea_file_name)

    # Download general rules from Google Drive to the temporary folder to be used as input for Gemini. If no general rules file is found, a FileNotFoundError will be raised.
    general_rules_file_name = os.path.join(temporary_path, GENERAL_RULES_FILE_NAME)
    google_service.download_file_by_name(folder_id=GOOGLE_DRIVE_RULES_FOLDER_ID, file_name=GENERAL_RULES_FILE_NAME, dest_folder=temporary_path)

    # Load agent rules
    #FORMAT_RULES_SHEET_NAME = "Format, Sort & Filter"
    #AGENT_TUNING_SHEET_NAME = "Agent Tuning"
    #format_rules_df = pd.read_excel(general_rules_file_name, sheet_name=FORMAT_RULES_SHEET_NAME);
    #format_rules = format_rules_df.values.tolist()
    #agent_tuning_df = pd.read_excel(general_rules_file_name, sheet_name=AGENT_TUNING_SHEET_NAME);
    #agent_tuning = agent_tuning_df.values.tolist()
    #print(f"✅ Input file downloaded and moved into work area: {workarea_file_name}")
    #print(f"✅ General rules file downloaded: {general_rules_file_name}")
    #for idx, rule in enumerate(format_rules):
    #    print(f"  Format Rule {idx+1}: {rule}")
    #for idx, tuning in enumerate(agent_tuning):
    #    print(f"  Agent Tuning {idx+1}: {tuning}")
    #print("✅ Ready to process data and generate insights with Gemini!")

    
    
    
    
    ##############################################################################################################################
    ##############################################################################################################################
    # DO THE MAGIC WITH GEMINI!












    ##############################################################################################################################
    ##############################################################################################################################
    # GEMINI MAGIC DONE!
    # Rename (move) raw data report from processing folder to processed folder with the processed file name with timestamp (this is a design choice, we could also choose to keep it in the processing folder and just skip it if it already exists in subsequent runs)
    os.rename(processing_file_name, processed_file_name)

    # Upload final output file to Google Drive output folder with the output file name pattern (including timestamp). This will be done at the end of the processing, after generating the insights with Gemini and saving the output file locally.
    google_service.upload_file(source_file=processed_file_name, folder_id=GOOGLE_DRIVE_OUTPUT_FOLDER_ID, file_name=output_file_name)

    # Remove temporary folder and its content
    # **** Uncomment next lines (and delete this line) when dev phase is done!
    #if os.path.exists(temporary_path):
    #    for file in os.listdir(temporary_path):
    #        os.remove(os.path.join(temporary_path, file))
    #    os.rmdir(temporary_path)




    # All done!








###############################################################
# Main function
def main():
    print("")
    print("")
    print("")
    print("-------------------------------------------------------------------")
    print(f"-- {AGENT_NAME}-{AGENT_VERSION}: AI Agent based on Gemini")
    print("-- Meta-Information based on raw data")
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
    print("🤖 Agent initialized with the following configuration: ")
    print(f"  📂 Log folder:                         {LOG_FOLDER}")
    print(f"  📂 Temp folder:                        {TEMP_FOLDER}")
    print(f"  📂 Processing folder:                  {PROCESSING_FOLDER}")
    print(f"  📂 Processed folder:                   {PROCESSED_FOLDER}")
    print(f"  🔑 Google Credentials file:            {'*********' if GOOGLE_CREDENTIALS_FILE else 'Not Set'}")
    print(f"  🔑 Google Token file:                  {'*********' if GOOGLE_TOKEN_FILE else 'Not Set'}")
    print(f"  📂 Google Drive Rules folder ID:       {GOOGLE_DRIVE_RULES_FOLDER_ID}")
    print(f"  📂 Google Drive Input folder ID:       {GOOGLE_DRIVE_INPUT_FOLDER_ID}")
    print(f"  📂 Google Drive Output folder ID:      {GOOGLE_DRIVE_OUTPUT_FOLDER_ID}")
    print(f"  🤖 Gemini Model:                       {GEMINI_MODEL}")
    print(f"  🔑 Gemini API Key:                     {'*********' if GEMINI_API_KEY else 'Not Set'}")
    print(f"  📂 General Rules file name:            {GENERAL_RULES_FILE_NAME}")
    print(f"  📂 Department Rules file name pattern: {DEPARTMENT_RULES_FILE_NAME_PATTERN}")
    print(f"  📂 Raw Data Report input file name:    {RAW_DATA_REPORT_INPUT_FILE_NAME}")
    print(f"  📂 Processing file name pattern:       {PROCESSING_FILE_NAME_PATTERN}")
    print(f"  📂 Processed file name pattern:        {PROCESSED_FILE_NAME_PATTERN}")
    print(f"  📂 Output file name pattern:           {OUTPUT_FILE_NAME_PATTERN}")
    print(f"  📧 On Error Notification Emails:       {ON_ERROR_NOTIFICATION_EMAILS}")
    print(f"  📧 On Success Notification Emails:     {ON_SUCCESS_NOTIFICATION_EMAILS}")
    print("-------------------------------------------------------------------")
    print("")
    print("")
    print("")
    print("")




    print("Validating configuration...")
    validate_configuration()
    print("✅ Configuration validated successfully!")
    print("")
    print("")




    print("Instanciating services...")
    print("  GoogleService...")
    try:
        global google_service
        google_service = GoogleService(credentials_path=GOOGLE_CREDENTIALS_FILE, token_path=GOOGLE_TOKEN_FILE)
    except Exception as e:
        print(f"    ❌ Error instanciating GoogleService: {e}")
        send_email(subject=f"{AGENT_NAME} Initialization Error", body=f"Unable to initialize GoogleService: {e}. Please check the services/google_service.py file and ensure it exists and is correctly implemented.", to_emails=ON_ERROR_NOTIFICATION_EMAILS)
        print("    Exiting with error code 1 due to GoogleService initialization failure.")
        sys.exit(1)
    print("  ✅ GoogleService instanciated successfully!")
    print("  GeminiService...")
    try:
        global gemini_service
        gemini_service = GeminiService(gemini_model=GEMINI_MODEL, gemini_api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"    ❌ Error instanciating GeminiService: {e}")
        send_email(subject=f"{AGENT_NAME} Initialization Error", body=f"Unable to initialize GeminiService: {e}. Please check the services/gemini_service.py file and ensure it exists and is correctly implemented.", to_emails=ON_ERROR_NOTIFICATION_EMAILS)
        print("    Exiting with error code 1 due to GeminiService initialization failure.")
        sys.exit(1)
    print("  ✅ GeminiService instanciated successfully!")
    print("✅ Services instanciated successfully!")
    print("✅ Ready to process data and generate insights with Gemini!")
    print("")
    print("")




    # Execute the agent
    print("-------------------------------------------------------------------")
    print(f"Executing {AGENT_NAME}-{AGENT_VERSION}...")
    global agent_execution_start_dt
    agent_execution_start_dt = datetime.now()
    agent_execution_start = agent_execution_start_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"   Agent execution started at: {agent_execution_start}")
    try:
        execute_agent()
    except Exception as e:
        print(f"❌ Error during agent execution: {e}")
        send_email(subject=f"{AGENT_NAME} Execution Error", body=f"An error occurred during agent execution: {e}. Please check the agent's log folder for details and investigate the issue.", to_emails=ON_ERROR_NOTIFICATION_EMAILS)
        print("Exiting with error code 1 due to execution failure.")
        sys.exit(1)
    print(f"   Processing file name: {processing_file_name}")
    print(f"   Processed file name:  {processed_file_name}")
    print(f"   Output file path:     {output_file_path}")
    print(f"   Output file name:     {output_file_name}")


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
    emailBody+= f"  Agent execution started at: {agent_execution_start}\n"
    emailBody+= f"  Agent execution ended at:   {agent_execution_end}\n"
    emailBody+= f"  Total execution time: {total_seconds} seconds or {agent_execution_time}\n\n"
    emailBody+= f"  Google drive input folder ID:  {GOOGLE_DRIVE_INPUT_FOLDER_ID}\n"
    emailBody+= f"  Input file name:               {RAW_DATA_REPORT_INPUT_FILE_NAME}\n"
    emailBody+= f"  Google drive output folder ID: {GOOGLE_DRIVE_OUTPUT_FOLDER_ID}\n"
    emailBody+= f"  Output file name:              {output_file_name}\n\n\n\n"
    emailBody+= "Please check the agent's local log folder for details and the google drive output folder for results!\n"
    emailBody+= "Have a great day! 🪐"
    send_email(subject=emailSubject, body=emailBody, to_emails=ON_SUCCESS_NOTIFICATION_EMAILS)
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
    sys.exit(0)
    

    # Next steps for the Lab:
    # 1. Authenticate with Google (Drive/Gmail)
    # 2. Search and download 'reporte.xlsx' and 'reglas.xlsx'
    # 3. Send data to Gemini
    # 4. Generate output and send via Gmail








###############################################################
# Entry point
if __name__ == "__main__":
    main()
