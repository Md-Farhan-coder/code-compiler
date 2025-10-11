from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import subprocess
import tempfile
import os
import time

app = FastAPI()

@app.post("/run")
async def run_code(language: str = Form(...), code: str = Form(...), stdin: str = Form("")):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = None
            run_cmd = None

            if language == "python":
                file_path = os.path.join(tmpdir, "main.py")
                run_cmd = ["python3", file_path]
            elif language == "cpp":
                file_path = os.path.join(tmpdir, "main.cpp")
                exe_file = os.path.join(tmpdir, "a.out")
                compile_cmd = ["g++", file_path, "-o", exe_file]
                run_cmd = [exe_file]
            elif language == "java":
                file_path = os.path.join(tmpdir, "Main.java")
                compile_cmd = ["javac", file_path]
                run_cmd = ["java", "-cp", tmpdir, "Main"]
            else:
                return JSONResponse({"error": "Unsupported language"}, status_code=400)

            # Write the code to file
            with open(file_path, "w") as f:
                f.write(code)

            # Compile if needed
            if language in ["cpp", "java"]:
                compile_process = subprocess.run(
                    compile_cmd, capture_output=True, text=True
                )
                if compile_process.returncode != 0:
                    return JSONResponse({"error": compile_process.stderr}, status_code=400)

            # Run the code with input
            start = time.time()
            result = subprocess.run(
                run_cmd, input=stdin, capture_output=True, text=True, timeout=5
            )
            end = time.time()

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "time": round(end - start, 3),
            }

    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "Execution timed out"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
