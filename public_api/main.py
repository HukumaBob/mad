from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from public_api import models, schemas
from public_api.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/memes", response_model=list[schemas.Meme])
def read_memes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    memes = db.query(models.Meme).offset(skip).limit(limit).all()
    return memes

@app.get("/memes/{meme_id}", response_model=schemas.Meme)
def read_meme(meme_id: int, db: Session = Depends(get_db)):
    meme = db.query(models.Meme).filter(models.Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    return meme

@app.post("/memes", response_model=schemas.Meme)
def create_meme(meme: schemas.MemeCreate, db: Session = Depends(get_db)):
    new_meme = models.Meme(text=meme.text, image_url=str(meme.image_url))
    db.add(new_meme)
    db.commit()
    db.refresh(new_meme)
    return new_meme

@app.put("/memes/{meme_id}", response_model=schemas.Meme)
def update_meme(meme_id: int, meme: schemas.MemeUpdate, db: Session = Depends(get_db)):
    existing_meme = db.query(models.Meme).filter(models.Meme.id == meme_id).first()
    if not existing_meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    update_data = jsonable_encoder(meme, exclude_unset=True)
    if 'image_url' in update_data:
        update_data['image_url'] = str(update_data['image_url'])

    for key, value in update_data.items():
        setattr(existing_meme, key, value)

    db.commit()
    db.refresh(existing_meme)
    return existing_meme

@app.delete("/memes/{meme_id}")
def delete_meme(meme_id: int, db: Session = Depends(get_db)):
    meme = db.query(models.Meme).filter(models.Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    db.delete(meme)
    db.commit()
    return {"message": "Meme deleted successfully"}
