import os
import subprocess
import time

def main():
    print("Starting JustorAI Local Development Environment...")
    
    # 1. Start Python Backend
    print("\n[1/2] Starting FastAPI Backend on port 10000...")
    backend_env = os.environ.copy()
    
    # Check if .venv exists
    python_cmd = ".venv\\Scripts\\python.exe" if os.path.exists(".venv") else "python"
    
    backend_process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "10000", "--reload"],
        env=backend_env
    )
    
    time.sleep(2) # Give backend a second to start
    
    # 2. Start Frontend
    print("\n[2/2] Starting Vite Frontend...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        shell=True
    )
    
    print("\n=== Development Servers Running ===")
    print("Backend API: http://localhost:10000")
    print("Frontend UI: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers.")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
