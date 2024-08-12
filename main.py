from fastapi import FastAPI, HTTPException
from models import Book, UpdateBook
from database import collection
from bson import ObjectId
from typing import List, Optional
from pymongo import ASCENDING, DESCENDING

app = FastAPI()

# Função utilitária para converter ObjectId para string
def book_serializer(book) -> dict:
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "published_year": book["published_year"],
        "genre": book.get("genre"),
        "description": book.get("description"),
    }

@app.post("/books/", response_model=Book)
def create_book(book: Book):
    result = collection.insert_one(book.model_dump())  # Inserir no MongoDB
    created_book = collection.find_one({"_id": result.inserted_id})  # Buscar o livro recém-criado
    return book_serializer(created_book)  # Retornar o livro com o ID incluído



@app.get("/books/", response_model=List[Book])
def get_books(limit: int = 10, skip: int = 0, sort_by: str = "title", order: str = "asc"):
    sort_order = ASCENDING if order == "asc" else DESCENDING
    books = collection.find().sort(sort_by, sort_order).skip(skip).limit(limit)
    return [book_serializer(book) for book in books]

@app.get("/books/search/", response_model=List[Book])
def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    published_year: Optional[int] = None,
    genre: Optional[str] = None,
    description: Optional[str] = None
):
    # Construindo a query dinâmica
    search_criteria = {}
    
    if title:
        search_criteria["title"] = {"$regex": title, "$options": "i"}
    if author:
        search_criteria["author"] = {"$regex": author, "$options": "i"}
    if published_year:
        search_criteria["published_year"] = published_year
    if genre:
        search_criteria["genre"] = {"$regex": genre, "$options": "i"}
    if description:
        search_criteria["description"] = {"$regex": description, "$options": "i"}

    # Executando a consulta no MongoDB
    books = collection.find(search_criteria)

    # Serializando os resultados
    result = [book_serializer(book) for book in books]

    if not result:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado.")

    return result


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: str):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return book_serializer(book)
    raise HTTPException(status_code=404, detail="Livro não encontrado.")

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: str, book: UpdateBook):
    update_data = {k: v for k, v in book.model_dump().items() if v is not None}
    result = collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})
    if result.modified_count:
        updated_book = collection.find_one({"_id": ObjectId(book_id)})
        return book_serializer(updated_book)
    raise HTTPException(status_code=404, detail="Livro não encontrado ou sem mudanças.")

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    result = collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count:
        return {"message": "Livro excluído com sucesso"}
    raise HTTPException(status_code=404, detail="Livro não encontrado.")
