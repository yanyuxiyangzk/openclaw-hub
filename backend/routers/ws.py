from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.agent import Agent

router = APIRouter(tags=["websockets"])


@router.websocket("/ws/agents/{agent_id}/status")
async def ws_agent_status(websocket: WebSocket, agent_id: str):
    """WS /ws/agents/{id}/status - Agent Status WebSocket (T-235)"""
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                status_data = {
                    "id": agent.id,
                    "status": agent.status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                status_data = {
                    "id": agent_id,
                    "status": "unknown",
                    "error": "Agent not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            await websocket.send_json(status_data)
            import asyncio
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
