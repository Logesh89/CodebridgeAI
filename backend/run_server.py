import os
import uvicorn

if __name__ == "__main__":
    os.environ["USE_SQLITE"] = "true"
    print("Starting SnapLogic Platform backend server on http://127.0.0.1:8005 ...", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8005, log_level="info")
