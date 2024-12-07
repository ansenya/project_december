from api.database import Base
from sqlalchemy import Column, Integer, String


class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String)
    party_number = Column(Integer)
    party_type = Column(String)
    at_fault = Column(Integer)
    party_sex = Column(String)
    party_age = Column(Integer)
    party_sobriety = Column(String)
    party_drug_physical = Column(String)
    direction_of_travel = Column(String)


class Case(Base):
    __tablename__ = "case_ids"

    case_id = Column(Integer, primary_key=True, index=True)
    db_year = Column(Integer)
