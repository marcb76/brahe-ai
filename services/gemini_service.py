# services/gemini_service.py
import json
import os
import google.generativeai as genai




class GeminiService:
    def __init__(self, gemini_model, gemini_api_key):
        """
        Initialize and authenticate Gemini service.
        Parameters:
            - gemini_model: Name of the Gemini model to use (e.g., 'gemini-1.5-flash').
            - gemini_api_key: API key for authenticating with Google AI services.
        Raises ValueError if either the model name or API key is missing.
        """
        if not gemini_model:
            raise ValueError("Gemini model name is missing. Please set the 'GEMINI_MODEL' environment variable with the desired Google AI model (e.g., 'gemini-1.5-flash').")
        if not gemini_api_key:
            raise ValueError("Gemini API key is missing. Please set the 'GEMINI_API_KEY' environment variable with your Google AI API key.")
        genai.configure(api_key=gemini_api_key)
        # Usamos 1.5-flash ya que está optimizado para ventanas de contexto gigantes (multimodal)
        self.model_name = gemini_model




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
            response = model.generate_content(contents)
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
                        pass # Prevent a failure in freeing memory from stopping the main flow




    @staticmethod
    def sanitize_gemini_generated_python_response(raw_response):
        """
        Parse and sanitize Gemini's raw response to extract clean Python code that can be executed, especially when Gemini is asked to generate code in a JSON format or within Markdown code blocks. This function handles various formats in which Gemini might return the code, such as:
            - Direct code as a string.
            - JSON object with a "code" field.
            - Markdown code blocks.
        Parameters:
            - raw_response: The original response from Gemini, which may contain the code in various formats.
        Returns: A clean string containing only the Python code that can be executed.
        """

        # If it comes as JSON {"code": "..."}, extract the value
        code = raw_response.strip()
        try:
            if code.startswith('{'):
                data = json.loads(code)
                if 'code' in data:
                    code = data['code']
        except json.JSONDecodeError:
            # If not valid JSON, continue with the original string
            pass

        # Remove Markdown code block markers (```python ... ```)
        # Look for blocks delimited by ```
        if "```" in code:
            parts = code.split("```")
            # If it has ```python at the start, the code is usually in the second segment
            if len(parts) >= 3:
                code = parts[1].replace("python", "", 1).strip()
            else:
                code = parts[0].strip()

        # Remove any escaped quotes that Gemini might have included (e.g., \"df = ...\" or \'df = ...\')
        code = code.replace('\\"', '"').replace("\\'", "'")
        
        # Remove enclosing quotes that Gemini sometimes includes (e.g., "df = ...")
        code = code.strip('"').strip("'")

        # Final cleanup of any extraneous whitespace
        return code.strip()