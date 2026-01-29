
import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
import time

# Force flush
import functools
print = functools.partial(print, flush=True)

def verify_workflow():
    print("Staritng verify_workflow...")
    
    # Debug file
    try:
        with open("verify_start.txt", "w") as f:
            f.write(f"Started at {time.time()}")
    except Exception as e:
        print(f"Failed to write debug file: {e}")

    # Add backend to path
    backend_path = os.path.dirname(os.path.abspath(__file__))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    print(f"Backend path: {backend_path}")

    try:
        from services.parser import parse_xlsx
        from services.pytest_generator import generate_pytest_project
        print("Imports successful.")
    except Exception as e:
        print(f"Import failed: {e}")
        return

    work_dir = Path("verification_work_dir")
    try:
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir()
        print(f"Work dir created: {work_dir}")
    except Exception as e:
        print(f"Failed to create work dir: {e}")
        return
    
    # 1. Load Sample Excel
    xlsx_path = Path("Suprabhat_APIs_v4.xlsx")
    if not xlsx_path.exists():
        print(f"Error: {xlsx_path} not found. Creating dummy.")
        # Create dummy logic... or just fail?
        # Let's try to fail gracefully
        return

    print(f"Reading {xlsx_path}...")
    with open(xlsx_path, "rb") as f:
        content = f.read()

    # 2. Parse
    print("Parsing...")
    api_data, warnings = parse_xlsx(content)
    if warnings:
        print("Warnings:", warnings)
    
    if not api_data:
        print("Parsing failed.")
        return
    
    print(f"Parsed {len(api_data.get('apis', []))} APIs.")

    # 3. Generate
    print("Generating Pytest Project...")
    zip_path_str = generate_pytest_project(api_data, str(work_dir))
    zip_path = Path(zip_path_str)
    
    print(f"Generated: {zip_path}")

    # 4. Unzip
    extract_dir = work_dir / "pytest_extracted"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted to: {extract_dir}")
    
    # 5. Run Pytest
    print("Running Pytest...")
    test_dir = extract_dir
    
    # Check if report_template.py exists
    if (test_dir / "report_template.py").exists():
        print("Confirmed: report_template.py exists.")
    else:
        print("ERROR: report_template.py MISSING.")

    # Run pytest
    # We use subprocess to run pytest in that directory
    cmd = [sys.executable, "-m", "pytest"]
    print(f"Executing: {cmd} in {test_dir}")
    
    try:
        # TIMEOUT added to prevent hanging
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=30 # 30 seconds timeout
        )
        print("Pytest Finished.")
        print("Pytest Output (stdout):")
        print(result.stdout)
        print("Pytest Output (stderr):")
        print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Pytest timed out! (Likely due to missing backend server)")
        # Proceed to check artifacts anyway, maybe it generated report before hanging? 
        # Unlikely with pytest hooks.
        # But wait, pytest hooks run after each test. sessionfinish runs at end.
        # If it hangs on a test, sessionfinish won't run.
        # We need skipped/mocked tests for report verification if server is down.
    except Exception as e:
        print(f"Subprocess failed: {e}")
    
    # 6. Verify Artifacts
    if (test_dir / "index.html").exists():
        print("SUCCESS: index.html generated!")
    else:
        print("FAILURE: index.html NOT found.")
        
    if (test_dir / "report.json").exists():
        print("SUCCESS: report.json generated!")
    else:
        print("FAILURE: report.json NOT found.")

if __name__ == "__main__":
    verify_workflow()
