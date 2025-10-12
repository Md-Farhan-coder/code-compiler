from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, tempfile, os, shutil, sys

app = FastAPI(title="Python Online Compiler")

class RunRequest(BaseModel):
    code: str
    stdin: str = ""

class RunResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool

@app.post("/run", response_model=RunResponse)
def run_python(req: RunRequest):
    folder = tempfile.mkdtemp()
    code_file = os.path.join(folder, "main.py")
    with open(code_file, "w") as f:
        f.write(req.code)

    try:
        proc = subprocess.Popen(
            [sys.executable, code_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(req.stdin, timeout=5)
            timed_out = False
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            timed_out = True

        return RunResponse(
            stdout=stdout,
            stderr=stderr,
            exit_code=proc.returncode,
            timed_out=timed_out
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(folder)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
