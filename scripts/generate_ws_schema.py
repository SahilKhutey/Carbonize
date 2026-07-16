"""
scripts/generate_ws_schema.py

Generate JSON Schema from Pydantic v2 WebSocket protocol models.
Output is consumed by json2ts to produce TypeScript types for the frontend.

Usage:
    python scripts/generate_ws_schema.py > docs/architecture/ws-schema.json

Then in the web package:
    npx json-schema-to-typescript docs/architecture/ws-schema.json > packages/web/src/types/ws-generated.d.ts
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure workspace src is on the path
workspace = Path(__file__).parent.parent
sys.path.insert(0, str(workspace / "packages" / "api" / "src"))

from cbms_api.websocket.v1_models import (
    AlertClearedMessage,
    AlertMessage,
    CommandAckMessage,
    CommandMessage,
    ErrorMessage,
    GoodbyeMessage,
    PingMessage,
    PongMessage,
    PROTOCOL_SUBPROTOCOL,
    PROTOCOL_VERSION,
    ResumeMessage,
    SubscribeMessage,
    TickMessage,
    WelcomeMessage,
)

MESSAGE_CLASSES = [
    WelcomeMessage,
    SubscribeMessage,
    TickMessage,
    AlertMessage,
    AlertClearedMessage,
    CommandMessage,
    CommandAckMessage,
    PingMessage,
    PongMessage,
    ErrorMessage,
    GoodbyeMessage,
    ResumeMessage,
]


def main() -> None:
    output = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "CBMS WebSocket Protocol v1",
        "description": (
            "Auto-generated JSON Schema from Pydantic models. "
            "DO NOT EDIT. Re-generate with: python scripts/generate_ws_schema.py"
        ),
        "protocol_version": PROTOCOL_VERSION,
        "subprotocol": PROTOCOL_SUBPROTOCOL,
        "messages": {},
        "discriminator": {
            "field": "type",
            "mapping": {cls.model_fields["type"].default: cls.__name__ for cls in MESSAGE_CLASSES},
        },
    }

    # Collect all $defs so they can be merged and de-duplicated
    all_defs: dict = {}
    schemas: dict = {}

    for cls in MESSAGE_CLASSES:
        schema = cls.model_json_schema()
        # Merge top-level $defs into shared pool
        defs = schema.pop("$defs", {})
        all_defs.update(defs)
        schemas[cls.__name__] = schema

    output["$defs"] = all_defs
    output["messages"] = schemas

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
