from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import shutil
import json
import traceback
from pathlib import Path
from services import parser, postman_generator, pytest_generator

router = APIRouter(prefix="/api", tags=["processing"])

# Simple in-memory storage for task state
# Structure: { task_id: { "status": "pending"|"processing"|"completed"|"failed", "logs": [], "artifacts": {} } }
TASKS = {}
ARTIFACTS_DIR = Path("artifacts_storage")
TASKS_FILE = ARTIFACTS_DIR / "tasks.json"

if not ARTIFACTS_DIR.exists():
    try:
        ARTIFACTS_DIR.mkdir()
    except:
        pass

def load_tasks():
    global TASKS
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r") as f:
                TASKS = json.load(f)
        except Exception:
            TASKS = {}
    else:
        TASKS = {}
        
def save_tasks():
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(TASKS, f, indent=4)
    except Exception as e:
        print(f"Failed to save tasks: {e}")

# Load tasks on startup
load_tasks()

def process_file_task(task_id: str, file_content: bytes, filename: str):
    TASKS[task_id]["status"] = "processing"
    TASKS[task_id]["logs"].append("Started processing file...")
    save_tasks()

    try:
        # Step 1: Parse
        TASKS[task_id]["logs"].append("Parsing XLSX file...")
        api_data, warnings = parser.parse_xlsx(file_content)
        
        for w in warnings:
            TASKS[task_id]["logs"].append(f"WARNING: {w}")
            
        # api_data is now { "apis": [], ... }
        if not api_data or not api_data.get("apis"):
            TASKS[task_id]["status"] = "failed"
            TASKS[task_id]["logs"].append("No valid API definitions found in file.")
            save_tasks()
            return

        api_count = len(api_data["apis"])
        TASKS[task_id]["logs"].append(f"Found {api_count} API definitions.")
        TASKS[task_id]["api_preview"] = api_data["apis"]
        save_tasks()

        # Prepare specific artifact directory
        task_dir = ARTIFACTS_DIR / task_id
        task_dir.mkdir(exist_ok=True)

        # Step 2: Generate Postman Collection
        TASKS[task_id]["logs"].append("Generating Postman Collection...")
        collection = postman_generator.generate_postman_collection(api_data, collection_name=f"Generated from {filename}")
        postman_path = task_dir / "postman_collection.json"
        with open(postman_path, "w") as f:
            json.dump(collection, f, indent=4)
        TASKS[task_id]["artifacts"]["postman"] = str(postman_path)

        # Step 3: Generate Pytest Code
        TASKS[task_id]["logs"].append("Generating Pytest structure...")
        pytest_path = pytest_generator.generate_pytest_project(api_data, output_dir=str(task_dir))
        TASKS[task_id]["artifacts"]["pytest"] = str(pytest_path)

        TASKS[task_id]["status"] = "completed"
        TASKS[task_id]["logs"].append("Processing finished successfully.")
        save_tasks()

    except Exception as e:
        TASKS[task_id]["status"] = "failed"
        TASKS[task_id]["logs"].append(f"ERROR: {str(e)}")
        save_tasks()
        traceback.print_exc()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    log_file = r"d:\ais\api\backend\backend_debug.log"
    try:
        with open(log_file, "a") as f:
            f.write(f"\n[UPLOAD] Starting upload for file: {file.filename}\n")
            f.write(f"[UPLOAD] CWD: {os.getcwd()}\n")
            
        if not file.filename.endswith(".xlsx"):
             raise HTTPException(status_code=400, detail="Invalid file format. Please upload .xlsx")
              
        content = await file.read()
        
        with open(log_file, "a") as f:
            f.write(f"[UPLOAD] File read successfully. Size: {len(content)} bytes\n")

        task_id = str(uuid.uuid4())
        
        TASKS[task_id] = {
            "status": "pending",
            "logs": ["File uploaded. Waiting for processing..."],
            "artifacts": {}
        }
        save_tasks()
        
        background_tasks.add_task(process_file_task, task_id, content, file.filename)
        
        with open(log_file, "a") as f:
            f.write(f"[UPLOAD] Task created: {task_id}\n")
            
        return {"task_id": task_id, "message": "Upload successful, processing started."}
    except HTTPException:
        raise
    except Exception as e:
        err_msg = traceback.format_exc()
        try:
            with open(log_file, "a") as f:
                f.write(f"[UPLOAD ERROR] {err_msg}\n")
        except:
            pass
        print(err_msg)
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id, 
        "status": TASKS[task_id]["status"], 
        "logs": TASKS[task_id]["logs"],
        "api_preview": TASKS[task_id].get("api_preview", []),
        "artifacts_ready": list(TASKS[task_id]["artifacts"].keys())
    }

@router.get("/download/{task_id}/{file_type}")
async def download_file(task_id: str, file_type: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
        
    artifacts = TASKS[task_id].get("artifacts", {})
    if file_type not in artifacts:
        raise HTTPException(status_code=404, detail=f"Artifact '{file_type}' not found or not ready.")
        
    file_path = artifacts[file_type]
    filename = os.path.basename(file_path)
    
    media_type = "application/json" if file_type == "postman" else "application/zip"
    
    return FileResponse(file_path, media_type=media_type, filename=filename)


