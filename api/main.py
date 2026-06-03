import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop


servers: dict[int, Server] = {}
next_server_id = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    poll_task = asyncio.create_task(run_poll_loop(servers))
    try:
        yield
    finally:
        poll_task.cancel()
        try:
            await poll_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="DevOps Monitoring API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> dict:
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def stream_metrics(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@app.post("/servers", response_model=ServerOut, status_code=201)
async def create_server(
    server_in: ServerIn,
    _: Annotated[str, Depends(verify_api_key)],
) -> ServerOut:
    global next_server_id

    server = Server(
        id=next_server_id,
        name=server_in.name,
        host=server_in.host,
        port=server_in.port,
    )
    servers[server.id] = server
    next_server_id += 1
    return ServerOut.from_server(server)


@app.get("/servers", response_model=list[ServerOut])
async def list_servers(status: str | None = None) -> list[ServerOut]:
    result = list(servers.values())
    if status is not None:
        result = [server for server in result if server.status == status]
    return [ServerOut.from_server(server) for server in result]


@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: int) -> ServerOut:
    server = servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerOut.from_server(server)


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(
    server_id: int,
    _: Annotated[str, Depends(verify_api_key)],
) -> None:
    if server_id not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    del servers[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def check_server(server_id: int) -> ServerOut:
    server = servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")

    await poll_server(server.id, server.base_url(), servers)
    return ServerOut.from_server(server)
