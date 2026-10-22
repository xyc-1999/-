"""API 子路由聚合器。"""
from fastapi import APIRouter

from app.api.routes import agent, chat_events, health, knowledge, session, tickets

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(chat_events.router, tags=["chat"])  # -> /api/v1/chat