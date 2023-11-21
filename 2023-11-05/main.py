import asyncio
import uvicorn

from functools import wraps
from time import monotonic
from fastapi import FastAPI
from pydantic import BaseModel


DELAY_SEC = 3


app = FastAPI()
lock = asyncio.Lock()


class TestResponse(BaseModel):
    elapsed: float


def scheduler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with lock:
            result = await func(*args, **kwargs)
        return result
    return wrapper


@scheduler
async def work() -> None:
    await asyncio.sleep(DELAY_SEC)


@app.get("/test")
async def handler() -> TestResponse:
    start_time = monotonic()
    await work()
    elapsed = monotonic() - start_time
    return TestResponse(elapsed=elapsed)


def main():
    print(f'INFO:     Documentation is available at - '
          f'http://127.0.0.1:5000/docs')

    uvicorn.run("task:app",
                host="127.0.0.1",
                port=5000
                )


if __name__ == '__main__':
    main()
