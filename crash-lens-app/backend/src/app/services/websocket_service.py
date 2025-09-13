import json
import asyncio
from typing import Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket connection manager for real-time crash notifications"""
    
    def __init__(self):
        # Store active connections - simplified to just broadcast to all
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ Error sending personal message: {e}")
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            print("⚠️ No active connections to broadcast to")
            return
            
        print(f"📡 Broadcasting to {len(self.active_connections)} connections")
        disconnected = set()
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"❌ Error broadcasting to connection: {e}")
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def send_crash_notification(self, crash_data: dict):
        """Send a crash notification to all connected clients - simplified version"""
        notification = {
            "id": crash_data.get("crash_id", "unknown"),
            "type": "crash_detected",
            "message": crash_data.get("title", "Crash detected"),
            "severity": crash_data.get("severity", "Medium").title(),
            "repositoryName": crash_data.get("repository_name", "Unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "component": crash_data.get("component", "UNKNOWN"),
            "error_type": crash_data.get("error_type", "UNKNOWN"),
            "users_impacted": crash_data.get("users_impacted", 0)
        }
        
        message = json.dumps(notification)
        
        # Always broadcast to all connections - no repository filtering
        await self.broadcast(message)
        
        print(f"✅ Sent crash notification: {notification['id']}")
        logger.info(f"Sent crash notification: {notification['id']}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
