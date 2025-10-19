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
        "difficulty":"Easy",
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ],
        "testcases": [
            {"input": "2\n3", "output": "5"},
            {"input": "10\n20", "output": "30"},
            {"input": "-5\n8", "output": "3"}
        ],
        "tags":["Array","Math"],
        "input_format":"Input two integers",
        "output_format":"Print the sum only"
    },
    {
    "id": 2,
    "title": "Palindrome Check",
    "description": "Given a string, check if it is a palindrome. A palindrome is a string that reads the same forwards and backwards.",
    "sample_input": "racecar",
    "sample_output": "true",
    "difficulty": "Easy",
    "constraints": [
        "1 <= s.length <= 10^5",
        "s consists only of printable ASCII characters",
        "Ignore case sensitivity",
        "Ignore non-alphanumeric characters"
    ],
    "testcases": [
        {"input": "racecar", "output": "true"},
        {"input": "hello", "output": "false"},
        {"input": "A man a plan a canal Panama", "output": "true"},
        {"input": "12321", "output": "true"},
        {"input": "No 'x' in Nixon", "output": "true"}
    ],
    "tags": ["String", "Two Pointers"],
    "input_format": "Input a string",
    "output_format": "Print 'true' if palindrome, 'false' otherwise"
    },
    {
    "id": 3,
    "title": "Reverse Integer",
    "description": "Given a signed 32-bit integer, reverse its digits. If reversing causes overflow, return 0.",
    "sample_input": "123",
    "sample_output": "321",
    "difficulty": "Medium",
    "constraints": [
        "-2^31 <= x <= 2^31 - 1",
        "If reversed integer overflows 32-bit range, return 0",
        "Leading zeros in reversed number should be omitted"
    ],
    "testcases": [
        {"input": "123", "output": "321"},
        {"input": "-123", "output": "-321"},
        {"input": "120", "output": "21"},
        {"input": "0", "output": "0"},
        {"input": "1534236469", "output": "0"},
        {"input": "-2147483648", "output": "0"}
    ],
    "tags": ["Math", "Number Theory"],
    "input_format": "Input a single integer",
    "output_format": "Print the reversed integer"
    },
    {
    "id": 4,
    "title": "Valid Parentheses",
    "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if: 1. Open brackets must be closed by the same type of brackets. 2. Open brackets must be closed in the correct order. 3. Every close bracket has a corresponding open bracket of the same type.",
    "sample_input": "()[]{}",
    "sample_output": "true",
    "difficulty": "Medium",
    "constraints": [
        "1 <= s.length <= 10^4",
        "s consists of parentheses only '()[]{}'",
        "Empty string is considered valid"
    ],
    "testcases": [
        {"input": "()[]{}", "output": "true"},
        {"input": "([)]", "output": "false"},
        {"input": "{[]}", "output": "true"},
        {"input": "(]", "output": "false"},
        {"input": "((()))", "output": "true"},
        {"input": "([{}])", "output": "true"},
        {"input": "", "output": "true"},
        {"input": "(((({{{[[]]}}}))))", "output": "true"}
    ],
    "tags": ["String", "Stack"],
    "input_format": "Input a string containing parentheses",
    "output_format": "Print 'true' if valid, 'false' otherwise"
    },
    {
    "id": 5,
    "title": "Factorial of a Number",
    "description": "Given a non-negative integer n, return the factorial of n. The factorial of n is the product of all positive integers less than or equal to n.",
    "sample_input": "5",
    "sample_output": "120",
    "difficulty": "Easy",
    "constraints": [
        "0 <= n <= 20",
        "Use iterative or recursive approach",
        "Factorial of 0 is 1"
    ],
    "testcases": [
        {"input": "5", "output": "120"},
        {"input": "0", "output": "1"},
        {"input": "1", "output": "1"},
        {"input": "7", "output": "5040"},
        {"input": "10", "output": "3628800"},
        {"input": "20", "output": "2432902008176640000"}
    ],
    "tags": ["Math", "Recursion"],
    "input_format": "Input a single non-negative integer",
    "output_format": "Print the factorial of the number"
    },
    {
    "id": 6,
    "title": "Prime Number Check",
    "description": "Given a positive integer, determine if it is a prime number. A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. This means it cannot be formed by multiplying two smaller natural numbers. The first few prime numbers are 2, 3, 5, 7, 11, 13, 17, 19, 23, and so on. Note that 1 is not considered a prime number because it does not meet the definition of having exactly two distinct positive divisors.",
    "sample_input": "7",
    "sample_output": "true",
    "difficulty": "Easy",
    "constraints": [
        "1 <= n <= 10^6",
        "Input will be a positive integer",
        "Optimize for large numbers (use efficient algorithms)",
        "1 is not a prime number"
    ],
    "testcases": [
        {"input": "7", "output": "true"},
        {"input": "4", "output": "false"},
        {"input": "1", "output": "false"},
        {"input": "2", "output": "true"},
        {"input": "97", "output": "true"},
        {"input": "100", "output": "false"},
        {"input": "7919", "output": "true"},
        {"input": "1000000", "output": "false"}
    ],
    "tags": ["Math", "Number Theory", "Algorithms"],
    "input_format": "Input a single positive integer",
    "output_format": "Print 'true' if prime, 'false' otherwise"
    },
    {
    "id": 7,
    "title": "Sort Array",
    "description": "Given an array of integers, sort the array in non-decreasing order. You can use any sorting algorithm such as bubble sort, merge sort, quicksort, or built-in sort functions. The array should be sorted from smallest to largest value.",
    "sample_input": "5\n5\n2\n8\n1\n9",
    "sample_output": "1\n2\n5\n8\n9",
    "difficulty": "Easy",
    "constraints": [
        "1 <= arr.length <= 10^4",
        "-10^5 <= arr[i] <= 10^5",
        "Array may contain duplicate values",
        "Sort in ascending order"
    ],
    "testcases": [
        {"input": "5\n5\n2\n8\n1\n9", "output": "1\n2\n5\n8\n9"},
        {"input": "8\n3\n1\n4\n1\n5\n9\n2\n6", "output": "1\n1\n2\n3\n4\n5\n6\n9"},
        {"input": "5\n-5\n-2\n-8\n0\n3", "output": "-8\n-5\n-2\n0\n3"},
        {"input": "1\n1", "output": "1"},
        {"input": "5\n5\n4\n3\n2\n1", "output": "1\n2\n3\n4\n5"},
        {"input": "4\n1\n1\n1\n1", "output": "1\n1\n1\n1"}
    ],
    "tags": ["Array", "Sorting", "Algorithms"],
    "input_format": "First line: number of elements (n)\nNext n lines: array elements",
    "output_format": "Print sorted array elements, each on a new line"
    },


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
            return {
                "id":q["id"],
                "title":q["title"],
                "description":q["description"],
                "constraints":q["constraints"],
                "tags":q["tags"],
                "input_format":q["input_format"],
                "output_format":q["output_format"],
                "difficulty":q["difficulty"]
            }
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
