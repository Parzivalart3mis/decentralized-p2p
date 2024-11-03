from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dht import create_topic, delete_topic, subscribe, query_topic, forward_request
from utils import hash_topic
from config import HYPERCUBE_DIMENSIONS, peer_id

router = APIRouter()

class CreateTopicRequest(BaseModel):
    topic: str

class SubscribeRequest(BaseModel):
    topic: str

class QueryTopicRequest(BaseModel):
    topic: str

@router.post("/create_topic")
async def create_topic_endpoint(request: CreateTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await create_topic(topic)
    else:
        response = await forward_request(target_node, "create_topic", {"topic": topic})
        return response

@router.post("/delete_topic")
async def delete_topic_endpoint(request: CreateTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await delete_topic(topic)
    else:
        response = await forward_request(target_node, "delete_topic", {"topic": topic})
        return response

@router.post("/subscribe")
async def subscribe_topic_endpoint(request: SubscribeRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await subscribe(topic)
    else:
        response = await forward_request(target_node, "subscribe", {"topic": topic})
        return response

@router.post("/query_topic")
async def query_topic_endpoint(request: QueryTopicRequest):
    topic = request.topic
    target_node = format(hash_topic(topic), f'0{HYPERCUBE_DIMENSIONS}b')
    if target_node == peer_id:
        return await query_topic(topic)
    else:
        response = await forward_request(target_node, "query_topic", {"topic": topic})
        return response
