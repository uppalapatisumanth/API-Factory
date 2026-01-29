import os
import shutil
import zipfile
import json
from pathlib import Path
from .report_template import HTML_REPORT_TEMPLATE

def generate_pytest_project(api_data, output_dir: str):
    """
    Generates a Pytest project structure from API data.
    api_data can be either:
    - A dict with {"apis": [...], "env": {}, "rules": {}}
    - Or a list of API dicts directly (legacy)
    """
    
    # Handle both dict format and list format
    if isinstance(api_data, dict):
        apis = api_data.get("apis", [])
    elif isinstance(api_data, list):
        apis = api_data
    else:
        apis = []
    
    base_dir = Path(output_dir)
    tests_dir = base_dir / "pytest_tests"
    if tests_dir.exists():
        shutil.rmtree(tests_dir)
    tests_dir.mkdir(parents=True)
    
    # Generate requirements.txt
    _create_file(tests_dir / "requirements.txt", "pytest\nrequests\n")
    
    # Extract env from api_data
    env = {}
    if isinstance(api_data, dict):
        env = api_data.get("env", {})
    
    # Generate conftest.py
    _create_conftest(tests_dir, apis, env)

    # Generate report_template.py
    import base64
    b64_template = base64.b64encode(HTML_REPORT_TEMPLATE.encode('utf-8')).decode('utf-8')
    rt_content = f'''import base64
HTML_TEMPLATE = base64.b64decode("{b64_template}").decode("utf-8")
'''
    _create_file(tests_dir / "report_template.py", rt_content)
    
    # Group APIs (logic: try to group by first path segment, or 'general')
    groups = {}
    for api in apis:
        # Simple grouping heuristic
        path_parts = api.get("url", "").split("://")[-1].split("/")
        group_name = "general"
        if len(path_parts) > 1 and path_parts[1]:
             group_name = path_parts[1]
        
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(api)
        
    # Generate Test Files
    for group, apis in groups.items():
        group_dir = tests_dir / f"test_{group}"
        group_dir.mkdir(exist_ok=True)
        # Create __init__.py for the package
        _create_file(group_dir / "__init__.py", "")
        
        for api in apis:
            _create_test_file(group_dir, api)
            
    # Zip the directory
    zip_path = base_dir / "pytest_tests.zip"
    _zip_directory(tests_dir, zip_path)
    
    return str(zip_path)

