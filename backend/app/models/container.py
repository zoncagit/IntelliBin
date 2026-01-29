from pydantic import BaseModel
from typing import Optional
from enum import Enum


class WasteStream(str, Enum):
    AQUEOUS_ACID = "AqueousAcid"
    AQUEOUS_BASE = "AqueousBase"
    HALOGENATED_SOLVENT = "HalogenatedSolvent"
    NON_HALOGENATED_SOLVENT = "NonHalogenatedSolvent"
    OXIDIZER = "Oxidizer"
    REACTIVE_METAL = "ReactiveMetal"
    HEAVY_METAL = "HeavyMetal"
    FLAMMABLE = "Flammable"
    CORROSIVE = "Corrosive"
    GENERAL = "GeneralChemical"


class ContainerStatus(str, Enum):
    ACTIVE = "Active"
    FULL = "Full"
    AWAITING_PICKUP = "AwaitingPickup"
    EMPTY = "Empty"


class ContainerContent(BaseModel):
    substance: str
    category: str
    quantity_ml: float
    concentration: str
    added_at: str  # ISO format datetime string


class WasteContainer(BaseModel):
    container_id: str
    waste_stream: WasteStream
    location: str
    capacity_ml: float
    current_fill_ml: float
    contents: list[ContainerContent] = []
    accumulation_start: Optional[str] = None
    pickup_deadline: Optional[str] = None
    status: ContainerStatus = ContainerStatus.EMPTY
