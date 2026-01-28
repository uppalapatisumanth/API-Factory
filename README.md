# XLSX to API Generator

## Project Overview

The **XLSX to API Generator** is a powerful automated tool designed to streamline the API testing process. It accepts a strictly formatted XLSX specification file as input and automatically generates:

1.  **Postman Collections**: Ready-to-import JSON files for manual testing and sharing.
2.  **Pytest Automation Code**: Python-based test scripts for robust, automated regression testing.

This project bridges the gap between manual API documentation and executable tests, ensuring consistency and saving significant development time.

## Features

-   **Automated Generation**: Converts spreadsheet specifications into executable test code instantly.
-   **Smart URL Handling**: 
    -   Paste full absolute URLs (e.g., `https://api.com/v1/users`) directly.
    -   Automatically extracts the base URL into `{{basic url}}` variables for cleaner collections.
-   **Advanced Authentication**:
    -   **Token Generators**: Mark APIs as "Token Generators" to auto-create auth scripts.
    -   **Auto-Injection**: Use "Auth Scope: Collection" to automatically inject Bearer tokens into requests.
    -   **Smart Sanitization**: Prevents accidental usage of long tokens as variable names.
-   **Strict Schema Validation**: Ensures the uploaded XLSX file adheres to a defined structure before processing.
-   **Multi-Output Support**: Generates both Postman v2.1 collections and standard Pytest scripts.
-   **Real-time Processing**: Fast feedback loop with immediate download options for generated artifacts.
-   **Modern UI**: Clean, responsive web interface built with React and TailwindCSS.
-   **Extensible Architecture**: Modular backend design allows for easy addition of new capabilities.


## Deployment

Deploying your own instance for customers is easy.

### 1. Backend (Render)
Click the button below to deploy the backend to Render.
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/uppalapatisumanth/XLSX-to-API-Generator)

*   **Note**: After deploying, copy the **Backend URL** (e.g., `https://xlsx-to-api-generator-backend.onrender.com`).

### 2. Frontend (Vercel)
Click the button below to deploy the frontend.
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fuppalapatisumanth%2FXLSX-to-API-Generator%2Ftree%2Fmain%2Ffrontend&env=VITE_API_URL&envDescription=Backend%20URL%20(including%20https%3A%2F%2F)&project-name=xlsx-to-api-generator-frontend&repository-name=xlsx-to-api-generator-frontend)

*   **Important**: During setup, Vercel will ask for `VITE_API_URL`. Paste the **Backend URL** you got from Render.

---

## Tech Stack

## XLSX File Structure (Mandatory)

The uploaded Excel file must contain the following sheets and columns.

### Sheet: API_Definitions

| Column Name | Required | Description |
|------------|----------|-------------|
| Ref_ID | Yes | Unique API reference |
| Module | Yes | Feature/module name |
| API_Name | Yes | Human-readable name |
| Method | Yes | GET/POST/PUT/DELETE |
| Base_URL | Yes | API base URL |
| Endpoint | Yes | API endpoint path |
| Headers | No | JSON headers |
| Query_Params | No | JSON query params |
| Request_Body | No | JSON payload |
| Auth_Scope | No | collection / request |
| Token_API_Ref | No | Ref_ID of login API |
| Expected_Status | Yes | HTTP status |
| Expected_Response_Keys | No | JSON array |
| Expected_Message | No | Expected message |
| Test_Type | No | positive / negative |

*Note: Column names are case-insensitive and fuzzy-matched.*

## Authentication Handling

The system supports collection-level authentication.

### Token Generation Rules
- If a static token is provided in the XLSX, it is used directly.
- If no token is provided:
  - The API marked as Token Generator is executed first.
  - The token is extracted from its response.
  - The token is stored as a Postman collection variable.

### Supported Auth Scope Values
- **collection**: Token applied to all requests.
- **request**: Token applied only to that API.

