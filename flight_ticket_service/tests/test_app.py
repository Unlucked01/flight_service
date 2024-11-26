import time

import pytest
from httpx import AsyncClient, ASGITransport
from flight_ticket_service.main import app


# @pytest.mark.asyncio(loop_scope="module")
# async def test_cash_elements():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         num_tickets = 1000000
#         await client.delete("/tickets")
#
#         test_tickets = [
#             {
#                 "flight_number": f"FL{i}",
#                 "passenger_name": f"Passenger {i}",
#                 "destination": f"Destination {i}",
#                 "price": i * 10.0
#             } for i in range(num_tickets)
#         ]
#         for ticket in test_tickets:
#             response = await client.post("/tickets", json=ticket)
#             assert response.status_code == 200
#
#         start_time_no_cache = time.time()
#         response_no_cache = await client.get("/tickets")
#         time_no_cache = time.time() - start_time_no_cache
#         assert response_no_cache.status_code == 200
#         assert len(response_no_cache.json()) == num_tickets
#
#         start_time_with_cache = time.time()
#         response_with_cache = await client.get("/tickets")
#         time_with_cache = time.time() - start_time_with_cache
#         assert response_with_cache.status_code == 200
#         assert len(response_with_cache.json()) == num_tickets
#
#         print(f"\nTime without cache: {time_no_cache:.2f} seconds")
#         print(f"Time with cache: {time_with_cache:.2f} seconds")
#         assert time_with_cache < time_no_cache
#
#         await client.delete("/tickets")



# @pytest.mark.asyncio(loop_scope="module")
# async def test_add_100_elements():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         await client.delete('/tickets')
#         for i in range(100):
#             response = await client.post("/tickets", json={
#                 "flight_number": f"FL{i}",
#                 "passenger_name": f"Passenger {i}",
#                 "destination": f"Destination {i}",
#                 "price": float(i * 10)
#             })
#             assert response.status_code == 200
#             data = response.json()
#
#             assert "_id" in data
#
#         response = await client.get("/tickets")
#         assert response.status_code == 200
#         tickets = response.json()
#         assert len(tickets) == 100


# @pytest.mark.asyncio(loop_scope="module")
# async def test_add_100000_elements():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         elems = 100000
#         for i in range(elems):
#             response = await client.post("/tickets", json={
#                 "flight_number": f"FL{i}",
#                 "passenger_name": f"Passenger {i}",
#                 "destination": f"Destination {i}",
#                 "price": float(i * 10)
#             })
#             assert response.status_code == 200
#             data = response.json()
#             assert "_id" in data
#
#         response = await client.get("/tickets")
#         assert response.status_code == 200
#         tickets = response.json()
#         assert len(tickets) == elems + 100


# @pytest.mark.asyncio(loop_scope="module")
# async def test_delete_all_elements():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
#         response = await client.get("/tickets")
#         tickets = response.json()
#         for ticket in tickets:
#             response = await client.delete(f"/tickets/{ticket['_id']}")
#             assert response.status_code == 200
#             assert response.json() == {"message": "Ticket deleted successfully"}
#
#         response = await client.get("/tickets")
#         assert response.status_code == 200
#         tickets = response.json()
#         assert len(tickets) == 0
#

