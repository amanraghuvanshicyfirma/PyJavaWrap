from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Sample Python API", version="1.0.0")

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True

class Item(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    # Mock data
    return User(id=user_id, username="jdoe", email="jdoe@example.com")

@app.post("/users/", response_model=User)
async def create_user(user: User):
    return user

@app.get("/items/", response_model=List[Item])
async def get_items():
    return [
        Item(id=1, name="Laptop", price=999.99),
        Item(id=2, name="Mouse", price=25.50)
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
