from motor.motor_asyncio import AsyncIOMotorClient


try:
    client = AsyncIOMotorClient("mongodb://mongo:27017")
    db = client.user_db
    collection = db.users
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

