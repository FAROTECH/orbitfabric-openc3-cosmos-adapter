from __future__ import annotations

import argparse
import json
import signal
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any

STOP_ACQUISITION_COMMAND_ID = 1
STATUS_PACKET_ID = 2


def emit(event: str, **fields: Any) -> None:
    payload = {"event": event, "time": time.time(), **fields}
    print(json.dumps(payload, sort_keys=True), flush=True)


@dataclass
class SimulatorState:
    stop: threading.Event = field(default_factory=threading.Event)
    telemetry_connected: threading.Event = field(default_factory=threading.Event)
    telemetry_socket: socket.socket | None = None
    telemetry_lock: threading.Lock = field(default_factory=threading.Lock)
    acquisition_active: bool = True

    def attach_telemetry(self, client: socket.socket) -> None:
        with self.telemetry_lock:
            self.telemetry_socket = client
            self.telemetry_connected.set()

    def detach_telemetry(self, client: socket.socket) -> None:
        with self.telemetry_lock:
            if self.telemetry_socket is client:
                self.telemetry_socket = None
                self.telemetry_connected.clear()

    def publish_status(self) -> None:
        if not self.telemetry_connected.wait(timeout=5.0):
            raise RuntimeError("COSMOS telemetry connection did not become available")

        packet = bytes([STATUS_PACKET_ID, 1 if self.acquisition_active else 0])
        with self.telemetry_lock:
            client = self.telemetry_socket
            if client is None:
                raise RuntimeError("COSMOS telemetry connection disappeared")
            client.sendall(packet)

        emit(
            "telemetry_sent",
            packet="STATUS",
            acquisition_active=self.acquisition_active,
            bytes_hex=packet.hex(),
        )


def handle_command_bytes(state: SimulatorState, data: bytes) -> None:
    emit("command_bytes_received", bytes_hex=data.hex(), length=len(data))
    for value in data:
        if value != STOP_ACQUISITION_COMMAND_ID:
            emit("unknown_command", command_id=value)
            continue

        emit(
            "command_received",
            command="STOP_ACQUISITION",
            command_id=value,
        )
        state.acquisition_active = False
        state.publish_status()


def serve_telemetry(state: SimulatorState, host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        server.settimeout(0.5)
        emit("telemetry_listener_ready", host=host, port=port)

        while not state.stop.is_set():
            try:
                client, address = server.accept()
            except socket.timeout:
                continue

            emit("telemetry_client_connected", peer=list(address))
            state.attach_telemetry(client)
            try:
                while not state.stop.wait(0.25):
                    pass
            finally:
                state.detach_telemetry(client)
                client.close()
                emit("telemetry_client_disconnected")


def serve_commands(state: SimulatorState, host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        server.settimeout(0.5)
        emit("command_listener_ready", host=host, port=port)

        while not state.stop.is_set():
            try:
                client, address = server.accept()
            except socket.timeout:
                continue

            emit("command_client_connected", peer=list(address))
            client.settimeout(0.5)
            with client:
                while not state.stop.is_set():
                    try:
                        data = client.recv(4096)
                    except socket.timeout:
                        continue
                    if not data:
                        break
                    handle_command_bytes(state, data)
            emit("command_client_disconnected")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="External OFDEMO target for canonical OpenC3 COSMOS native acceptance."
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--command-port", type=int, default=18080)
    parser.add_argument("--telemetry-port", type=int, default=18081)
    args = parser.parse_args()

    state = SimulatorState()

    def request_stop(signum: int, _frame: Any) -> None:
        emit("shutdown_requested", signal=signum)
        state.stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    threads = [
        threading.Thread(
            target=serve_commands,
            args=(state, args.host, args.command_port),
            name="ofdemo-command-server",
            daemon=True,
        ),
        threading.Thread(
            target=serve_telemetry,
            args=(state, args.host, args.telemetry_port),
            name="ofdemo-telemetry-server",
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    emit(
        "simulator_ready",
        command_port=args.command_port,
        telemetry_port=args.telemetry_port,
        acquisition_active=state.acquisition_active,
    )

    while not state.stop.wait(0.25):
        pass

    for thread in threads:
        thread.join(timeout=2.0)
    emit("simulator_stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
