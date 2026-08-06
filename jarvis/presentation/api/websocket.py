"""
WebSocket Telemetry Stream Controller.
Broadcasts real-time system health, process states, and event updates.
"""

import asyncio
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jarvis.infrastructure.logging.logger import get_logger

logger = get_logger("jarvis.websocket")
router = APIRouter(tags=["WebSocket Telemetry Stream"])


class ConnectionManager:
    """Manages active WebSocket telemetry subscriptions."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket telemetry client connected", client=str(websocket.client))

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
        logger.info("WebSocket telemetry client disconnected")

    async def broadcast(self, message: dict) -> None:
        if not self.active_connections:
            return
        payload = json.dumps(message)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket) -> None:
    """Real-time telemetry stream connection handler."""
    await manager.connect(websocket)
    try:
        scheduler = websocket.app.state.scheduler
        while True:
            metrics = await scheduler.get_metrics()
            telemetry_data = {
                "event": "TELEMETRY_UPDATE",
                "data": {
                    "total_processes": metrics.total_processes,
                    "active_processes": metrics.active_processes,
                    "completed_tasks": metrics.completed_tasks,
                    "failed_tasks": metrics.failed_tasks,
                    "uptime_seconds": metrics.uptime_seconds
                }
            }
            await websocket.send_text(json.dumps(telemetry_data))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket stream error", error=str(e))
        manager.disconnect(websocket)
