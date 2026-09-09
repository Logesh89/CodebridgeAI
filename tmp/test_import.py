import sys
import os

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.main import app
    print("SUCCESS: Imported app.main successfully!")
except Exception as e:
    import traceback
    print("IMPORT ERROR:")
    traceback.print_exc()
