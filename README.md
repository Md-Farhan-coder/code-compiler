# Simple Online Code Compiler API

### Run locally:
pip install -r requirements.txt
uvicorn main:app --reload

### Example API call:
POST /run
Form Data:
  language: python | cpp | java
  code: your code here
  stdin: your input here
