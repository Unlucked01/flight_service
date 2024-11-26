import json
import logging

from confluent_kafka import Producer
from fastapi import FastAPI, HTTPException
from typing import List

from contextlib import asynccontextmanager
import asyncio

from models.fligh_ticket_model import FlightTicket
from models.mongodb_connector import collection
from models.redis_connector import redis, get_cache, set_cache

from models.kafka import start_kafka_producer, start_kafka_consumer, send_message


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

producer: Producer


@asynccontextmanager
async def lifespan(app):
    global producer
    producer = start_kafka_producer()
    consumer = start_kafka_consumer("object_confirmation_responses", "flight_service_group")
    consumer_task = asyncio.create_task(consume_user_updates(consumer))

    yield
    consumer_task.cancel()
    consumer.close()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Flight Ticket Sales API"}


@app.get("/tickets", response_model=List[FlightTicket])
async def get_all_tickets():
    tickets = await collection.find().to_list()
    return tickets


@app.get("/tickets/{ticket_id}", response_model=FlightTicket)
async def get_ticket(ticket_id: str):
    cache_key = f"ticket_{ticket_id}"
    cached_data = await get_cache(cache_key, redis)
    if cached_data:
        return cached_data

    ticket = await collection.find_one({"_id": ticket_id})
    if ticket:
        await set_cache(cache_key, ticket, redis)
        return ticket
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/tickets", response_model=FlightTicket)
async def create_ticket(ticket: FlightTicket):
    ticket_dict = ticket.model_dump(by_alias=True)

    try:
        result = await collection.insert_one(ticket_dict)
    except Exception as db_error:
        raise HTTPException(status_code=500, detail=f"Database error: {db_error}")

    ticket_dict["_id"] = str(result.inserted_id)

    message = {
        "user_id": ticket_dict["user_id"],
        "object_id": ticket_dict["_id"]
    }
    try:
        send_message(producer, "object_confirmation", message)
    except Exception as e:
        print(f"Failed to send Kafka message: {e}")

    return FlightTicket(**ticket_dict)


@app.put("/tickets/{ticket_id}", response_model=FlightTicket)
async def update_ticket(ticket_id: str, updated_ticket: FlightTicket):
    result = await collection.update_one({"_id": ticket_id}, {"$set": updated_ticket.model_dump(by_alias=True)})
    if result.modified_count == 1:
        updated_ticket_dict = await collection.find_one({"_id": ticket_id})

        await set_cache(f"ticket_{ticket_id}", updated_ticket_dict, redis)
        return updated_ticket_dict
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str):
    result = await collection.delete_one({"_id": ticket_id})
    if result.deleted_count == 1:
        await redis.delete(f"ticket_{ticket_id}")
        return {"message": "Ticket deleted successfully"}
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.delete("/tickets")
async def delete_all_tickets():
    result = await collection.delete_many({})
    return {"message": f"Deleted {result.deleted_count} tickets"}


@app.post("/test_kafka/{num_objects}")
async def test_kafka(num_objects: int):
    test_tickets = [
        {
            "flight_number": f"FL{i}",
            "passenger_name": f"Passenger {i}",
            "destination": f"Destination {i}",
            "price": i * 10.0,
            "user_id": i % 10

        } for i in range(1, num_objects + 1)
    ]

    created_tickets = []
    for ticket_data in test_tickets:
        ticket = FlightTicket(**ticket_data)
        try:
            created_ticket = await create_ticket(ticket)
            created_tickets.append(created_ticket)
            log.info(f"Ticket created and sent to Kafka: {created_ticket}")
        except Exception as e:
            log.error(f"Failed to create ticket: {ticket_data}. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create some tickets: {e}")

    return {"status": "Tickets sent to Kafka", "created_tickets": created_tickets}


async def consume_user_updates(consumer):
    while True:
        try:
            msg = await asyncio.to_thread(consumer.poll, timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                log.error(f"Consumer error: {msg.error()}")
                continue

            log.info(f"Received message: {msg.value().decode('utf-8')}")
            message = json.loads(msg.value().decode("utf-8"))

            object_id = message.get("object_id")
            user_id = message.get("user_id")
            timestamp = message.get("timestamp")

            if object_id and user_id:
                await collection.update_one(
                    {"_id": object_id},
                    {"$set": {"user_id": user_id, "timestamp": timestamp}}
                )
        except Exception as e:
            log.error(f"Error consuming Kafka message: {e}")


