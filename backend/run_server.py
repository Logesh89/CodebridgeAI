import os
import sys

# Get absolute path to backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get parent directory (project root)
project_root = os.path.dirname(current_dir)

# Add both to sys.path
for p in [project_root, current_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ["USE_SQLITE"] = "true"

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting SnapLogic Platform backend server on http://127.0.0.1:8005 ...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