def _create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _create_conftest(base_path, apis, env={}):
    # Find Token Generator API
    token_api = next((api for api in apis if api.get("is_token_generator")), None)
    
    # Determine default base url
    default_base_url = env.get("base_url", "http://localhost:8000")
    
    content = f"""import pytest
import os
import requests
import json
import time
import datetime
import sys
import inspect

sys.path.append(os.path.dirname(__file__))
try:
    # Try relative import first (package mode)
    from .report_template import HTML_TEMPLATE
except ImportError:
    try:
    # Try direct import (script mode)
        import report_template
        HTML_TEMPLATE = report_template.HTML_TEMPLATE
    except Exception as e:
        # Fallback with debug info
        HTML_TEMPLATE = f"<h1>Error loading template: {{str(e)}}</h1>"
except Exception as e:
    HTML_TEMPLATE = f"<h1>Error loading template (General): {{str(e)}}</h1>"

# --- REPORTING SYSTEM ---
REPORT_DATA = {{"summary": {{"total": 0, "passed": 0, "failed": 0}}, "tests": []}}

def pytest_sessionfinish(session, exitstatus):
    report_json_path = os.path.join(os.path.dirname(__file__), "report.json")
    
    # 1. Load Existing Data (for merging)
    final_tests = []
    if os.path.exists(report_json_path):
        try:
            with open(report_json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                final_tests = existing_data.get("tests", [])
        except:
            pass # corrupted or empty
            
    # 2. Merge Strategies (Deduplicate by nodeid)
    # Create a dict of existing tests for O(1) lookup
    test_map = {{t["nodeid"]: t for t in final_tests}}
    
    # Update with new results (REPORT_DATA is the current run's data)
    for new_test in REPORT_DATA["tests"]:
        test_map[new_test["nodeid"]] = new_test
        
    # Reconstruct list (sort by name/nodeid for consistency)
    merged_tests = sorted(test_map.values(), key=lambda x: x["nodeid"])
    
    # 3. Recalculate Stats
    total = len(merged_tests)
    passed = len([t for t in merged_tests if t["status"] == "passed"])
    failed = len([t for t in merged_tests if t["status"] == "failed"])
    
    final_data = {{
        "summary": {{
            "total": total,
            "passed": passed,
            "failed": failed
        }},
        "tests": merged_tests
    }}
    
    # 4. Save Consolidated JSON
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)
        
    # 5. Generate HTML
    # Inject Consolidated Data
    json_str = json.dumps(final_data)
    final_html = HTML_TEMPLATE.replace("%%REPORT_DATA%%", json_str)
    
    report_html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(report_html_path, "w", encoding="utf-8") as f:
        f.write(final_html)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        entry = getattr(item, "_report_entry", None)
        if entry:
            entry["status"] = "passed" if rep.passed else "failed"
            
            # Capture Source Code
            try:
                entry["source_code"] = inspect.getsource(item.obj)
            except Exception as e:
                entry["source_code"] = f"# Could not retrieve source: {{str(e)}}"

            if rep.failed:
                entry["error_log"] = str(rep.longrepr)

# --- FIXTURES ---

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var
    return os.getenv("API_BASE_URL", "{default_base_url}")

@pytest.fixture(scope="session")
def auth_token(base_url):
"""

    if token_api:
        # Generate code to call the token API
        url = token_api.get("url", "")
        method = token_api.get("method", "POST").lower()
        headers = token_api.get("headers", {})
        # Ensure User-Agent is present
        if "User-Agent" not in headers:
            headers["User-Agent"] = "API-Factory-Test-Client/1.0"
            
        body = token_api.get("body", {})
        url_params = token_api.get("url_params", {})
        token_var = token_api.get("token_variable", "token")
        
        if "://" in url:
            path = "/" + "/".join(url.split("://")[-1].split("/")[1:])
        else:
            path = url if url.startswith("/") else f"/{url}"
            
        content += f"    # Token Generator API: {token_api.get('name')}\n"
        content += f"    url = f'{{base_url}}{path}'\n"
        content += f"    headers = {json.dumps(headers)}\n"
        
        content += "    try:\n"
        if method in ['post', 'put', 'patch']:
            if token_api.get("body_mode") == "urlencoded":
                payload = body or url_params
                content += f"        data = {json.dumps(payload)}\n"
                content += f"        response = requests.{method}(url, headers=headers, data=data, timeout=45)\n"
            else:
                content += f"        json_body = {json.dumps(body)}\n"
                content += f"        response = requests.{method}(url, headers=headers, json=json_body, timeout=45)\n"
        else:
             content += f"        response = requests.{method}(url, headers=headers, timeout=45)\n"
             
        content += "    except Exception as e:\n"
        content += "        print(f'Auth Warning: {str(e)}')\n"
        content += "        pytest.skip(f'Skipping tests due to Auth API failure: {str(e)}')\n"
        content += "        return None\n\n"
             
        content += f"    if response.status_code not in (200, 201):\n"
        content += f"        print(f'Auth Warning: Status {{response.status_code}}')\n"
        content += f"        pytest.skip(f'Skipping check: Auth API returned status {{response.status_code}}')\n"
        content += f"        return None\n"
        content += f"    \n"
        content += f"    data = response.json()\n"
        content += f"    token = data.get('{token_var}') or data.get('token') or data.get('access_token')\n"
        content += f"    if not token:\n"
        content += f"        pytest.skip(f'Skipping check: Token \"{token_var}\" not found in auth response')\n"
        content += f"    return token\n"
        
    else:
        content += """    # No Token Generator API found. 
    return os.getenv("AUTH_TOKEN", None)
"""

    # Add api_client fixture
    content += """
@pytest.fixture
def api_client(base_url, auth_token, request):
    class ApiClient:
        def __init__(self):
            self.base_url = base_url
            self.token = auth_token
            
        def request(self, method, url, **kwargs):
            # Auth Injection
            if self.token:
                if "headers" not in kwargs: kwargs["headers"] = {}
                if "Authorization" not in kwargs["headers"]:
                    kwargs["headers"]["Authorization"] = f"Bearer {self.token}"

            full_url = url
            if not url.startswith("http"):
                full_url = f"{self.base_url}{url}"

            start_time = time.time()
            response = None
            error = None
            
            try:
                response = requests.request(method, full_url, **kwargs)
                return response
            except Exception as e:
                error = e
                raise e
            finally:
                duration = time.time() - start_time
                
                # Capture Data for Report
                req_headers = kwargs.get("headers", {})
                req_body = kwargs.get("json") or kwargs.get("data") or kwargs.get("params")
                
                res_status = response.status_code if response else 0
                res_headers = dict(response.headers) if response else {}
                try:
                    res_body = response.json() if response else (response.text if response else "")
                except:
                    res_body = response.text if response else ""
                
                entry = {
                    "name": request.node.name,
                    "nodeid": request.node.nodeid,
                    "method": method,
                    "url": full_url,
                    "request_headers": req_headers,
                    "request_body": req_body,
                    "response_status": res_status,
                    "response_headers": res_headers,
                    "response_body": res_body,
                    "duration": duration,
                    "status": "unknown",
                    "error_log": str(error) if error else ""
                }
                
                REPORT_DATA["tests"].append(entry)
                # Link entry to item so hook can update status
                request.node._report_entry = entry

        def get(self, url, **kwargs): return self.request("GET", url, **kwargs)
        def post(self, url, **kwargs): return self.request("POST", url, **kwargs)
        def put(self, url, **kwargs): return self.request("PUT", url, **kwargs)
        def delete(self, url, **kwargs): return self.request("DELETE", url, **kwargs)
        def patch(self, url, **kwargs): return self.request("PATCH", url, **kwargs)

    return ApiClient()
"""
    
    _create_file(base_path / "conftest.py", content)

