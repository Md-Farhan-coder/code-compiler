from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import os

app = FastAPI()

# Allow all origins (CORS fix for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    stdin = data.get("stdin", "")
    language = data.get("language", "python").lower()

    with tempfile.TemporaryDirectory() as tmpdirname:
        if language == "python":
            code_file = os.path.join(tmpdirname, "main.py")
            with open(code_file, "w") as f:
                f.write(code)
            cmd = ["python3", code_file]

        elif language == "cpp":
            code_file = os.path.join(tmpdirname, "main.cpp")
            exe_file = os.path.join(tmpdirname, "a.out")
            with open(code_file, "w") as f:
                f.write(code)
            compile_proc = subprocess.run(["g++", code_file, "-o", exe_file],
                                          capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return {"output": compile_proc.stderr}
            cmd = [exe_file]

        elif language == "java":
            code_file = os.path.join(tmpdirname, "Main.java")
            with open(code_file, "w") as f:
                f.write(code)
            compile_proc = subprocess.run(["javac", code_file],
                                          capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return {"output": compile_proc.stderr}
            cmd = ["java", "-cp", tmpdirname, "Main"]

        else:
            return {"output": "Unsupported language"}

        try:
            result = subprocess.run(
                cmd,
                input=stdin.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            output = result.stdout.decode() + result.stderr.decode()
        except subprocess.TimeoutExpired:
            output = "Execution timed out."

        return {"output": output}
