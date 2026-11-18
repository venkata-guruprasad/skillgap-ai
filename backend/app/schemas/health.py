"""Pydantic schemas for health check endpoints."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    message: str


class DatabaseHealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    database: str
    message: str
