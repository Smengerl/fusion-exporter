import weakref
from typing import Any, Dict

# Store addin instance (weakref if possible)
_fusion_app_ref = None

def set_app(app: Any) -> None:
    """Store the running add-in instance. Use a weakref if supported."""
    global _fusion_app_ref
    try:
        _fusion_app_ref = weakref.ref(app)
    except Exception:
        # Fallback to strong reference if object isn't weakref-able
        _fusion_app_ref = lambda: app

def get_app() -> Any:
    global _fusion_app_ref
    if _fusion_app_ref is None:
        return None
    try:
        return _fusion_app_ref()
    except Exception:
        try:
            return _fusion_app_ref()
        except Exception:
            return None


# Preferences storage
_preferences: Dict[str, Any] = {}

def set_preferences(prefs: Dict[str, Any]) -> None:
    """Replace the entire preferences dictionary."""
    global _preferences
    if prefs is None:
        _preferences = {}
    else:
        _preferences = dict(prefs)

def get_preferences() -> Dict[str, Any]:
    return dict(_preferences)

def set_preference(key: str, value: Any) -> None:
    _preferences[key] = value

def get_preference(key: str, default: Any = None) -> Any:
    return _preferences.get(key, default)

