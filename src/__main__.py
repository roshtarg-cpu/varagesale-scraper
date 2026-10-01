import asyncio
import sys
import traceback

print("__main__ loading...", flush=True)

try:
    print("Importing main...", flush=True)
    from .main import main
    print("Running main...", flush=True)
    asyncio.run(main())
    print("Main completed", flush=True)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    traceback.print_exc()
    sys.exit(1)
