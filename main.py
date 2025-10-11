from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import docker
import tempfile, os, shutil
import asyncio

app = FastAPI()
client = docker.from_env()

@app.get("/")
def home():
    return {"msg": "Live Compiler WebSocket Backend Running"}

@app.websocket("/ws/run")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        # Receive initial data: language & code
        data = await ws.receive_json()
        language = data.get("language")
        code = data.get("code")

        tmpdir = tempfile.mkdtemp()
        compile_cmd = None
        run_cmd = []

        # Create code file & commands
        if language == "python":
            filename = "main.py"
            open(os.path.join(tmpdir, filename), "w").write(code)
            run_cmd = ["python3", filename]
        elif language == "cpp":
            filename = "main.cpp"
            open(os.path.join(tmpdir, filename), "w").write(code)
            compile_cmd = ["g++", filename, "-o", "a.out"]
            run_cmd = ["./a.out"]
        elif language == "java":
            filename = "Main.java"
            open(os.path.join(tmpdir, filename), "w").write(code)
            compile_cmd = ["javac", filename]
            run_cmd = ["java", "-cp", tmpdir, "Main"]
        else:
            await ws.send_text("Unsupported language")
            await ws.close()
            return

        # Start Docker container
        container = client.containers.run(
            "code-runner",
            command="sleep 60",
            detach=True,
            working_dir="/work",
            network_disabled=True,
            mem_limit="256m",
            mounts=[docker.types.Mount("/work", tmpdir, type="bind")]
        )

        # Compile step if needed
        if compile_cmd:
            compile_res = container.exec_run(compile_cmd)
            if compile_res.exit_code != 0:
                await ws.send_text("Compilation Error:\n" + compile_res.output.decode())
                await ws.close()
                container.remove(force=True)
                shutil.rmtree(tmpdir)
                return

        # Start interactive execution
        exec_id = client.api.exec_create(
            container.id, run_cmd, stdin=True, stdout=True, stderr=True, tty=True
        )["Id"]
        sock = client.api.exec_start(exec_id, detach=False, tty=True, socket=True)

        async def read_output():
            while True:
                try:
                    output = sock._sock.recv(1024)
                    if not output:
                        break
                    await ws.send_text(output.decode(errors="replace"))
                except Exception:
                    break

        # Run output reader in background
        asyncio.create_task(read_output())

        # Receive live input from frontend
        while True:
            msg = await ws.receive_text()
            if msg.strip().lower() == "exit":
                break
            sock._sock.send((msg + "\n").encode())

        await ws.send_text("\n[Session ended]")
        await ws.close()

    except WebSocketDisconnect:
        pass
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        if 'container' in locals():
            container.remove(force=True)
