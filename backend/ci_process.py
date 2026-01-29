import sys
import os
from pathlib import Path

# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services import parser, pytest_generator

def run_ci_gen(file_path="sample_api.xlsx", output_dir="ci_output"):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        # If sample doesn't exist, try to generate it using generate_sample.py logic? 
        # Or just fail. Let's assume it exists or user provides it.
        # Check if we can find it in current dir
        if os.path.exists(os.path.join("backend", file_path)):
             file_path = os.path.join("backend", file_path)
        else:
             sys.exit(1)

    print(f"Loading {file_path}...")
    with open(file_path, "rb") as f:
        content = f.read()
    
    print("Parsing...")
    api_data, warnings = parser.parse_xlsx(content)
    for w in warnings:
        print(f"WARN: {w}")
        
    print(f"Generating tests to {output_dir}...")
    
    out_path = Path(output_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True)
        
    pytest_generator.generate_pytest_project(api_data, str(out_path))
    print("Done. Tests generated in ci_output/pytest_tests")

if __name__ == "__main__":
    # If args provided
    fpath = "sample_api.xlsx"
    if len(sys.argv) > 1:
        fpath = sys.argv[1]
    run_ci_gen(fpath)
