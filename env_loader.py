"""
Load environment from project root so Supabase and other config work from any cwd.
Call load_env() before importing supabase_config or using os.environ for SUPABASE_*.
"""
import os
import sys

_PROJECT_ROOT = None


def get_project_root():
    """Return the project root directory (where app_global.py and .env live)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    # This file is in project root
    _PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    return _PROJECT_ROOT


def load_env():
    """
    Load .env from project root (if present), then apply environment_config.
    Use override=False so existing env vars (e.g. from shell) are not overwritten.
    """
    root = get_project_root()
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(root, ".env")
        load_dotenv(env_path, override=False)
    except Exception:
        pass
    try:
        import environment_config  # noqa: F401
    except Exception:
        pass
