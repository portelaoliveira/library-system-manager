Como treinamento, vamos construir uma pequena aplicação utilizando FastAPI e MongoDB com o objetivo de abordar os principais conceitos dessas tecnologias. A aplicação será uma API que gerencia um sistema de biblioteca, onde será possível cadastrar, buscar, atualizar e excluir livros. Vamos também implementar funcionalidades como pesquisa (com regex), ordenação (sorting) e validação com schemas.

### Passo 1: Preparar o Ambiente

Primeiro, vamos preparar nosso ambiente. Certifique-se de ter o Python instalado. Em seguida, vamos instalar as bibliotecas necessárias:

```bash
pip install fastapi uvicorn pymongo pydantic
```

### Passo 2: Configurar o MongoDB

Você precisará de um banco de dados MongoDB. Você pode usar uma instância local ou uma instância em nuvem como MongoDB Atlas. Vamos assumir que temos uma conexão MongoDB rodando na `localhost` na porta `27017`.

### Passo 3: Criar o Projeto FastAPI

Vamos criar a estrutura básica do projeto:

```
my_library/
├── main.py
├── models.py
└── database.py
```

### Passo 4: Configurar a Conexão com o MongoDB (`database.py`)

Aqui, vamos configurar a conexão com o MongoDB:

```python
from pymongo import MongoClient

# Configuração da conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.my_library_db  # Nome do banco de dados
collection = db.books  # Nome da coleção (tabela)

# Dropar o banco de dados inteiro
# client.drop_database("my_library_db")
```

### Passo 5: Criar os Schemas e Modelos (`models.py`)

Vamos criar os modelos e schemas usando Pydantic para validação de dados:

```python
from typing import Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    id: Optional[str] = None  # Campo id opcional
    title: str = Field(..., example="O Alquimista")
    author: str = Field(..., example="Paulo Coelho")
    published_year: int = Field(..., example=1988)
    genre: Optional[str] = Field(None, example="Ficção")
    description: Optional[str] = Field(
        None, example="Um romance sobre a jornada de um jovem pastor."
    )

class UpdateBook(BaseModel):
    title: Optional[str] = Field(None, example="O Alquimista")
    author: Optional[str] = Field(None, example="Paulo Coelho")
    published_year: Optional[int] = Field(None, example=1988)
    genre: Optional[str] = Field(None, example="Ficção")
    description: Optional[str] = Field(
        None, example="Um romance sobre a jornada de um jovem pastor."
    )

```

### Passo 6: Implementar as Rotas da API (`main.py`)

Agora, vamos implementar as rotas da API para CRUD, pesquisa e ordenação.

```python
from typing import List, Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pymongo import ASCENDING, DESCENDING

from database import collection
from models import Book, UpdateBook

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
    created_book = collection.find_one(
        {"_id": result.inserted_id}
    )  # Buscar o livro recém-criado
    return book_serializer(created_book)  # Retornar o livro com o ID incluído


@app.get("/books/", response_model=List[Book])
def get_books(
    limit: int = 10, skip: int = 0, sort_by: str = "title", order: str = "asc"
):
    sort_order = ASCENDING if order == "asc" else DESCENDING
    books = collection.find().sort(sort_by, sort_order).skip(skip).limit(limit)
    return [book_serializer(book) for book in books]


@app.get("/books/search/", response_model=List[Book])
def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    published_year: Optional[int] = None,
    genre: Optional[str] = None,
    description: Optional[str] = None,
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
```

### Passo 7: Executar a Aplicação

Para rodar a aplicação, use o comando abaixo:

```bash
uvicorn main:app --reload
```

### Explicação Passo a Passo:

1. **Conexão com o MongoDB**: Configuramos a conexão com o MongoDB no arquivo `database.py` usando `pymongo`.

2. **Schemas e Validação**: No arquivo `models.py`, criamos os schemas para validação de entrada de dados usando Pydantic.

3. **CRUD**: Implementamos as operações CRUD (Create, Read, Update, Delete) em `main.py`.

4. **Pesquisa com Regex**: Implementamos uma rota `/books/search/` para buscar livros pelo título usando expressões regulares.

5. **Ordenação e Paginação**: A rota `/books/` permite ordenar os livros por qualquer campo e aplicar paginação usando os parâmetros `limit` e `skip`.

### Passo 8: Melhorias Finais

- **Autenticação**: Em uma aplicação real, você pode adicionar autenticação usando JWT para proteger as rotas.
- **Testes Unitários**: Adicionar testes unitários usando `pytest` e `httpx` para garantir a robustez do sistema.
- **Deploy**: Para produção, você pode utilizar o Docker para containerizar a aplicação e fazer o deploy em serviços como AWS, Heroku ou Azure.

Este projeto serve como uma base sólida para criar APIs mais complexas e robustas, utilizando FastAPI e MongoDB.