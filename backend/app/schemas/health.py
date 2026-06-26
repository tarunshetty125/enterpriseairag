from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    application: str
    version: str
    environment: str
    timestamp: datetime


class ComponentHealth(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: str
    details: str


class SystemHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    application: str
    version: str
    environment: str
    components: list[ComponentHealth]
    timestamp: datetime
