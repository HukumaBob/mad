import os
import uuid
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio
from minio.error import S3Error
import shutil
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv("MINIO_BUCKET")
minio_endpoint=os.getenv("MINIO_ENDPOINT")

app = FastAPI()

minio_client = Minio(
    endpoint=minio_endpoint,
    access_key=os.getenv("MINIO_ACCESS"),
    secret_key=os.getenv("MINIO_SECRET"),
)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    destination_file_name = file.filename
    unique_filename = f"{uuid.uuid4()}_{destination_file_name}"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    with NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    minio_client.fput_object(bucket_name, unique_filename, temp_file_path)

    os.remove(temp_file_path)

    file_url = f"https://{minio_endpoint}/{bucket_name}/{unique_filename}"
    return {"file_url": file_url}


@app.get("/retrieve/{filename}")
async def get_file(filename: str):    
    try:
        data = minio_client.get_object(bucket_name, filename)
        return StreamingResponse(data.stream(32*1024), media_type="image/jpeg")
    except S3Error as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/delete/{filename}")
async def delete_file(filename: str):
    try:
        minio_client.remove_object(bucket_name, filename)
        return {"message": "File deleted successfully"}
    except S3Error as e:
        raise HTTPException(status_code=404, detail=str(e))
