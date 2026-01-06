from enum import Enum
from typing import Annotated
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

class ModelName(str, Enum):
	alexnet = "alexnet"
	resnet = "resnet"
	vgg16 = "vgg16"

class Item(BaseModel):
	name: str
	description: str | None = None
	price: float
	tax: float | None = None

app = FastAPI()

@app.get('/')
def root():
    return {"message" : "Hello World"}


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
	if model_name is ModelName.alexnet:
		return {"model_name": model_name, "message": "Deep Learning FTW!"}

	if model_name.value == "resnet":
		return {"model_name": model_name, "message": "LeCNN all the images"}

	return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}


@app.post("/items/{item_id}")
def update_item(item_id: Annotated[int, Path(gt=0)], item: Item, q: Annotated[str | None, Query(max_length=50)] = None):
    result = {"item_id": item_id, **item.model_dump()}
    
    if q:
        result.update({"q": q})
    return result