## Documentation
- **[User Guide for XLSX Template](file:///C:/Users/IT%20ZONE/.gemini/antigravity/brain/06dd0c5f-d525-4d67-956c-8df297d28cc6/USER_GUIDE.md)**: Detailed instructions on finding columns and filling the sheet.
- **Sample File**: A sample file `sample_api.xlsx` is generated in the backend folder.

## Smart URL Handling

This feature allows you to copy-paste full browser URLs directly.

### Example

**Input URL:**
`https://api.example.com/v1/users`

**Generated Postman:**
`{{basic url}}/v1/users`

**Where:**
- `basic url` variable = `https://api.example.com`

---

### Backend
-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
-   **Server**: Uvicorn
-   **Data Processing**: Pandas, OpenPyXL, XlsxWriter
-   **Utilities**: Jinja2 (Templating), Requests

### Frontend
-   **Framework**: [React](https://react.dev/) (Vite)
-   **Styling**: [TailwindCSS](https://tailwindcss.com/)
-   **Icons**: Lucide-React
-   **HTTP Client**: Axios

## Installation & Setup

### Prerequisites
-   **Python 3.8+**: Ensure Python is installed and added to your system PATH.
-   **Node.js & npm**: Required for the frontend.

### 🚀 Quick Start (Recommended)

The easiest way to run the application is to use the included startup script.

1.  Open your terminal/command prompt.
2.  Navigate to the project root directory.
3.  Run the following command:
    ```powershell
    .\start_app.bat
    ```
    This script will automatically:
    -   Install python dependencies.
    -   Start the Backend server in a new window.
    -   Start the Frontend server in a new window.

---

### 🛠️ Manual Installation (Advanced)

If you prefer to run things manually, follow these steps. You will need **two separate terminal windows**.

#### Terminal 1: Backend Setup

1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```

2.  (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Start the backend server:
    ```bash
    python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    ```
    ✅ The backend is running at `http://127.0.0.1:8000`

#### Terminal 2: Frontend Setup

1.  Navigate to the `frontend` folder:
    ```bash
    cd frontend
    ```

2.  Install Node dependencies:
    ```bash
    npm install
    ```

3.  Start the frontend server:
    ```bash
    npm run dev
    ```
    ✅ The frontend is accessible at `http://localhost:5173`

or
Simply run the startup script from your terminal:

powershell
.\start_app.bat
This is the easiest way to get everything running.

Manual Method (If you prefer)
If you want to run them manually, you need to open two separate terminal windows and run these exact commands:

Terminal 1 (Backend):

powershell
cd backend
python -m uvicorn main:app --reload
Terminal 2 (Frontend):

powershell
cd frontend
npm run dev

## Usage Guide

1.  **Open the App**: Navigate to `http://localhost:5173` in your browser.
2.  **Download Template**: Click the "Download Template" button to get the strictly formatted `AI_API_Test_Template.xlsx`.
3.  **Fill the Data**:
    *   **apis**: Define your API endpoints, methods, headers, and payloads.
    *   **environments**: Set global variables like `base_url` or auth tokens.
    *   **rules**: Define extraction rules (e.g., capture `token` from a login response).
4.  **Upload & Generate**: Drag and drop your completed XLSX file into the upload area.
5.  **Get Results**: The system will process the file and provide download links for your Postman Collection and Pytest scripts.


## Validation & Error Handling

If validation fails:
- The request is rejected.
- A structured error response is returned.
- The UI highlights the invalid rows and columns.

**Common errors:**
- Missing mandatory columns.
- Invalid JSON in Headers / Body.
- Duplicate Ref_IDs.

## Known Limitations

- Nested authentication flows are not supported.
- GraphQL APIs are not supported (REST only).
- Response schema validation is key-based, not full JSON schema.

## Roadmap

- [ ] Swagger/OpenAPI import
- [ ] Response schema validation
- [ ] CI/CD-ready GitHub Actions export
- [ ] Multi-environment support (QA/UAT/PROD)

## Security Note

- Uploaded XLSX files are processed in-memory.
- No API credentials are persisted.
- Generated tokens exist only in runtime artifacts.

## Troubleshooting

-   **"npm error code ENOENT"**: ensure you are inside the `frontend` folder before running `npm` commands.
-   **Backend won't start?**: Run `fix_server.bat` in the root directory to attempt an automatic repair of the python environment.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---
*Built with ❤️ for API Developers.*
