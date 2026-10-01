from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("greenbusiness.security")


def security_event(event_name: str, **fields: Any) -> None:
    safe = {
        str(key): value
        for key, value in fields.items()
        if str(key).lower()
        not in {"authorization", "cookie", "password", "receipt_id", "refresh_token", "token"}
    }
    logger.warning(
        "security_event %s",
        json.dumps({"event": event_name, **safe}, sort_keys=True, default=str),
    )
