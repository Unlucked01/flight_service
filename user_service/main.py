import logging
from contextlib import asynccontextmanager
from datetime import datetime

from confluent_kafka import Producer, Consumer
from fastapi import FastAPI, HTTPException
from typing import List
import asyncio
import json

from models.mongodb_connector import collection
from models.user_model import User
from models.kafka import start_kafka_producer, start_kafka_consumer, send_message

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

producer: Producer


@asynccontextmanager
async def lifespan(app):
    global producer

    producer = start_kafka_producer()
    consumer = start_kafka_consumer("object_confirmation", "user_service_group")

    consumer_task = asyncio.create_task(consume_object_messages(consumer))

    yield

    consumer_task.cancel()
    consumer.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the User Service API API"}


@app.post("/users", response_model=User)
async def create_user(user: User):
    user_data = user.model_dump(by_alias=True)
    try:
        result = await collection.insert_one(user_data)
    except Exception:
        raise HTTPException(status_code=409, detail=f"User already exists")
    user_data["_id"] = int(result.inserted_id)
    return user_data


@app.get("/users", response_model=List[User])
async def get_all_users():
    users = await collection.find().to_list()
    return users


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = await collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    result = await collection.delete_one({"_id": user_id})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    result = await collection.update_one({"_id": user_id}, {"$set": user.model_dump(by_alias=True)})
    if result.modified_count == 1:
        return await collection.find_one({"_id": user_id})
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users")
async def delete_all_users():
    result = await collection.delete_many({})
    return {"message": f"Deleted {result.deleted_count} users"}


async def consume_object_messages(consumer: Consumer):
    while True:
        try:
            msg = await asyncio.to_thread(consumer.poll, 1.0)

            if msg is None:
                continue
            if msg.error():
                log.error(f"Kafka Consumer error: {msg.error()}")
                continue

            log.info(f"Received message from consumer: {msg.value().decode('utf-8')}")
            message = json.loads(msg.value().decode("utf-8"))

            user_id = message.get("user_id")
            object_id = message.get("object_id")

            if user_id and object_id:
                user = await collection.find_one({"_id": user_id})
                if not user:
                    await collection.insert_one({"_id": user_id, "registered_objects": 1})
                else:
                    await collection.update_one({"_id": user_id}, {"$inc": {"registered_objects": 1}})

            response_message = {"object_id": object_id,
                                "user_id": user_id,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            send_message(producer, "object_confirmation_responses", response_message)

        except Exception as e:
            log.error(f"Error while consuming messages: {e}")
