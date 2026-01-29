from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ChemicalCategory(str, Enum):
    ACID = "Acid"
    BASE = "Base"
    METAL = "Metal"
    ORGANIC = "Organic"
    OXIDIZER = "Oxidizer"
    HALOGEN = "Halogen"
    SOLVENT = "Solvent"
    WATER_REACTIVE = "Water-Reactive"
    HEAVY_METAL = "Heavy-Metal"
    UNKNOWN = "Unknown"


class SubstanceProperties(BaseModel):
    ph_range: tuple[float, float] = (7.0, 7.0)
    flammable: bool = False
    oxidizer: bool = False
    water_reactive: bool = False
    toxicity: str = "Low"  # Low, Medium, High
    flash_point_c: Optional[float] = None


class SubstanceProfile(BaseModel):
    id: str
    name: str
    aliases: list[str] = []
    category: ChemicalCategory
    default_waste_stream: str
    properties: SubstanceProperties
    incompatible_with: list[str] = []  # List of category names
