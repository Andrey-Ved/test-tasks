import asyncio
import uvicorn

from functools import wraps
from time import monotonic
from fastapi import FastAPI
from pydantic import BaseModel


DELAY_SEC = 3
SAMPLES_NUMBER = 10


app = FastAPI()
lock = asyncio.Lock()


class TestResponse(BaseModel):
    elapsed: float


class Report(BaseModel):
    delay_sec: float
    samples_number: int
    minimum_time: float
    average_time: float


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


@app.get("/test_test")
async def tests_handler() -> Report:
    start_time = monotonic()

    tasks = [
        asyncio.create_task(handler())
        for _ in range(SAMPLES_NUMBER)
    ]
    minimum_time = DELAY_SEC * 10 ** 3

    for r in await asyncio.gather(*tasks):
        if minimum_time > r.elapsed:
            minimum_time = r.elapsed

    average_time = (monotonic() - start_time) / SAMPLES_NUMBER

    return Report(
        delay_sec=DELAY_SEC,
        samples_number=SAMPLES_NUMBER,
        minimum_time=minimum_time,
        average_time=average_time,
    )


def main():
    print(f'INFO:     Documentation is available at - '
          f'http://127.0.0.1:5000/docs')

    uvicorn.run("task:app",
                host="127.0.0.1",
                port=5000
                )


if __name__ == '__main__':
    main()
