import pytest

from asyncio import gather, create_task
from httpx import AsyncClient
from main import app as fastapi_app, DELAY_SEC


async def worker() -> float:
    async with AsyncClient(
            app=fastapi_app,
            base_url="http://test"
    ) as client:
        response = await client.get(
            url="/test",
            params={}
        )
    return response.json()['elapsed']


async def parallel_survey_result(
        samples_number=10,
) -> list[float]:
    tasks = [
        create_task(worker())
        for _ in range(samples_number)
    ]

    return list(await gather(*tasks))


@pytest.mark.asyncio
async def test_test():
    total_time = 0.0

    for r in await parallel_survey_result():
        assert r >= total_time + DELAY_SEC
        total_time += DELAY_SEC
