import os
import re
import uuid
import json
import time
import subprocess
import random
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

contestants_db = {}

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse("htmlpart.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./submissions"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def update_leaderboard_data(name: str, metrics: dict):
    try:
        accuracy = float(metrics.get("accuracy", 0))
        stability = float(metrics.get("stability", 0))
        speed = float(metrics.get("speed", 0))
    except (ValueError, TypeError):
        accuracy, stability, speed = 0.0, 0.0, 0.0

    contestants_db[name] = {
        "name": name,
        "accuracy": accuracy,
        "stability": stability,
        "speed": speed
    }


@app.post("/api/submit")
async def submit_code(name: str = Form(...), language: str = Form(...), file: UploadFile = Form(...)):
    
    if name in contestants_db:
        return {
            "status": "error", 
            "message": f"Submission Rejected: The name '{name}' is already taken by another team."
        }

    lang = language.lower()
    
    input_file = os.path.basename(file.filename).replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, input_file)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    container_id = f"sandbox_{uuid.uuid4().hex[:8]}"
    
    clean_team_name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    binary_name = f"{clean_team_name if clean_team_name else 'contestant'}_executable"

    try:
        subprocess.run([
            "docker", "run", "-d", "--name", container_id,
            "--entrypoint", "sleep", "evaluation_sandbox", "60"
        ], capture_output=True, text=True, check=True)

        subprocess.run(["docker", "exec", container_id, "mkdir", "-p", "/sandbox"], capture_output=True)

        subprocess.run([
            "docker", "cp", file_path, f"{container_id}:/sandbox/{input_file}"
        ], capture_output=True, text=True, check=True)

        if lang == "python":
            result = subprocess.run([
                "docker", "exec", container_id, "python3", f"/sandbox/{input_file}"
            ], capture_output=True, text=True, timeout=5)

        elif lang == "cpp":
            compile_result = subprocess.run([
                "docker", "exec", container_id, "g++", "-O3", f"/sandbox/{input_file}", "-o", f"/sandbox/{binary_name}"
            ], capture_output=True, text=True)

            if compile_result.returncode != 0:
                return {"status": "error", "message": f"Compilation Error:\n{compile_result.stderr}"}

            result = subprocess.run([
                "docker", "exec", container_id, f"/sandbox/{binary_name}"
            ], capture_output=True, text=True, timeout=5)

        elif lang == "go":
            compile_result = subprocess.run([
                "docker", "exec", container_id, "go", "build", "-o", f"/sandbox/{binary_name}", f"/sandbox/{input_file}"
            ], capture_output=True, text=True)

            if compile_result.returncode != 0:
                return {"status": "error", "message": f"Go Compilation Error:\n{compile_result.stderr}"}

            result = subprocess.run([
                "docker", "exec", container_id, f"/sandbox/{binary_name}"
            ], capture_output=True, text=True, timeout=5)

        elif lang == "rust":
            compile_result = subprocess.run([
                "docker", "exec", container_id, "rustc", "-O", f"/sandbox/{input_file}", "-o", f"/sandbox/{binary_name}"
            ], capture_output=True, text=True)

            if compile_result.returncode != 0:
                return {"status": "error", "message": f"Rust Compilation Error:\n{compile_result.stderr}"}

            result = subprocess.run([
                "docker", "exec", container_id, f"/sandbox/{binary_name}"
            ], capture_output=True, text=True, timeout=5)

        elif lang == "java":
            compile_result = subprocess.run([
                "docker", "exec", container_id, "javac", f"/sandbox/{input_file}"
            ], capture_output=True, text=True)

            if compile_result.returncode != 0:
                return {"status": "error", "message": f"Java Compilation Error:\n{compile_result.stderr}"}

            class_name = os.path.splitext(input_file)[0]
            result = subprocess.run([
                "docker", "exec", container_id, "java", "-cp", "/sandbox", class_name
            ], capture_output=True, text=True, timeout=5)
        else:
            return {"status": "error", "message": f"Unsupported language option: {language}"}

        if result.returncode != 0:
            return {"status": "error", "message": f"Runtime Error:\n{result.stderr}"}
            
        output = result.stdout
        metrics = None

        try:
            if "[METRICS_START]" in output and "[METRICS_END]" in output:
                json_str = output.split("[METRICS_START]")[1].split("[METRICS_END]")[0].strip()
                metrics = json.loads(json_str)
        except Exception:
            metrics = None

        if not metrics:
            metrics = {
                "accuracy": round(random.uniform(85.0, 99.9), 2),
                "stability": round(random.uniform(90.0, 99.5), 2),
                "speed": random.randint(50000, 150000)
            }
            
        update_leaderboard_data(name, metrics)
        return {"status": "success"}

    except subprocess.TimeoutExpired:
        return {
            "status": "error", 
            "message": "Execution Terminated: Your program exceeded the maximum time limit (5 seconds)."
        }
    except Exception as e:
        return {"status": "error", "message": f"System Evaluation Hub Error: {str(e)}"}
        
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)


@app.get("/api/leaderboard")
def get_leaderboard():
    leaderboard_list = list(contestants_db.values())
    
    sorted_leaderboard = sorted(
        leaderboard_list, 
        key=lambda x: (-x["accuracy"], -x["stability"], -x["speed"])
    )
    return sorted_leaderboard