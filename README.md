# brahe-ai

> A rule-driven AI agent prototype for turning operational spreadsheets into repeatable data transformations and business insights with Gemini and Google Workspace services.

---

## Author & Copyright

**Author:** Marc Bonet  
**Copyright:** © 2026 Marc Bonet.  
*This mini-project began as a research and development experiment with the Gemini API. Its broader goal is to explore how configurable AI workflows can help teams prepare recurring spreadsheet data, derive useful summaries, and deliver results through the tools they already use.*

---

## Motivation & Objective

Organizations often repeat the same spreadsheet preparation and reporting tasks: selecting fields, sorting records, applying business rules, summarizing results, and sharing them with the right people. These workflows are usually manual, difficult to adapt, and disconnected from the systems where the source data lives.

**brahe-ai** explores an agent-based approach to that problem: making spreadsheet analysis accessible through human language. The goal is for anyone—not only people who know how to program—to describe the transformations or analysis they need in ordinary language and use AI to turn raw Excel data into useful new information in an easy, natural way.

The agent's capabilities are designed to grow with the human-readable verbs defined as rows in the Excel rules workbook. Each verb describes a transformation or analysis; Gemini translates the instruction into Python so the user can extend a workflow through the rules workbook instead of writing code. In principle, a workflow can support as many transformations and analyses as there are verbs, within the realms and operations implemented by the agent.

Its longer-term objective is to provide a configurable assistant that can take an operational spreadsheet, apply business-defined transformations, generate useful insights, and deliver the resulting artifacts through Google Drive and Gmail.

_The current repository is an early R&D prototype. It demonstrates the core integration pattern—rules in Excel, code generation with Gemini, spreadsheet processing with pandas, and Google Workspace actions—but **is not a production-ready** automation platform._

---

## Story and Etymology

- **Tycho Brahe** (16th-century astronomer).

Long before computers or advanced telescopes existed, Tycho Brahe spent decades collecting the largest and most precise collection of scattered astronomical data in human history.  
His data tables were so massive and meticulous that, after his death, Johannes Kepler used them to formulate the laws of planetary motion.  
https://en.wikipedia.org/wiki/Tycho_Brahe

Brahe AI performs the exact same role for e-commerce: it processes a vast universe of massive, scattered transactional data, enabling store owners to uncover the fundamental laws governing their business sales.  
**The name is concise, modern, and memorable.**

---

## What It Does

In the current implementation, an execution:

1. Authenticates with Google and downloads the input workbook and general rules workbook from Drive.
2. Reads instructions from the `Agent` and `Gemini` sheets in the rules workbook. Each active verb is written as a human-readable instruction.
3. Selects rules whose `Realm` is `pandas` and asks Gemini to translate those instructions into Python code.
4. Applies the generated code to a pandas DataFrame.
5. Uploads the resulting workbook to Drive and sends the configured success or error notification through Gmail.

Rows with other realm values, like `xpandas`, are ignored by the current agent. They can be kept as test scenarios or similar.  
The intended experience is that a user can describe what they want to learn or change about the spreadsheet without writing Python. The number of available analyses and transformations can grow by adding human-readable verbs to the rules workbook, subject to the functionality supported by the agent.  
The sample rules workbook also demonstrates an insight task that asks Gemini-generated code to summarize records by department and send an email. Review the rules and recipient addresses before running the agent.

---

## Technology Stack

- **Python** for orchestration and service integration.
- **Gemini API** for generating Python transformations from configurable prompts.
- **pandas and Excel tooling** for spreadsheet data processing.
- **Google Drive API** for retrieving inputs and publishing results.
- **Gmail API** for execution notifications and rule-driven messages.
- **Excel workbooks** for defining agent verbs and Gemini contexts.

---

## Architecture & Workflow

```text
Google Drive input workbook ─┐
                             ├─> AgentService ─> Gemini-generated Python
Google Drive rules workbook ─┘                       │
                                                     ▼
                                               pandas DataFrame
                                                     │
                                      transformed workbook / insights
                                          │                    │
                                          ▼                    ▼
                                    Google Drive         Gmail messages
```

The main components are:

