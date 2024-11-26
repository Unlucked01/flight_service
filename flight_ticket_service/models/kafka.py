import json
from confluent_kafka import Producer, Consumer, KafkaException


KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"


def start_kafka_producer() -> Producer:
    try:
        producer_config = {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        }
        producer = Producer(producer_config)
        print("Kafka producer started")
        return producer
    except KafkaException as e:
        print(f"Kafka producer error: {e}")
        raise e


def start_kafka_consumer(topic: str, group_id: str) -> Consumer:
    try:
        consumer_config = {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe([topic])
        print("Kafka consumer started")
        return consumer
    except KafkaException as e:
        print(f"Kafka consumer error: {e}")
        raise e


def send_message(producer, topic: str, message: dict):
    try:
        producer.produce(topic, json.dumps(message).encode("utf-8"))
        producer.flush()
    except KafkaException as e:
        print(f"Error sending message to Kafka: {e}")
        raise e
