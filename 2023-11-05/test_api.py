import pytest

from asyncio import gather, create_task
from httpx import AsyncClient
from main import app as fastapi_app, DELAY_SEC


async def get_elapsed_from_api() -> float:
    async with AsyncClient(
            app=fastapi_app,
            base_url="http://test"
    ) as client:
        response = await client.get(
            url="/test",
            params={}
        )
    return response.json()['elapsed']


@pytest.fixture(scope="session")
async def get_parallel_request(
        samples_number=10,
) -> list[float]:
    tasks = [
        create_task(get_elapsed_from_api())
        for _ in range(samples_number)
    ]

    return list(await gather(*tasks))


@pytest.mark.asyncio
async def test_test(get_parallel_request):
    total_time = 0.0

    for r in await get_parallel_request:
        assert r >= total_time + DELAY_SEC
        total_time += DELAY_SEC
