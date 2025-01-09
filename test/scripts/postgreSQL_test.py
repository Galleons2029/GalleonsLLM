# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 14:20
# @Author  : Galleons
# @File    : postgreSQL_test.py

"""
这里是文件说明
"""
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5433/rag_test"
)
engine = create_engine(DATABASE_URL)

class HeroBase(SQLModel):
    name: str = Field(index=False)
    age: int | None = Field(default=None, index=False)

class Hero(HeroBase, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

class HeroPublic(HeroBase):
    id: int

class HeroCreate(HeroBase):
    secret_name: str

class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None

def create_db_and_tables():
    # 先删除所有表，然后重新创建
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

# Session将对象存储在内存中并跟踪数据中所需的任何更改，然后它使用engine与数据库通信。
def get_session():
    with Session(engine) as session:   # 为每个请求提供一个新的Session。这确保了我们每个请求使用一个会话。
        yield session

# 简化将使用此依赖项的其余代码。
SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 加载数据库
    create_db_and_tables()
    yield
    # Clean up the ML models and release the resources

app = FastAPI(lifespan=lifespan)

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    try:
        db_hero = Hero.model_validate(hero)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero
    except Exception as e:
        session.rollback()
        print(f"Error creating hero: {e}")
        raise


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    try:
        heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
        print(f"Found {len(heroes)} heroes")
        for hero in heroes:
            print(f"Hero: {hero.name}")
        return heroes
    except Exception as e:
        print(f"Error reading heroes: {e}")
        raise


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "postgreSQL_test:app",
        host="0.0.0.0",
        port=9013,
        reload=True,
    )