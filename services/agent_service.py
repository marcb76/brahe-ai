# services/agent_service.py
import os
import shutil
import pandas as pd




class AgentService:
    TIMESTAMP_FORMAT = "%Y.%m.%d-%H-%M-%S"
    WORK_AREA_PROCESSING_FILE_NAME_PATTERN = "brahe-ai-processing-{}.xlsx"  # {} will be replaced with timestamp
    FORMAT_RULES_SHEET_NAME = "Format, Sort & Filter"
    AGENT_TUNING_SHEET_NAME = "Agent Tuning"


    def __init__(self, 
                 google_service, 
                 gemini_service,
                 configuration_service):
        self.google_service = google_service
        self.gemini_service = gemini_service
        self.log_folder = configuration_service.LOG_FOLDER
        self.temp_folder = configuration_service.TEMP_FOLDER
        self.processing_folder = configuration_service.PROCESSING_FOLDER
        self.processed_folder = configuration_service.PROCESSED_FOLDER
        self.processing_file_name_pattern = configuration_service.PROCESSING_FILE_NAME_PATTERN
        self.processed_file_name_pattern = configuration_service.PROCESSED_FILE_NAME_PATTERN
        self.work_area_processing_file_name_pattern = self.WORK_AREA_PROCESSING_FILE_NAME_PATTERN
        self.output_file_name_pattern = configuration_service.OUTPUT_FILE_NAME_PATTERN
        self.timestamp_format = self.TIMESTAMP_FORMAT
        self.google_drive_input_folder_id = configuration_service.GOOGLE_DRIVE_INPUT_FOLDER_ID
        self.google_drive_output_folder_id = configuration_service.GOOGLE_DRIVE_OUTPUT_FOLDER_ID
        self.google_drive_rules_folder_id = configuration_service.GOOGLE_DRIVE_RULES_FOLDER_ID
        self.raw_data_report_input_file_name = configuration_service.RAW_DATA_REPORT_INPUT_FILE_NAME
        self.general_rules_file_name = configuration_service.GENERAL_RULES_FILE_NAME





    def prepare_runtime_paths(self, execution_start_dt):
        """
        Build final runtime paths for the agent, cleaning and generating all path variables.
        Avoids issues with duplicate extensions (.xlsx.xlsx).
        """
        # Apply patterns to format names based on your patterns and timestamp
        execution_start = execution_start_dt.strftime(self.timestamp_format)
        temporary_folder = os.path.join(self.temp_folder, f"exec_{execution_start}")
        work_area_processing_file_name = os.path.join(temporary_folder, self.work_area_processing_file_name_pattern.format(execution_start))
        processing_file_name = os.path.join(self.processing_folder, self.processing_file_name_pattern.format(self.raw_data_report_input_file_name, execution_start))
        processed_file_name = os.path.join(self.processed_folder, self.processed_file_name_pattern.format(self.raw_data_report_input_file_name, execution_start))
        output_file_name = os.path.join(self.temp_folder, self.output_file_name_pattern.format(self.raw_data_report_input_file_name, execution_start))

        # Clean any potential duplicate .xlsx extensions that could have been added due to pattern formatting
        processing_file_name = self._clean_xlsx_extension(processing_file_name)
        processed_file_name = self._clean_xlsx_extension(processed_file_name)
        output_file_name = self._clean_xlsx_extension(output_file_name)

        # Return structured dictionary with final absolute/relative paths for processing, processed, and output files
        return {
            "temporary_folder": temporary_folder,
            "work_area_processing_file_name": work_area_processing_file_name,
            "processing_file_name": processing_file_name,
            "processed_file_name": processed_file_name,
            "output_file_name": output_file_name
        }




    def _clean_xlsx_extension(self, filename: str) -> str:
        """
        Remove any duplicate internal .xlsx extensions that could have been added due to pattern formatting.
        """
        if filename.count(".xlsx") > 1:
            return filename.replace(".xlsx", "", filename.count(".xlsx") - 1)
        return filename




    def load_rules_from_excel(self):
        """
        Load agent business rules from Excel (using Pandas) and return them as lists in matrix format (list).
        """
        general_rules_file_path = os.path.join(self.temp_folder, self.general_rules_file_name)
        if not os.path.exists(general_rules_file_path):
            raise FileNotFoundError(f"General Rules (Excel) file not found at: {general_rules_file_path}")
        format_rules_df = pd.read_excel(general_rules_file_path, sheet_name=self.FORMAT_RULES_SHEET_NAME)
        agent_tuning_df = pd.read_excel(general_rules_file_path, sheet_name=self.AGENT_TUNING_SHEET_NAME)
        return format_rules_df.values.tolist(), agent_tuning_df.values.tolist()




    def do_the_magic_with_gemini(self, workarea_path, workarea_file_name, format_rules, agent_tuning):
        """
        This is where the core logic of the agent will be implemented, applying Gemini to the input file based on the loaded rules and generating output.
        Parameters:
            - workarea_path: The temporary working directory where the agent can read/write files during processing.
            - workarea_file_name: The name of the file in the working directory that contains the data to be processed.
            - format_rules: The list of formatting, sorting, and filtering rules loaded from the Excel file.
            - agent_tuning: The list of agent tuning parameters loaded from the Excel file.
        """
        # Implement your core logic here to process the input file based on the loaded rules and generate output using Gemini.
        # This is a placeholder for where you would add the specific processing steps for your agent's functionality.

        print("")
        print("")
        print("")
        print("***************************************************************")
        print("******************** EXECUTING AGENT LOGIC ********************")
        print("**  Executing agent with the following semantics:")
        print("**    - Work area path: " + workarea_path)
        print("**    - Work area file name: " + workarea_file_name)
        print("**    - Format rules:")
        for rule in format_rules:
            print("**        - " + str(rule))
        print("**    - Agent tuning parameters:")
        for tuning in agent_tuning:
            print("**        - " + str(tuning))
        print("***************************************************************")
        print("***************************************************************")
        print("")
        print("")
        print("")
        output_files = []
        return output_files




    def execute(self, execution_start_dt):
        """
        Main execution method for the agent. This is where the core logic of the agent will be implemented.
        It will use the prepared paths, download files (from Google Drive), parse rules, invoke (several times) gemini, generate new insight and generate the outputs to Google Drive).
        """
        # Apply patterns to paths and file names
        paths = self.prepare_runtime_paths(execution_start_dt)
        
        # Download (and remove in order to avoid double processing) raw_data_report from Google Drive's input folder to the temporary folder
        self.google_service.download_file_by_name(folder_id=self.google_drive_input_folder_id, file_name=self.raw_data_report_input_file_name, dest_folder=paths["temporary_folder"])
        self.google_service.delete_file_by_name(folder_id=self.google_drive_input_folder_id, file_name=self.raw_data_report_input_file_name)

        # Copy downloaded file from temporary folder to the processing folder
        shutil.copy(os.path.join(paths["temporary_folder"], self.raw_data_report_input_file_name), paths["processing_file_name"])

        # Rename downloaded file in temporary folder to work area processing file name
        os.rename(os.path.join(paths["temporary_folder"], self.raw_data_report_input_file_name), paths["work_area_processing_file_name"])

        # Download general rules Excel file from Google Drive to the temporary folder (replace if already present to ensure we have the latest version)
        if os.path.exists(os.path.join(self.temp_folder, self.general_rules_file_name)):
            os.remove(os.path.join(self.temp_folder, self.general_rules_file_name))
        self.google_service.download_file_by_name(folder_id=self.google_drive_rules_folder_id, file_name=self.general_rules_file_name, dest_folder=self.temp_folder)

        # Load agent rules from Excel file into structured lists (matrix format) for processing
        format_rules, agent_tuning = self.load_rules_from_excel()




        ##############################################################################################################################
        ##############################################################################################################################
        # DO THE MAGIC WITH GEMINI!
        output_files = self.do_the_magic_with_gemini(
            workarea_path=paths["temporary_folder"],
            workarea_file_name=paths["work_area_processing_file_name"],
            format_rules=format_rules,
            agent_tuning=agent_tuning
        )
        ##############################################################################################################################
        ##############################################################################################################################




        # Move (rename) processed file from processing folder to processed folder
        shutil.move(paths["processing_file_name"], paths["processed_file_name"])

        # Upload output files to Google Drive's output folder
        for output_file in output_files:
            self.google_service.upload_file(source_file=output_file, folder_id=self.google_drive_output_folder_id, file_name=os.path.basename(output_file)) 

        # Remove temporary folder and its content
        shutil.rmtree(paths["temporary_folder"])

        # All done! Agent execution completed successfully.
        return {
            "status": "success",
            "message": "Agent execution completed successfully.",
            "output_files": output_files
        }