- `brahe-ai.py`: application entry point and service orchestration.
- `services/configuration_service.py`: environment configuration loading and validation.
- `services/google_service.py`: Google OAuth, Drive, and Gmail integration.
- `services/gemini_service.py`: Gemini requests and temporary Gemini File API uploads.
- `services/agent_service.py`: rule loading, DataFrame processing, and file workflow.
- `services/notification_service.py`: success and error notifications.
- `assets/rules/brahe-ai-general-rules.xlsx`: example agent verbs and Gemini prompts.

---

## Requirements

- Python 3 and `pip`.
- A Gemini API key and access to the configured Gemini model.
- A Google Cloud project with the Google Drive and Gmail APIs enabled.
- Google OAuth desktop application credentials.
- 7-Zip and the configured Windows backup destination, if using `generateBackupImage.cmd`.

## Installation

Create and activate a virtual environment from the repository root:

```bash
python -m venv venv
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

git bash (Windows):

```gitbash
source venv/Scripts/activate
```

macOS or Linux:

```bash
source venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 google-generativeai pandas openpyxl python-dotenv
```

## Configuration

1. Copy `.env.sample` to `.env` and fill in the values for your environment.
2. Place your Google OAuth desktop credentials at the path configured by `GOOGLE_CREDENTIALS_FILE`. The first run can open a browser-based authorization flow and save a token at `GOOGLE_TOKEN_FILE`.
3. Set the Gemini API key and model, Google Drive folder IDs, input workbook name, and notification recipients.
4. Make sure the workbook and rules sheet names match the configured values.

Key settings include:

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API key. |
| `GEMINI_MODEL` | Gemini model name. |
| `GEMINI_DEBUG_MODE` | Enables detailed Gemini debug logging. |
| `GOOGLE_CREDENTIALS_FILE` | Path to Google OAuth desktop credentials. |
| `GOOGLE_TOKEN_FILE` | Local path for the OAuth token. |
| `GOOGLE_DRIVE_RULES_FOLDER_ID` | Drive folder containing the rules workbook. |
| `GOOGLE_DRIVE_INPUT_FOLDER_ID` | Drive folder containing the input workbook. |
| `GOOGLE_DRIVE_OUTPUT_FOLDER_ID` | Drive folder for generated output. |
| `GENERAL_RULES_FILE_NAME` | Rules workbook name. |
| `RAW_DATA_REPORT_INPUT_FILE_NAME` | Input workbook name. |
| `ON_ERROR_NOTIFICATION_EMAILS` | Comma-separated error notification recipients. |
| `ON_SUCCESS_NOTIFICATION_EMAILS` | Comma-separated success notification recipients. |

See `.env.sample` for directory settings and filename patterns. Never commit `.env`, `token.json`, or `credentials.json`.

## Agent Rules Workbook

The workbook configured by `GENERAL_RULES_FILE_NAME` is expected to contain:

- An `Agent` sheet with `Realm`, `Verb`, and `Value` columns.
- A `Gemini` sheet with the prompt pattern and system instructions used to generate code.

Active rules run in workbook order. The current implementation applies `pandas` realm rules to the DataFrame; other realms are ignored. The included workbook is an experiment and should be reviewed before use, especially when rules request external actions such as sending email.

## Run

With the virtual environment active and `.env` configured:

```bash
python brahe-ai.py
```

The agent authenticates with Google, downloads its configured inputs, processes the data according to the active rules, uploads the resulting workbook, and sends a notification. The first run may require completing Google's OAuth flow in a browser.

---

## Security & Limitations

This is an R&D prototype, not a production service. The agent executes Python generated by Gemini with `exec`. That code runs with the process's local permissions and receives access to `google_service`, including its Drive and Gmail operations. Treat rule workbooks and model output as executable instructions. Use reviewed rules, test accounts, and non-sensitive data; do not run it with credentials or permissions beyond what the experiment needs.

The current workflow is intentionally narrow: it applies pandas rules to a single DataFrame and returns a work-area workbook. Additional realms, stronger execution isolation, and production controls remain future work.

The Windows backup script uses local paths configured in `generateBackupImage.cmd`; confirm that 7-Zip and the destination folder exist before using it.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for the full license text.

---

## About

**brahe-ai** is a small AI agent prototype for experimenting with rule-driven spreadsheet workflows, Gemini code generation, and Google Workspace integrations.
