"""Resolve a controller at mission start; fail back to baseline."""
import os

def resolve(robot_id):
    from dotenv import load_dotenv
    from flagsmith import Flagsmith
    load_dotenv()
    try:
        client = Flagsmith(environment_key=os.environ["FLAGSMITH_ENVIRONMENT_KEY"], request_timeout_seconds=3)
        flags = client.get_identity_flags(robot_id)
        value = flags.get_feature_value("navigation_strategy")
        if flags.is_feature_enabled("navigation_strategy") and value in ("astar","congestion_aware"):
            return value, "flagsmith"
        return "astar", "disabled_or_invalid"
    except Exception:
        return "astar", "fallback"
