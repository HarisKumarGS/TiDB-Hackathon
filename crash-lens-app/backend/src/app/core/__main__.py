import asyncio
import os

from src.app.core import error_analyzer_agent_executor
from dotenv import load_dotenv

load_dotenv()


async def main():
    print("init block")
    print("Os name")
    print(error_analyzer_agent_executor.get_graph())
    res = await error_analyzer_agent_executor.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """
      Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/api/endpoints/cart.py", line 82, in checkout
    return await cart_service.checkout(data_obj, current_user)
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/services/cart_service.py", line 130, in checkout
    return await self.paystack.initialize_payment(
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/paystack.py", line 35, in initialize_payment
    rsp = await self.client.post(
  File "/usr/local/lib/python3.11/site-packages/httpx/_client.py", line 1778, in _send_single_request
    raise httpx.ConnectTimeout("Timed out while connecting to Paystack")
httpx.ConnectTimeout: Timed out while connecting to Paystack

    crash id: 12345676 
    repository id: 1fcca1b6-a577-43e6-bed4-ad3ac98d751b
    repository url: https://github.com/HarisKumarGS/sample-ecommerce-application
    """,
                }
            ]
        }
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
