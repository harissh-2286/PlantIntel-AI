import os
import sys
import subprocess

def run_cmd(cmd, cwd=None):
    print(f" Executing: {cmd} (in {cwd or '.'})")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}: {cmd}")
        sys.exit(result.returncode)

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    backend_dir = os.path.join(root_dir, "backend")
    dist_dir = os.path.join(frontend_dir, "dist")

    print("\n==================================================")
    print("      PLANTINTEL AI - PRODUCTION DEPLOYMENT       ")
    print("==================================================\n")

    # Step 1: Ensure Frontend Production Build Exists
    if not os.path.exists(dist_dir) or not os.listdir(dist_dir):
        print("🔨 Building Frontend Production Bundle...")
        run_cmd("npm run build", cwd=frontend_dir)
    else:
        print("✓ Frontend production build found at frontend/dist")

    # Step 2: Set Python Path & Virtual Env Executable
    venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    print(f"✓ Using Python executable: {venv_python}")
    print("\n🚀 Launching Unified Production Server on http://0.0.0.0:8000...")
    print("   -> Frontend App: http://localhost:8000")
    print("   -> API Health:   http://localhost:8000/api/health")
    print("   -> API Docs:     http://localhost:8000/docs")
    print("==================================================\n")

    # Step 3: Run Uvicorn Server
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)
    subprocess.run([
        venv_python, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()
