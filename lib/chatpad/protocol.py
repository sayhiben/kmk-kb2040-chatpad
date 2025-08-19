"""UART protocol handler for Xbox 360 Chatpad."""
import busio
from time import monotonic
from config import (
    Protocol, UART_TX_PIN, UART_RX_PIN, UART_BAUDRATE,
    UART_BUFFER_SIZE, KEEP_ALIVE_INTERVAL
)

class FrameParser:
    """Accumulates bytes and yields validated frames."""

    def __init__(self):
        self.buffer = bytearray()

    def add_data(self, data):
        if data:
            self.buffer.extend(data)
            if len(self.buffer) > UART_BUFFER_SIZE * 2:
                # keep recent bytes only
                self.buffer = self.buffer[-UART_BUFFER_SIZE:]

    def get_frame(self):
        """Return next 8‑byte valid data frame or None."""
        while len(self.buffer) >= Protocol.FRAME_SIZE:
            # skip status frames
            if self.buffer[0] == Protocol.STATUS_HEADER:
                self.buffer = self.buffer[Protocol.FRAME_SIZE:]
                continue
            # look for data header
            if self.buffer[0] == Protocol.DATA_HEADER:
                if len(self.buffer) < Protocol.FRAME_SIZE:
                    return None
                if self.buffer[1] != Protocol.HEADER2:
                    self.buffer = self.buffer[1:]
                    continue
                frame = bytes(self.buffer[:Protocol.FRAME_SIZE])
                if self._checksum_ok(frame):
                    self.buffer = self.buffer[Protocol.FRAME_SIZE:]
                    return frame
                # bad checksum, resync by one byte
                self.buffer = self.buffer[1:]
                continue
            # unknown, drop a byte
            self.buffer = self.buffer[1:]
        return None

    @staticmethod
    def _checksum_ok(frame):
        s = sum(frame[:7]) & 0xFF
        return ((-s) & 0xFF) == frame[7]


class UARTHandler:
    """Non‑blocking UART with parsing and keep‑alive."""

    def __init__(self):
        self.uart = busio.UART(
            tx=UART_TX_PIN, rx=UART_RX_PIN,
            baudrate=UART_BAUDRATE, timeout=0, receiver_buffer_size=UART_BUFFER_SIZE
        )
        self.parser = FrameParser()
        self.last_ping = 0.0
        self.uart.write(Protocol.INIT_MSG)

    def maintain(self):
        now = monotonic()
        if now - self.last_ping > KEEP_ALIVE_INTERVAL:
            self.uart.write(Protocol.AWAKE_MSG)
            self.last_ping = now

    def next_report(self):
        """Return dict {'modifiers','key0','key1'} or None."""
        iw = getattr(self.uart, "in_waiting", 0)
        if iw:
            data = self.uart.read(iw)
            # Debug: Enable to see raw UART data
            # print(f"UART RX ({len(data)} bytes): {' '.join(hex(b) for b in data)}")
            self.parser.add_data(data)
        frame = self.parser.get_frame()
        if not frame:
            return None
        # Debug: Enable to see parsed frames
        # print(f"Frame: {' '.join(hex(b) for b in frame)}")
        return {"modifiers": frame[3], "key0": frame[4], "key1": frame[5]}