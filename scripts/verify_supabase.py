#!/usr/bin/env python3
"""Verify Supabase connection. Run from project root: python3 scripts/verify_supabase.py"""
import os
import sys
import signal

# Project root
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
os.chdir(root)

# Load env (same as app)
try:
    from env_loader import load_env
    load_env()
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    try:
        import environment_config  # noqa: F401
    except Exception:
        pass

TIMEOUT_SECONDS = 15


def main():
    url = (os.environ.get('SUPABASE_URL') or '').strip()
    key = (os.environ.get('SUPABASE_ANON_KEY') or '').strip()

    if not url or not key:
        print("Supabase is NOT established.")
        print("  SUPABASE_URL and/or SUPABASE_ANON_KEY are missing.")
        print("  Set them in .env or environment_config.py (see SUPABASE_SETUP.md).")
        return 1

    print(f"SUPABASE_URL: {url}")
    print("SUPABASE_ANON_KEY: set")
    print("Testing connection (timeout %ds)..." % TIMEOUT_SECONDS)

    def _timeout(*_):
        raise TimeoutError("Connection timed out after %s seconds. Is the project paused or unreachable?" % TIMEOUT_SECONDS)

    try:
        from supabase_config import supabase_manager
        if supabase_manager is None:
            print("Supabase is NOT established (init failed). Check the warning above.")
            return 1
        # Quick test query with timeout (Unix/macOS)
        try:
            signal.signal(signal.SIGALRM, _timeout)
            signal.alarm(TIMEOUT_SECONDS)
            supabase_manager.get_all_charts(limit=1)
        finally:
            signal.alarm(0)
        print("Supabase is established. Connection OK.")
        return 0
    except TimeoutError as e:
        print(f"Supabase: {e}")
        print("  If the project is paused, restore it in the Supabase dashboard.")
        return 1
    except Exception as e:
        print(f"Supabase connection failed: {e}")
        print("  Check URL, anon key, and that the project is active (see SUPABASE_SETUP.md).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
