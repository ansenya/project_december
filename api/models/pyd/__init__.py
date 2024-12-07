from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar('T')


class TableInfo(BaseModel):
    table_name: str
    description: str


class Page(BaseModel, Generic[T]):
    data: List[T]
    total_pages: int
    has_more: bool

    class Config:
        orm_mode = True


class Party(BaseModel):
    id: int
    case_id: str
    party_number: int
    party_type: str
    at_fault: int
    party_sex: str
    party_age: int
    party_sobriety: str
    party_drug_physical: str

    class Config:
        orm_mode = True


class VehicleDistributionModel(BaseModel):
    case_id: str
    vehicle_year: int

    class Config:
        orm_mode = True


class PartyData(BaseModel):
    age: float
    sex: str
    race: str
