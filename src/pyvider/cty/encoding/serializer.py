
# pyvider/cty/encoding/serializer.py

from typing import Any

class ValueSerializer:
    """Handles serialization of Cty values to raw bytes (without protocol awareness)."""
    
    @staticmethod
    def to_json_bytes(value) -> bytes:
        """Serialize a Cty value to JSON bytes."""
        # Implementation using standard json module
        import json
        return json.dumps(value).encode('utf-8')
    
    @staticmethod
    def from_json_bytes(json_bytes: bytes) -> Any:
        """Deserialize JSON bytes to Python value."""
        import json
        return json.loads(json_bytes.decode('utf-8'))
        
    @staticmethod
    def to_msgpack_bytes(value) -> bytes:
        """Serialize a Cty value to msgpack bytes."""
        import msgpack
        return msgpack.packb(value)
        
    @staticmethod
    def from_msgpack_bytes(msgpack_bytes: bytes) -> Any:
        """Deserialize msgpack bytes to Python value."""
        import msgpack
        return msgpack.unpackb(msgpack_bytes)
