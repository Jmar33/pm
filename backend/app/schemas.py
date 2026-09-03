from pydantic import BaseModel, Field


class ColumnUpdate(BaseModel):
    title: str = Field(min_length=1)


class CardCreate(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    details: str = ""
    column_id: str = Field(min_length=1)


class CardUpdate(BaseModel):
    title: str = Field(min_length=1)
    details: str = ""


class CardMove(BaseModel):
    column_id: str = Field(min_length=1)
    position: int = Field(ge=0)
