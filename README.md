# API Factory

**Build APIs Beautifully.**
The automated tool that turns your Excel sheets into production-ready Postman Collections and Pytest scripts.

---

## 🌟 Quick Start
1.  **Click on the link**: https://xlsx-to-api-generator-frontend.vercel.app/
2.  **Get Template**: Click the button in the app to download the `.xlsx` file.
3.  **Fill Data**: Open it in Excel and add your API details.
4.  **Generate**: detailed instructions below.

---

## � The Excel Manual (Complete Guide)

The magic happens in your Excel file. Here is exactly how to fill it.

### 1. The "APIs" Sheet (Main)
This sheet contains your API definitions. Each row is one request.

| Column Name | What it does | Data Type | Example |
| :--- | :--- | :--- | :--- |
| **Ref ID** | A unique ID for this request. | Text | `AUTH-001`, `USER-005` |
| **Module/Feature** | Creates a **Folder** in Postman. | Text | `Authentication`, `Products` |
| **API Name** | The name shown in the collection. | Text | `Login`, `Get Item Details` |
| **HTTP Method** | The verb (GET/POST/PUT/DELETE). | Text | `POST` |
| **Endpoint URL** | The path (or full URL). | Text | `/api/v1/login` or `https://api.com/user` |
| **Headers Required** | Custom headers (optional). | JSON | `{"Content-Type": "application/json"}` |
| **Request Payload** | The body you send to the server. | JSON | `{"email": "user@test.com", "pass": "123"}` |
| **URL Params** | Query parameters (after `?`). | JSON | `{"page": 1, "limit": 10}` |
| **Expected Response** | What the server *should* return. | JSON | `{"status": "success", "id": 123}` |
| **Auth Scope** | How to handle login. | Text | `Collection` (uses global token) or blank. |
| **Token Variable** | Variable name to *store* a token in. | Text | `authToken` (see Token Logic below) |
| **Is Token Generator** | Is this a Login API? | `TRUE`/`FALSE` | `TRUE` |

### 2. The "Environments" Sheet (Global Variables)
Use this sheet to define variables that you reuse everywhere (like your base URL).

| Variable | Value | Usage in APIs Sheet |
| :--- | :--- | :--- |
| `base_url` | `https://api.mysite.com` | The system automatically uses this. |
| `username` | `admin_user` | Use `{{username}}` in your payload. |
| `password` | `secret_pass` | Use `{{password}}` in your payload. |

---

## 🧠 Smart Features

### 1. Variables (`{{...}}`)
You can use variables anywhere (in URLs, Headers, or Body).
*   **Example**: define `userId` in the Environments sheet.
*   **Usage**: `/api/users/{{userId}}`

### 2. Authentication Logic (How it works)
We handle login for you automatically.

*   **Step 1**: Create a **Login API** row.
    *   Set **Is Token Generator** to `TRUE`.
    *   Set **Token Variable** to `myToken`.
*   **Step 2**: The system will run this API first, extract the token from the response, and save it as `{{myToken}}`.
*   **Step 3**: For other APIs, set **Headers** to `{"Authorization": "Bearer {{myToken}}"}` OR just set **Auth Scope** to `Collection`.

### 3. Data Types
*   **JSON**: Must be valid JSON (keys in double quotes `"`).
    *   ✅ Correct: `{"key": "value"}`
    *   ❌ Wrong: `{key: "value"}` (missing quotes)
*   **Text**: Simple plain text.

---

## 🚀 Advanced Features

### 1. Consolidated Reporting (Master Report)
You don't need to fit everything into one file!
*   **How it works**: Run `pytest` on multiple API folders (e.g., `pytest tests/api1`, then `pytest tests/api2`).
*   **The Magic**: The system **merges** the results into a single `index.html` Master Report.
*   The report grows as you test more APIs.

### 2. Source Code in Reports
Why guess what happened?
*   Open the HTML Report.
*   Click on any test case.
*   Click the **"Code"** tab.
*   **See the exact Python code** that ran for that test!

### 3. Smart "About"
*   Click the **(i)** icon in the report header to see version info and details.

---

## ❓ FAQ

### Can I copy-paste a full browser URL?
**Yes!** If you paste `https://google.com/search?q=test` into **Endpoint URL**, the system is smart enough to extract the base URL and parameters automatically.

### What if my JSON is invalid?
The system will tell you exactly which row has the error. Just fix the quotes or commas in Excel and re-upload.

---

---

## ☁️ Deploy to GitHub

Want to see your reports online?

1.  **Push your code** to GitHub.
2.  Go to your Repository **Settings** > **Pages**.
3.  Under **Build and deployment**, select **Source**: `GitHub Actions`.
    *   *(Or if using the legacy method, select `gh-pages` branch if created by the action)*. 
    *   *Note: Our workflow uses `upload-pages-artifact`, so normally you just go to Settings > Pages and ensure strict security is set or just wait for the Action to run.*
    *   Actually, usually you just need to enable Pages.
    *   **Simpler Instruction**: Go to **Settings** > **Pages**. Set **Source** to **GitHub Actions**.
4.  The "Deploy Report to Pages" workflow will run automatically.
5.  Your report will be live at: `https://<username>.github.io/<repo-name>/`

---
*Powered by API Factory.*
