import asyncio

import httpx

from api.models import Server


async def poll_server(server_id: int, url: str, store: dict[int, Server]) -> None:
    """Check one server and update its status in the shared store."""
    server = store.get(server_id)
    if server is None:
        return

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
        server.status = "UP" if response.status_code == 200 else "DEGRADED"
    except httpx.HTTPError:
        server.status = "DOWN"


async def run_poll_loop(store: dict[int, Server], interval: int = 10) -> None:
    """Continuously check all registered servers in the background."""
    while True:
        checks = [
            poll_server(server.id, server.base_url(), store)
            for server in list(store.values())
        ]
        if checks:
            await asyncio.gather(*checks)
        await asyncio.sleep(interval)
