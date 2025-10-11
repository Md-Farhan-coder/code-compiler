from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import asyncio

app = FastAPI()

# Judge0 API endpoint
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
# Replace with your RapidAPI Key
RAPIDAPI_KEY = "760be94f96msh825896edecae3fep1ce5d0jsn68d6948d9b98"
RAPIDAPI_HOST = "judge0-ce.p.rapidapi.com"

# Mapping languages to Judge0 language_id
LANGUAGE_MAP = {
    "python": 71,
    "cpp": 52,
    "java": 62
}

@app.get("/")
def home():
    return {"msg": "Live Compiler WebSocket Backend Running with Judge0"}

@app.websocket("/ws/run")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    stdin_lines = []
    try:
        # Receive initial code and language
        data = await ws.receive_json()
        language = data.get("language")
        code = data.get("code")

        if language not in LANGUAGE_MAP:
            await ws.send_text("Unsupported language!")
            await ws.close()
            return

        lang_id = LANGUAGE_MAP[language]
        await ws.send_text("[Connected to live terminal]\nType your input below:")

        # Function to submit code to Judge0
        async def submit_code(stdin_text):
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-RapidAPI-Key": RAPIDAPI_KEY,
                    "X-RapidAPI-Host": RAPIDAPI_HOST,
                    "Content-Type": "application/json"
                }
                payload = {
                    "language_id": lang_id,
                    "source_code": code,
                    "stdin": stdin_text
                }
                # Wait=true makes Judge0 respond after execution
                response = await client.post(
                    JUDGE0_URL + "?base64_encoded=false&wait=true",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                return response.json()

        # Loop to receive live input
        while True:
            msg = await ws.receive_text()
            if msg.strip().lower() == "exit":
                await ws.send_text("\n[Session ended]")
                await ws.close()
                return

            stdin_lines.append(msg)
            stdin_text = "\n".join(stdin_lines)
            result = await submit_code(stdin_text)

            stdout = result.get("stdout") or ""
            stderr = result.get("stderr") or ""
            compile_output = result.get("compile_output") or ""

            output_text = ""
            if compile_output:
                output_text += f"[Compile Error]\n{compile_output}\n"
            if stderr:
                output_text += f"[Runtime Error]\n{stderr}\n"
            if stdout:
                output_text += stdout

            await ws.send_text(output_text)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await ws.send_text(f"[Error] {str(e)}")
        await ws.close()
