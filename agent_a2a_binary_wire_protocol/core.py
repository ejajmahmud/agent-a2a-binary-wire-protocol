"""Core implementation of A2A binary wire protocol."""
import struct
import zlib
import enum
from typing import List, Optional, Tuple

MAGIC = b"A2A\x01"
HEADER_FORMAT = "!4sIIHB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

class A2AFrameType(enum.IntEnum):
    HEARTBEAT = 1
    TOOL_CALL = 2
    TOOL_RESPONSE = 3
    SCRATCHPAD = 4
    ERROR = 5

class A2AFrame:
    def __init__(self, msg_id: int, frame_type: A2AFrameType, payload: bytes, flags: int = 0):
        self.msg_id = msg_id
        self.frame_type = frame_type
        self.payload = payload
        self.flags = flags
        self.checksum = zlib.crc32(payload) & 0xFFFFFFFF

    def encode(self) -> bytes:
        payload_len = len(self.payload)
        header = struct.pack(HEADER_FORMAT, MAGIC, self.msg_id, self.checksum, payload_len, int(self.frame_type))
        return header + self.payload

    @classmethod
    def decode_header(cls, header_bytes: bytes) -> Tuple[int, int, int, int]:
        if len(header_bytes) < HEADER_SIZE:
            raise ValueError("Header truncated")
        magic, msg_id, checksum, payload_len, frame_type_val = struct.unpack(HEADER_FORMAT, header_bytes)
        if magic != MAGIC:
            raise ValueError(f"Invalid magic byte sequence: {magic}")
        return msg_id, checksum, payload_len, frame_type_val

    @classmethod
    def decode(cls, data: bytes) -> "A2AFrame":
        if len(data) < HEADER_SIZE:
            raise ValueError("Insufficient data for A2A frame")
        msg_id, checksum, payload_len, frame_type_val = cls.decode_header(data[:HEADER_SIZE])
        payload = data[HEADER_SIZE:HEADER_SIZE + payload_len]
        if len(payload) != payload_len:
            raise ValueError("Payload truncated")
        actual_checksum = zlib.crc32(payload) & 0xFFFFFFFF
        if actual_checksum != checksum:
            raise ValueError(f"CRC32 checksum mismatch: expected {checksum}, got {actual_checksum}")
        return cls(msg_id=msg_id, frame_type=A2AFrameType(frame_type_val), payload=payload)

class A2AStreamDecoder:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, chunk: bytes) -> List[A2AFrame]:
        self._buffer.extend(chunk)
        frames = []
        while len(self._buffer) >= HEADER_SIZE:
            try:
                msg_id, checksum, payload_len, frame_type_val = A2AFrame.decode_header(bytes(self._buffer[:HEADER_SIZE]))
            except ValueError:
                self._buffer.pop(0)
                continue

            total_frame_len = HEADER_SIZE + payload_len
            if len(self._buffer) < total_frame_len:
                break

            frame_data = bytes(self._buffer[:total_frame_len])
            self._buffer = self._buffer[total_frame_len:]
            frame = A2AFrame.decode(frame_data)
            frames.append(frame)
        return frames
