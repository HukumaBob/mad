from fastapi.testclient import TestClient
from public_api.main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from public_api.database import get_db
from public_api import models
import uuid


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределем функцию get_db для использования тестовой сессии
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def db_session():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)


client = TestClient(app)

@pytest.fixture(scope="function")
def prepare_data(db_session):
    print("Добавляем тестовый мем в базу данных")
    new_meme = models.Meme(text="Тестовый мем", image_url="http://test.com/test.jpg")
    db_session.add(new_meme)
    db_session.commit()
    print(f"Создан мем с ID: {new_meme.id}")
    return new_meme.id

def test_read_meme(prepare_data):
    meme_id = prepare_data
    response = client.get(f"/memes/{meme_id}")
    print(f"Ответ API для test_read_meme: {response.json()}")
    assert response.status_code == 200
    assert response.json()['id'] == meme_id

def test_read_memes(db_session):
    response = client.get("/memes")
    print(f"Ответ API для test_read_memes: {response.json()}")

    assert response.status_code == 200
    assert response.json() is not None


def test_create_meme():
    unique_image_url = f"http://test.com/{uuid.uuid4()}.jpg"
    test_meme_data = {
        "text": "Тестовый мем №2",
        "image_url": unique_image_url
    }
    response = client.post("/memes", json=test_meme_data)
    print(f"Ответ API для test_create_meme: {response.json()}")
    assert response.status_code == 200
    assert response.json()['text'] == "Тестовый мем №2"


def test_update_meme():
    unique_image_url = f"http://test.com/{uuid.uuid4()}.jpg"
    test_update_data = {
        "text": "Обновленный текст мема",
        "image_url": unique_image_url
    }
    response = client.put("/memes/1", json=test_update_data)
    print(f"Ответ API для test_update_meme: {response.json()}")
    assert response.status_code == 200
    assert response.json()['text'] == "Обновленный текст мема"

def test_delete_meme():
    response = client.delete("/memes/1")
    print(f"Ответ API для test_delete_meme: {response.json()}")
    assert response.json() == {"message": "Meme deleted successfully"}
