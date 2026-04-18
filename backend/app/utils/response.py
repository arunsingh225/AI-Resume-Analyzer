"""
Standardized API response helpers for consistent response shapes.
"""
from typing import Any, Optional


def success_response(data: Any, meta: Optional[dict] = None) -> dict:
    """Wrap successful response data in a standard envelope."""
    resp = {"success": True, "data": data}
    if meta:
        resp["meta"] = meta
    return resp


def error_response(message: str) -> dict:
    """Wrap error message in a standard envelope."""
    return {"success": False, "error": message}
