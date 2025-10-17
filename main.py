from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import os

app = FastAPI()

origins = [
    "http://localhost:3000",       # your local frontend
    "https://code-compiler-8mlf.onrender.com", 
    "http://localhost:5173",  # Add Vite dev server
    "http://127.0.0.1:3000",  # Add localhost variant   # add your production domain here
]
# Allow all origins (CORS fix for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,    
    
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Basic DSA Question Bank
DSA_QUESTIONS = [
    {
        "id": 1,
        "title": "Sum of Two Numbers",
        "description": "Given two integers, print their sum.",
        "sample_input": "2 3",
        "sample_output": "5",
        "testcases": [
            {"input": "2 3", "output": "5"},
            {"input": "10 20", "output": "30"},
            {"input": "-5 8", "output": "3"}
        ]
    },
    {
        "id": 2,
        "title": "Reverse a String",
        "description": "Given a string, print its reverse.",
        "sample_input": "hello",
        "sample_output": "olleh",
        "testcases": [
            {"input": "hello", "output": "olleh"},
            {"input": "abcd", "output": "dcba"},
            {"input": "madam", "output": "madam"}
        ]
    }
]


@app.get("/")
def home():
    return {"message": "Online Compiler & DSA API is running!"}


@app.get("/questions")
def get_questions():
    return {"questions": DSA_QUESTIONS}


@app.get("/questions/{qid}")
def get_question(qid: int):
    for q in DSA_QUESTIONS:
        if q["id"] == qid:
            return q
    return {"error": "Question not found"}


@app.post("/submit")
async def submit_solution(request: Request):
    data = await request.json()
    language = data.get("language", "python").lower()
    code = data.get("code", "")
    qid = data.get("question_id", None)

    question = next((q for q in DSA_QUESTIONS if q["id"] == qid), None)
    if not question:
        return {"error": "Invalid question ID"}

    passed = 0
    total = len(question["testcases"])
    results = []

    for case in question["testcases"]:
        result = run_code_direct(language, code, case["input"])
        got = result["stdout"].strip()
        expected = case["output"].strip()
        is_passed = got == expected
        if is_passed:
            passed += 1
        results.append({
            "input": case["input"],
            "expected": expected,
            "got": got,
            "passed": is_passed,
            "stderr": result["stderr"]
        })

    return {
        "question": question["title"],
        "passed": passed,
        "total": total,
        "results": results
    }


@app.post("/run")
async def run_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    stdin = data.get("stdin", "")
    language = data.get("language", "python").lower()
    return run_code_direct(language, code, stdin)


def run_code_direct(language, code, stdin):
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
                return {"stdout": "", "stderr": compile_proc.stderr}
            cmd = [exe_file]

        elif language == "java":
            code_file = os.path.join(tmpdirname, "Main.java")
            with open(code_file, "w") as f:
                f.write(code)
            compile_proc = subprocess.run(["javac", code_file],
                                          capture_output=True, text=True)
            if compile_proc.returncode != 0:
                return {"stdout": "", "stderr": compile_proc.stderr}
            cmd = ["java", "-cp", tmpdirname, "Main"]

        elif language == "javascript":
            code_file = os.path.join(tmpdirname, "main.js")
            with open(code_file, "w") as f:
                f.write(code)
            cmd = ["node", code_file]

        else:
            return {"stdout": "", "stderr": "Unsupported language"}

        try:
            result = subprocess.run(
                cmd,
                input=stdin.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return {
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode()
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Execution timed out"}
