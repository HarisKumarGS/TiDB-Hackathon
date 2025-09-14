from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json

from ..services.websocket_service import websocket_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time crash notifications"""
    await websocket_manager.connect(websocket)
    
    try:
        # Send a welcome message
        welcome_message = {
            "type": "connection_established",
            "message": "Connected to Realtime Updates",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        await websocket_manager.send_personal_message(
            json.dumps(welcome_message), 
            websocket
        )
        
        # Keep the connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message from client (like ping/pong for keepalive)
                data = await websocket.receive_text()
                print(f"📨 Received message from client: {data}")
                logger.info(f"Received message from client: {data}")
                
                # Echo back for now (can be extended for client commands)
                if data == "ping":
                    await websocket_manager.send_personal_message("pong", websocket)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"❌ Error in WebSocket communication: {e}")
                logger.error(f"Error in WebSocket communication: {e}")
                break
                
    except WebSocketDisconnect:
        print("🔌 WebSocket disconnected normally")
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(websocket)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": len(websocket_manager.active_connections),
        "message": f"Currently {len(websocket_manager.active_connections)} active WebSocket connections"
    }
