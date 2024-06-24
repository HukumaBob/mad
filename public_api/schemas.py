from pydantic import BaseModel, HttpUrl, field_validator
from PIL import Image

class MemeBase(BaseModel):
    text: str
    image_url: HttpUrl

    @field_validator("image_url")
    def validate_image_url(cls, value):
        extensions = str(value).split(".")[-1].lower()
        allowed_extensions = ["jpg", "jpeg", "png", "gif"]
        if extensions not in allowed_extensions:
            raise ValueError(
                f"Invalid image extension. Allowed extensions: "
                f"{', '.join(allowed_extensions)}"
                )
        return value        

class MemeCreate(MemeBase):
    pass

class MemeUpdate(MemeBase):
    pass

class Meme(MemeBase):
    id: int
