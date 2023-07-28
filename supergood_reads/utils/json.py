import json
from typing import Any
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    """Encodes UUIDs to strings."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
