from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dht import publish_message, pull_messages, forward_request
from utils import hash_topic
from config import HYPERCUBE_DIMENSIONS, peer_id

router = APIRouter()

class PublishMessageRequest(BaseModel):
    topic: str
    message: str

class PullMessagesRequest(BaseModel):
    topic: str

@router.post("/publish_message")
async def publish_message_endpoint(request: PublishMessageRequest):
    topic = request.topic
    message = request.message
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await publish_message(topic, message)
    else:
        response = await forward_request(target_node, "publish_message", {"topic": topic, "message": message})
        return response

@router.post("/pull_messages")
async def pull_messages_endpoint(request: PullMessagesRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await pull_messages(topic)
    else:
        response = await forward_request(target_node, "pull_messages", {"topic": topic})
        return response
