from pydantic import BaseModel
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "Safe"
    CAUTION = "Caution"
    DANGER = "Danger"


class RouteRequest(BaseModel):
    substance: str
    quantity_ml: float
    concentration: str = "Pure"


class RoutedContainer(BaseModel):
    container_id: str
    location: str
    current_fill_percent: float
    after_fill_percent: float
    days_until_deadline: Optional[int] = None


class ClassificationResult(BaseModel):
    category: str
    waste_stream: str


class RouteResponse(BaseModel):
    success: bool
    substance: str
    classified_as: ClassificationResult
    routed_to: Optional[RoutedContainer] = None
    safety_status: RiskLevel
    message: str
    warnings: list[str] = []


class DisposalResponse(BaseModel):
    success: bool
    container_id: str
    new_fill_ml: float
    fill_percent: float
    logged_at: str