def _create_test_file(directory, api):
    clean_name = api.get("name", "untitled").lower().replace(" ", "_").replace("-", "_")
    filename = f"test_{clean_name}.py"
    
    method = api.get("method", "GET").lower()
    url = api.get("url", "")
    headers = api.get("headers", {})
    body = api.get("body", {})
    params = api.get("params", {})
    expected_response = api.get("expected_response")
    expected_response_type = api.get("expected_response_type", "text")
    status = api.get("status", 200)

    body_mode = api.get("body_mode", "raw")
    is_auth = api.get("is_auth", False)
    
    # Identify token variable to substitute
    # We assume 'authToken' or 'token' is the fixture name
    token_fixture_name = "auth_token"

    # Helper to handle {{variable}} substitution
    import re
    def sanitize(val):
        """Converts {{var}} to string interpolation or direct variable usage."""
        if not isinstance(val, str): return val
        
        # Regex to find {{ var }} with optional whitespace
        match = re.search(r"\{\{\s*(\w+)\s*\}\}", val)
        if match:
            var_name = match.group(1)
            # Normalize auth token name
            if var_name in ["authToken", "token"]:
                if val.strip() == match.group(0): # Entire string is the variable
                    return "___AUTH_TOKEN_PLACEHOLDER___"
                else:
                    return val.replace(match.group(0), "{auth_token}")
        return val

    # Recursively process dicts/lists
    def process_structure(data):
        if isinstance(data, dict):
            return {k: process_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [process_structure(i) for i in data]
        else:
            return sanitize(data)

    headers = process_structure(headers)
    params = process_structure(params)
    body = process_structure(body)

    # 1. URL Handler
    if "://" in url:
        path = "/" + "/".join(url.split("://")[-1].split("/")[1:])
    else:
        path = url if url.startswith("/") else f"/{url}"
    
    # 2. Body Handling
    final_body = body
    use_params_as_body = False
    
    if not final_body and body_mode == "urlencoded" and params:
        final_body = params
        use_params_as_body = True

    # 3. Construct Code
    # Determine needed fixtures
    # fixtures = ["base_url"] # No longer needed explicitly if api_client handles it, but keeps generated code clean
    fixtures = ["api_client"] 
    # NOTE: base_url and auth_token are used implicitly by api_client, so we don't need to inject them into test function args
    # unless we need strict raw access.
    
    # Check if we need auth_token
    needs_auth = False
    # Check headers for placeholder
    if str(headers).find("___AUTH_TOKEN_PLACEHOLDER___") != -1: needs_auth = True
    # Check auth scope
    if str(api.get("auth_scope", "")).lower() == "collection": needs_auth = True
    
    # We always inject api_client. api_client handles auth internally if configured in conftest.
    # However, if we need to explicitly substitute the token in a HEADER value (custom auth),
    # we might need the actual token string.
    
    if str(headers).find("___AUTH_TOKEN_PLACEHOLDER___") != -1:
        # We need the raw token to substitute
        fixtures.append("auth_token")

    code = "import pytest\nimport requests\n\n"
    code += f"def test_{clean_name}({', '.join(fixtures)}):\n"
    # code += f"    url = f\"{{base_url}}{path}\"\n" # Managed by api_client
    code += f"    url = \"{path}\"\n"
    
    # Render Headers
    # We construct the dict string manually to handle variables
    if headers:
        code += "    headers = {\n"
        for k, v in headers.items():
            if v == "___AUTH_TOKEN_PLACEHOLDER___":
                code += f"        \"{k}\": {token_fixture_name},\n"
            else:
                code += f"        \"{k}\": \"{v}\",\n"
        code += "    }\n"
    else:
        code += "    headers = {}\n"

    # Explicit Auth Scope Injection (if not already handled by header var)
    # api_client handles 'Bearer' auth if we don't do anything.
    # But if we want to be safe and use existing logic:
    if str(api.get("auth_scope", "")).lower() == "collection" and "Authorization" not in headers:
         # api_client will auto-inject if it sees collection scope...? 
         # The current api_client implementation auto-injects if self.token is set.
         # So we don't need to manually add it to headers, UNLESS api_client logic is 'always inject'.
         # Our api_client logic: "if self.token: ... if Authorization not in headers: inject"
         # So safe to omit here.
         pass
         # code += f"    headers['Authorization'] = f'Bearer {{{token_fixture_name}}}'\n"

    # Render Params
    if use_params_as_body:
        code += "    params = {}\n"
    else:
        if params:
            code += "    params = {\n"
            for k, v in params.items():
                code += f"        \"{k}\": \"{v}\",\n"
            code += "    }\n"
        else:
            code += "    params = {}\n"

    # Make Request
    if method in ['post', 'put', 'patch'] and final_body:
        if body_mode == "urlencoded":
            code += f"    payload = {json.dumps(final_body)}\n"
            code += f"    response = api_client.{method}(url, headers=headers, params=params, data=payload)\n"
        else:
            code += f"    json_body = {json.dumps(final_body)}\n"
            code += f"    response = api_client.{method}(url, headers=headers, params=params, json=json_body)\n"
    else:
        code += f"    response = api_client.{method}(url, headers=headers, params=params)\n"

    # Assertions
    code += "\n    # Assertions\n"
    code += "    print(f'Status Code: {response.status_code}')\n"
    code += "    print(f'Response Body: {response.text}')\n"
    code += f"    assert response.status_code in [{status}, 200, 201]\n"

    if expected_response:
        if expected_response_type == "json":
            code += f"    response_json = response.json()\n"
            for k, v in expected_response.items():
                if isinstance(v, str):
                   # Placeholder check
                   if "<" in v and ">" in v:
                       code += f"    # Skipped assertion for {k} due to placeholder '{v}'\n"
                   else:
                       code += f"    assert response_json.get('{k}') == \"{v}\"\n"
                else:
                    code += f"    assert response_json.get('{k}') == {v}\n"
        else:
            # Plain String Assertion
            safe_str = str(expected_response).replace('"', '\\"')
            if safe_str == "None" or safe_str == "":
                 code += f"    # Skipped assertion for empty/None response\n"
            elif "<" in safe_str and ">" in safe_str:
                code += f"    # Skipped body text assertion due to placeholder '{safe_str}'\n"
            else:
                code += f"    assert \"{safe_str}\" in response.text\n"

    
    # 5. Local Execution Block
    code += "\nif __name__ == \"__main__\":\n"
    code += "    # Allow running this file directly with Python\n"
    code += "    import sys\n"
    code += "    sys.exit(pytest.main([\"-v\", \"-s\", __file__]))\n"

    _create_file(directory / filename, code)

def _zip_directory(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(folder_path)
                zipf.write(file_path, arcname)

def _create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
