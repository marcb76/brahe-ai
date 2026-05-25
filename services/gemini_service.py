# services/gemini_service.py
import json
import os
import google.generativeai as genai




class GeminiService:
    def __init__(self, gemini_model, gemini_api_key, debugMode=False):
        """
        Initialize and authenticate Gemini service.
        Parameters:
            - gemini_model: Name of the Gemini model to use (e.g., 'gemini-1.5-flash').
            - gemini_api_key: API key for authenticating with Google AI services.
            - debugMode: If True, enables debug mode for detailed logging (optional).
        Raises ValueError if either the model name or API key is missing.
        """
        if not gemini_model:
            raise ValueError("Gemini model name is missing. Please set the 'GEMINI_MODEL' environment variable with the desired Google AI model (e.g., 'gemini-1.5-flash').")
        if not gemini_api_key:
            raise ValueError("Gemini API key is missing. Please set the 'GEMINI_API_KEY' environment variable with your Google AI API key.")
        genai.configure(api_key=gemini_api_key)
        self.model_name = gemini_model
        self.debugMode = debugMode
        if self.debugMode:
            print(f"GeminiService::__init__::initialized with model: {self.model_name}; debugMode: {self.debugMode}")




    def gemini(self, prompt: str, system_instruction: str = None, file_paths: list = None, json_output: bool = False):
        """
        Invokes Gemini to process a prompt along with optional system instructions and files, returning the generated response.
        Parameters:
            - prompt: The specific task or question to be addressed.
            - system_instruction: The fixed role, personality, or rules for the agent (optional).
            - file_paths: List of local file paths to be processed (e.g., ['tmp/reporte.xlsx', 'tmp/reglas.pdf']) (optional).
            - json_output: If True, forces Gemini to respond strictly in valid JSON format (optional).
         Returns: The generated response from Gemini, either as text or JSON depending on the configuration.
         Raises: ValueError for missing prompt, and RuntimeError for API issues.
         Note: The method handles the entire flow from uploading files to Gemini, generating the response, and cleaning up temporary files in Google AI's File API.
         """
        uploaded_files = []
        
        try:
            # If request has files, upload each local file to Gemini's File API and get their references for the prompt
            if file_paths:
                for path in file_paths:
                    if not os.path.exists(path):
                        raise FileNotFoundError(f"The file '{path}' does not exist. Please check the path and try again.")
                    g_file = genai.upload_file(path=path)
                    uploaded_files.append(g_file)

            # Configure the model behavior (System Instructions and Output Format)
            generation_config = {}
            if json_output:
                generation_config["response_mime_type"] = "application/json"

            # Create the model instance applying the fixed system rules and the generation configuration (e.g., forcing JSON output if requested)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction,
                generation_config=generation_config
            )

            
            # Consolidate the content (Combine the uploaded files from Google with the text prompt) and generate the response from Gemini (do the magic!)
            contents = uploaded_files + [prompt]
            if self.debugMode:
                print(f"GeminiService::gemini::invoking gemini with prompt: {prompt.replace(chr(10), ' ').replace(chr(13), ' ')}")
                print(f"GeminiService::gemini::         system_instruction: {system_instruction.replace(chr(10), ' ').replace(chr(13), ' ')}")
                print(f"GeminiService::gemini::                json_output: {json_output}")
            response = model.generate_content(contents)
            if self.debugMode:
                print(f"GeminiService::gemini::raw response from Gemini: {response.text}")
                if hasattr(response, 'mime_type'):
                    print(f"GeminiService::gemini::response MIME type: {response.mime_type}")
                if hasattr(response, 'files'):
                    print(f"GeminiService::gemini::response includes files: {[f.name for f in response.files]}")
                if hasattr(response, 'metadata'):
                    print(f"GeminiService::gemini::response metadata: {response.metadata}")
                if hasattr(response, 'usage_metadata'):
                    print(f"GeminiService::gemini::response usage metadata-tokens-in: {response.usage_metadata.prompt_token_count}, tokens-out: {response.usage_metadata.candidates_token_count}, total-tokens: {response.usage_metadata.total_token_count}")
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error in Gemini service: {e}")
        finally:
            # Critical Cleanup: Delete temporary files from Google AI's File API to free up memory and avoid hitting storage limits in subsequent runs
            if uploaded_files:
                for g_file in uploaded_files:
                    try:
                        genai.delete_file(g_file.name)
                    except Exception:
                        if self.debugMode:
                            print(f"GeminiService::gemini::failed to delete temporary file: {g_file.name}")
                        pass # Prevent a failure in freeing memory from stopping the main flow




    def sanitize_gemini_generated_python_response(self, raw_response):
        """
        Parse and sanitize Gemini's raw response to extract clean Python code that can be executed.
        IMPORTANT: It is expected that Gemini was invoked with json_output=False.
        Parameters:
            - raw_response: The original response from Gemini, which may contain the code in various formats.
        Returns: A clean string containing only the Python code that can be executed.
        """

        if self.debugMode:
            print(f"GeminiService::sanitize_gemini_generated_python_response::sanitizing raw response: {raw_response}")
        if raw_response is None:
            return ""
        code = raw_response.strip()
        if self.debugMode:
            print(f"GeminiService::sanitize_gemini_generated_python_response::sanitized code: {code}")
        return code
