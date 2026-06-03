from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class Server:
    """Monitored server stored in memory."""

    id: int
    name: str
    host: str
    port: int
    status: str = "unknown"

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Request body used to register a new server."""

    name: str = Field(..., min_length=1)
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)


class ServerOut(BaseModel):
    """Response model returned by the API."""

    id: int
    name: str
    host: str
    port: int
    status: str

    @classmethod
    def from_server(cls, server: Server) -> "ServerOut":
        return cls(
            id=server.id,
            name=server.name,
            host=server.host,
            port=server.port,
            status=server.status,
        )
