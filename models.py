from pydantic import BaseModel, Field
from typing import Optional

class Book(BaseModel):
    id: Optional[str] = None  # Campo id opcional
    title: str = Field(..., example="O Alquimista")
    author: str = Field(..., example="Paulo Coelho")
    published_year: int = Field(..., example=1988)
    genre: Optional[str] = Field(None, example="Ficção")
    description: Optional[str] = Field(None, example="Um romance sobre a jornada de um jovem pastor.")

class UpdateBook(BaseModel):
    title: Optional[str] = Field(None, example="O Alquimista")
    author: Optional[str] = Field(None, example="Paulo Coelho")
    published_year: Optional[int] = Field(None, example=1988)
    genre: Optional[str] = Field(None, example="Ficção")
    description: Optional[str] = Field(None, example="Um romance sobre a jornada de um jovem pastor.")
