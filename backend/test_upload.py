import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open("test.txt", "rb") as f:
            res = await client.post("http://localhost:8000/upload", files={"file": f})
            print(res.status_code)
            print(res.text)

asyncio.run(main())
