import asyncio
import sys
import traceback

try:
    from main import main
    asyncio.run(main())
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
