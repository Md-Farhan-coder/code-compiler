from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import os

# Create FastAPI app
app = FastAPI()

# ✅ Fix CORS (allow all origins for testing)
# In production, replace ["*"] with your domain (like ["https://myfrontend.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Python Online Compiler is Running!"}


@app.post("/run")
async def run_code(request: Request):
    """
    Runs Python code sent in the request body.
    Expected JSON format:
    {
        "code": "print('Hello')",
        "stdin": "input_data_here"
    }
    """
    try:
        data = await request.json()
        code = data.get("code", "")
        stdin = data.get("stdin", "")

        # Temporary folder for code execution
        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = os.path.join(tmpdir, "main.py")

            # Save the received code into main.py
            with open(code_path, "w") as f:
                f.write(code)

            try:
                # Run Python code with timeout and capture stdout/stderr
                result = subprocess.run(
                    ["python3", code_path],
                    input=stdin.encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5  # seconds
                )

                return {
                    "stdout": result.stdout.decode(),
                    "stderr": result.stderr.decode(),
                    "exit_code": result.returncode,
                    "timed_out": False
                }

            except subprocess.TimeoutExpired:
                return {
                    "stdout": "",
                    "stderr": "❌ Execution timed out after 5 seconds.",
                    "exit_code": -1,
                    "timed_out": True
                }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Server Error: {str(e)}",
            "exit_code": -1,
            "timed_out": False
        }
