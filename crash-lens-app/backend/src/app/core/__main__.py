import asyncio
import os

from src.app.core import error_analyzer_agent_executor
from dotenv import load_dotenv

load_dotenv()


async def main():
    print("init block")
    print("Os name")
    print(os.environ["AWS_SECRET_ACCESS_KEY"])
    print(error_analyzer_agent_executor.get_graph())
    res = await error_analyzer_agent_executor.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """
      Traceback (most recent call last):
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/main.py", line 7, in <module>
    from core.middleware import start_up_db
  File "/Users/hariskumargs/Documents/Personal/TiDB-Hackathon/sample-ecommerce-app/backend/core/middleware.py", line 48, in start_up_db
    raise DatabaseConnectionError
core.errors.DatabaseConnectionError

    crash id: 12345676""",
                }
            ]
        }
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
