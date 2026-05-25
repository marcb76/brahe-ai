# services/agent_service.py
import json
import os
import shutil
import pandas as pd




class AgentService:
    TIMESTAMP_FORMAT = "%Y.%m.%d-%H-%M-%S"
    WORK_AREA_PROCESSING_FILE_NAME_PATTERN = "brahe-ai-processing-{}.xlsx"  # {} will be replaced with timestamp
    AGENT_VERBS_SHEET_NAME = "Agent"
    GEMINI_CONTEXTS_SHEET_NAME = "Gemini"


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
        agent_verbs_df = pd.read_excel(general_rules_file_path, sheet_name=self.AGENT_VERBS_SHEET_NAME)
        gemini_contexts_df = pd.read_excel(general_rules_file_path, sheet_name=self.GEMINI_CONTEXTS_SHEET_NAME)
        return agent_verbs_df.values.tolist(), gemini_contexts_df.values.tolist()




    def apply_pandas_verb(self, df, pandas_verb, gemini_context):
        """
        Apply a single Pandas rule to the input Excel file and return the resulting DataFrame.
        Parameters:
            - df: The DataFrame to which the rule will be applied.
            - pandas_verb: The specific Pandas rule (verb) to apply.
            - gemini_context: The Gemini context to use for the rule, containing the prompt pattern and system instruction.
        Returns:
            - The resulting DataFrame after applying the Pandas verb with the Gemini context.
        """
        # Apply the pandas_verb via gemini... return the resulting DataFrame after applying the rule.
        verb_name = pandas_verb[1]
        human_instruction = pandas_verb[2]
        gemini_prompt = gemini_context[1].replace("{value}", human_instruction)
        gemini_system_instruction = gemini_context[3]

        if self.gemini_service.debugMode:
            print(f"AgentService::gemini::invoking Gemini for dataframe code-generation transformation while applying verb '{verb_name}'")
        gemini_response = self.gemini_service.gemini(prompt=gemini_prompt, system_instruction=gemini_system_instruction, json_output=False)
        try:
            if self.gemini_service.debugMode:
                print(f"AgentService::gemini::applying Gemini-generated code over dataframe with shape: {df.shape}; columns: {df.columns.tolist()}...")
            exec_context = { "df": df.copy(), "google_service": self.google_service }
            gemini_code_to_execute = self.gemini_service.sanitize_gemini_generated_python_response(gemini_response)
            compiled_gemini_code_to_execute = compile(gemini_code_to_execute, '<string>', 'exec')
            exec(compiled_gemini_code_to_execute, {}, exec_context)
            updated_df = exec_context["df"]
            if self.gemini_service.debugMode:
                print(f"AgentService::gemini::gemini-generated code applied. Resulting dataframe shape: {updated_df.shape}; columns: {updated_df.columns.tolist()}")
            return updated_df
        except SyntaxError as se:
            raise SyntaxError(f"Syntax error in Gemini-generated code: {se}\nGenerated code was:\n{gemini_code_to_execute}")
        except Exception as e:
            raise RuntimeError(f"Error executing Gemini-generated code: {e}\nGenerated code was:\n{gemini_code_to_execute}")




    def do_the_magic_with_gemini(self, workarea_path, workarea_file_name, agent_verbs, gemini_contexts):
        """
        This is where the core logic of the agent will be implemented, applying Gemini to the input file based on the loaded rules and generating output.
        Parameters:
            - workarea_path: The temporary working directory where the agent can read/write files during processing.
            - workarea_file_name: The name of the file in the working directory that contains the data to be processed.
            - agent_verbs: The list of agent verbs loaded from the Excel file.
            - gemini_contexts: The list of Gemini contexts loaded from the Excel file.
        Returns:
            - A list of output file names generated as a result of applying the agent logic with Gemini. This could include processed Excel files, CSVs, text files, or any other relevant output formats depending on the applied rules and contexts.
        """

        if self.gemini_service.debugMode:
            print(f"AgentService::do_the_magic_with_gemini::starting Gemini processing with:")
            print(f"AgentService::do_the_magic_with_gemini::workarea_path:      {workarea_path}")
            print(f"AgentService::do_the_magic_with_gemini::workarea_file_name: {workarea_file_name}")

        # No output files generated yet
        output_file_names = []
        ################################################################################################################################
        # Apply pandas verbs... if any
        pandas_verbs = [verb for verb in agent_verbs if verb[0].lower() == "pandas"]
        if pandas_verbs:
            # Ensure there is one and only one Gemini context to apply with the Pandas verb(s)
            gemini_contexts_for_pandas = [context for context in gemini_contexts if context[0].lower() == "pandas"]
            if len(gemini_contexts_for_pandas) != 1:
                raise ValueError("Pandas verbs were found in agent rules but no Gemini pandas context was found. When applying pandas verbs, there must be one AND ONLY one Gemini context for the pandas realm.")
            gemini_context = gemini_contexts_for_pandas[0]
            # Apply each pandas verb over input dataframe using the defined Gemini context
            df = pd.read_excel(workarea_file_name)
            if self.gemini_service.debugMode:
                print(f"AgentService::do_the_magic_with_gemini::{len(pandas_verbs)} pandas verbs to be applied over dataframe of shape {df.shape} and using the following Gemini context:")
                print(f"AgentService::do_the_magic_with_gemini::Gemini prompt pattern:     {gemini_context[1].replace(chr(10), ' ').replace(chr(13), ' ')}")
               #print(f"AgentService::do_the_magic_with_gemini::Gemini system instruction: {gemini_context[3].replace(chr(10), ' ').replace(chr(13), ' ')}")
            for pandas_verb in pandas_verbs:
                df = self.apply_pandas_verb(df, pandas_verb, gemini_context)
            # After applying all pandas verbs, save the resulting DataFrame into the same workarea file (overwriting it)
            df.to_excel(workarea_file_name, index=False)
        output_file_names.append(workarea_file_name)
        return output_file_names




    def execute(self, execution_start_dt):
        """
        Main execution method for the agent. This is where the core logic of the agent will be implemented.
        It will use the prepared paths, download files (from Google Drive), parse rules, invoke (several times) gemini, generate new insight and generate the outputs to Google Drive).
        """
        ################################################################################################################################
        # PRE-PROCESSING STEPS: Prepare paths, download input file from Google Drive, load rules from Excel, etc.
        # Apply patterns to paths and file names
        paths = self.prepare_runtime_paths(execution_start_dt)
        
        # Download (and remove in order to avoid double processing) raw_data_report from Google Drive's input folder to the temporary folder
        self.google_service.download_file_by_name(folder_id=self.google_drive_input_folder_id, file_name=self.raw_data_report_input_file_name, dest_folder=paths["temporary_folder"])
        # self.google_service.delete_file_by_name(folder_id=self.google_drive_input_folder_id, file_name=self.raw_data_report_input_file_name)

        # Copy downloaded file from temporary folder to the processing folder
        shutil.copy(os.path.join(paths["temporary_folder"], self.raw_data_report_input_file_name), paths["processing_file_name"])

        # Rename downloaded file in temporary folder to work area processing file name
        os.rename(os.path.join(paths["temporary_folder"], self.raw_data_report_input_file_name), paths["work_area_processing_file_name"])

        # Download general rules Excel file from Google Drive to the temporary folder (replace if already present to ensure we have the latest version)
        if os.path.exists(os.path.join(self.temp_folder, self.general_rules_file_name)):
            os.remove(os.path.join(self.temp_folder, self.general_rules_file_name))
        self.google_service.download_file_by_name(folder_id=self.google_drive_rules_folder_id, file_name=self.general_rules_file_name, dest_folder=self.temp_folder)

        # Load agent rules from Excel file into structured lists (matrix format) for processing
        agent_verbs, gemini_contexts = self.load_rules_from_excel()




        ################################################################################################################################
        ################################################################################################################################
        # DO THE MAGIC WITH GEMINI!
        output_files = self.do_the_magic_with_gemini(
            workarea_path=paths["temporary_folder"],
            workarea_file_name=paths["work_area_processing_file_name"],
            agent_verbs=agent_verbs,
            gemini_contexts=gemini_contexts
        )
        ################################################################################################################################
        ################################################################################################################################




        ################################################################################################################################
        # POST-PROCESSING STEPS: Move processed file to processed folder, upload output files to Google Drive, clean up temporary files, etc.
        # Move (rename) processed file from processing folder to processed folder
        shutil.move(paths["processing_file_name"], paths["processed_file_name"])

        # Upload output files to Google Drive's output folder
        for output_file in output_files:
            self.google_service.upload_file(source_file=output_file, folder_id=self.google_drive_output_folder_id, file_name=os.path.basename(output_file)) 

        # Remove temporary folder and its content
        #shutil.rmtree(paths["temporary_folder"])

        # All done! Agent execution completed successfully.
        return {
            "status": "success",
            "message": "Agent execution completed successfully.",
            "output_files": output_files
        }
