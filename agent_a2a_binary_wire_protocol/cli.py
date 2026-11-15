"""CLI interface for A2A binary wire protocol."""
import argparse
import sys
from .core import A2AFrame, A2AFrameType, A2AStreamDecoder

def main():
    parser = argparse.ArgumentParser(description="A2A Binary Wire Protocol CLI")
    parser.add_argument("--demo", action="store_true", help="Run protocol encode/decode verification")
    parser.add_argument("--msg", default="Hello Agent Swarm", help="Message payload for test frame")
    args = parser.parse_args()

    frame = A2AFrame(msg_id=101, frame_type=A2AFrameType.TOOL_CALL, payload=args.msg.encode("utf-8"))
    raw = frame.encode()
    print(f"Encoded frame bytes: {len(raw)} bytes")
    decoded = A2AFrame.decode(raw)
    print(f"Decoded msg_id: {decoded.msg_id}, payload: {decoded.payload.decode('utf-8')}")

if __name__ == "__main__":
    main()
