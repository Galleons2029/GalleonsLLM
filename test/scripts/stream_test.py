import httpx
import asyncio

async def fetch_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream(
                # "POST", "http://127.0.0.1:9011/api/prompt/stream",
                "POST", "http://127.0.0.1:9011/v1/chat/completions/stream",
                json={
                          "collections": [
                            "zsk_1"
                          ],
                          "messages": [
                            {
                              "content": "You are a helpful assistant.",
                              "role": "user"
                            }
                          ],
                          "model": "qwen2-pro",
                          "stream": True,
                          "temperature": 1
                        }
                ) as response:
            async for line in response.aiter_text():
                print(line, end="")


async def origin_fetch_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream(
                "POST", "http://127.0.0.1:8000/prompt/stream",
                json={"message": "Write me 3 paragraph poem about why the sky is blue"}
                ) as response:
            async for line in response.aiter_text():
                print(line, end="")

if __name__ == "__main__":
    # asyncio.run(origin_fetch_stream())
    asyncio.run(fetch_stream())

