"""Automated test suite for A2A Binary Wire Protocol."""
import unittest
from agent_a2a_binary_wire_protocol.core import A2AFrame, A2AFrameType, A2AStreamDecoder

class TestA2ABinaryWireProtocol(unittest.TestCase):
    def test_encode_decode_roundtrip(self):
        payload = b'{"action": "evaluate", "score": 0.98}'
        frame = A2AFrame(msg_id=42, frame_type=A2AFrameType.TOOL_RESPONSE, payload=payload)
        raw = frame.encode()
        decoded = A2AFrame.decode(raw)
        self.assertEqual(decoded.msg_id, 42)
        self.assertEqual(decoded.frame_type, A2AFrameType.TOOL_RESPONSE)
        self.assertEqual(decoded.payload, payload)

    def test_corrupted_checksum_raises(self):
        payload = b"secure payload"
        frame = A2AFrame(msg_id=1, frame_type=A2AFrameType.SCRATCHPAD, payload=payload)
        raw = bytearray(frame.encode())
        raw[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            A2AFrame.decode(bytes(raw))

    def test_streaming_decoder_chunked_input(self):
        decoder = A2AStreamDecoder()
        f1 = A2AFrame(msg_id=1, frame_type=A2AFrameType.HEARTBEAT, payload=b"ping")
        f2 = A2AFrame(msg_id=2, frame_type=A2AFrameType.HEARTBEAT, payload=b"pong")
        stream = f1.encode() + f2.encode()

        frames = []
        for i in range(0, len(stream), 3):
            frames.extend(decoder.feed(stream[i:i+3]))

        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].payload, b"ping")
        self.assertEqual(frames[1].payload, b"pong")
