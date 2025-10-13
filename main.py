# main.py
# Simple FastAPI service that compiles/runs Python, C++ and Java code.
# Request JSON:
# {
#   "language": "python" | "cpp" | "java",
#   "code": "<source code>",
#   "stdin": "<optional stdin, can contain newlines>",
#   "timeout": 5   # optional, seconds for program run
# }
#
# Response JSON:
# {
#   "stdout": "...",
#   "stderr": "...",
#   "compile_output": "...",   # non-empty for compile errors (cpp/java)
#   "exit_code": 0,
#   "timed_out": false
# }

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os, shutil, subprocess, sys

app = FastAPI(title="Multi-language Code Runner")

# Allow CORS for testing. Replace "*" with specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunReq(BaseModel):
    language: str
    code: str
    stdin: str = ""
    timeout: int = 5

@app.get("/")
def home():
    return {"message": "Multi-language Code Runner is up."}

@app.post("/run")
async def run(req: RunReq):
    lang = req.language.strip().lower()
    code = req.code
    stdin = req.stdin or ""
    timeout = max(1, min(req.timeout, 30))  # clamp timeout between 1 and 30s

    if lang not in ("python", "cpp", "java"):
        raise HTTPException(status_code=400, detail="language must be one of: python, cpp, java")

    # Create temporary workspace
    tmpdir = tempfile.mkdtemp(prefix="code-run-")
    try:
        if lang == "python":
            src_name = "main.py"
            src_path = os.path.join(tmpdir, src_name)
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Run python script
            try:
                proc = subprocess.run(
                    [sys.executable, src_name],
                    cwd=tmpdir,
                    input=stdin,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
                return {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "compile_output": "",
                    "exit_code": proc.returncode,
                    "timed_out": False
                }
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "Execution timed out", "compile_output": "", "exit_code": -1, "timed_out": True}

        elif lang == "cpp":
            src_name = "main.cpp"
            exe_name = "main_exec"
            src_path = os.path.join(tmpdir, src_name)
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            try:
                comp = subprocess.run(
                    ["g++", src_name, "-O2", "-std=gnu++17", "-o", exe_name],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    text=True
                )
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "", "compile_output": "Compilation timed out", "exit_code": -1, "timed_out": True}

            if comp.returncode != 0:
                # compile error
                return {"stdout": "", "stderr": "", "compile_output": comp.stderr, "exit_code": comp.returncode, "timed_out": False}

            # Run executable
            exe_path = os.path.join(tmpdir, exe_name)
            try:
                proc = subprocess.run(
                    [f"./{exe_name}"],
                    cwd=tmpdir,
                    input=stdin,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
                return {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "compile_output": "",
                    "exit_code": proc.returncode,
                    "timed_out": False
                }
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "Execution timed out", "compile_output": "", "exit_code": -1, "timed_out": True}

        elif lang == "java":
            # We will use class name Main
            src_name = "Main.java"
            classname = "Main"
            src_path = os.path.join(tmpdir, src_name)
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            try:
                comp = subprocess.run(
                    ["javac", src_name],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    text=True
                )
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "", "compile_output": "Compilation timed out", "exit_code": -1, "timed_out": True}

            if comp.returncode != 0:
                return {"stdout": "", "stderr": "", "compile_output": comp.stderr, "exit_code": comp.returncode, "timed_out": False}

            # Run java class
            try:
                proc = subprocess.run(
                    ["java", "-cp", ".", classname],
                    cwd=tmpdir,
                    input=stdin,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
                return {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "compile_output": "",
                    "exit_code": proc.returncode,
                    "timed_out": False
                }
            except subprocess.TimeoutExpired:
                return {"stdout": "", "stderr": "Execution timed out", "compile_output": "", "exit_code": -1, "timed_out": True}

    except Exception as e:
        return {"stdout": "", "stderr": f"Server error: {e}", "compile_output": "", "exit_code": -1, "timed_out": False}
    finally:
        # cleanup
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
