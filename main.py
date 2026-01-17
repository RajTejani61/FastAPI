from enum import Enum
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
import json
from fastapi import (
    FastAPI,
    Header, 
    Query, 
    Path, 
    HTTPException, 
    Cookie, 
    APIRouter,
    Response
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse

class Gender(Enum):
	MALE = "male"
	FEMALE = "female"

class Department(Enum):
    COMPUTER_SCIENCE = "computer science"
    MATHEMATICS = "Mathematics"
    PHYSICS = "Physics"


class Student(BaseModel):
    id : str = Field(description="ID of student", examples=['S001'])
    name: str = Field(min_length=3, max_length=50, examples=['Abc'])
    age: int = Field(gt=17, lt=100, examples=[18])
    gender: Gender
    department: Department
    email: EmailStr = Field(description="Email of student", examples=["abc123@gmail.com"])
    password: str = Field(min_length=8, max_length=50)
    height : Annotated[float, Field(gt=0, description="Height of student in meters")] 
    weight : Annotated[float, Field(gt=0, description="Height of student in kgs")] 
    
    @field_validator("email")
    @classmethod
    def email_validator(cls, value):
        valid_domains = ["gmail.com", "student.com"]
        
        #abe@gmail.com
        domain_name = value.split('@')[-1]
        
        if domain_name not in valid_domains:
            raise HTTPException(status_code=400, detail="Email domain must be gmail.com or student.com")
        
        return value
    
    @computed_field
    @property
    def confirm_password(self) -> str:
        confirm_pass = self.password
        return confirm_pass
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2), 2)
        return bmi

class Cookies(BaseModel):    
    st_id : str | None = None
    st_name : str | None = None
    st_age : int | None = None


def load_data():
    with open("data.json", 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("data.json", 'w') as f:
        json.dump(data, f)


student_router = APIRouter(
    prefix="/student",
    tags=["Student"]
)

app = FastAPI()


@app.get('/')
def root():
    return {"message" : "Welcome to ABC College"}


@student_router.get("/view/")
def view_all(
    cookies: Annotated[Cookies, Cookie()] = None, # type: ignore
    accept_encoding : Annotated[str | None,  Header()] = None
    ):
    data = load_data()
    return {
        "data" : data, 
        "cookies" : cookies,
        "accept_encoding" : accept_encoding 
        }


@student_router.get("/view/{student_id}", )
def get_student_record(student_id: Annotated[str, Path(title="View Student data", description="ID of the student", examples=["S001"])]):
    data = load_data()
    if student_id in data:
        return {"message" : "Student Retrieved Successfully", "student_id": student_id, "student": data[student_id]}
    raise HTTPException(status_code=404, detail="Student record not found")


@student_router.get("/sort/")
def sort_data(
    sort_by: Annotated[str, Query(description="Sort on the basis of name, age, department")] = "name", 
    order: Annotated[str, Query(description="Sort in asc or in desc order")] = "asc"
    ):
    
    valid_fields = ["name", "age", "department"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field selct from {valid_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Select order between asc and desc")
    
    data = load_data()
    
    sorted_data = sorted(data.values(), key=lambda x : x.get(sort_by, 0), reverse = True if order == "desc" else False)
    
    return sorted_data

    
@student_router.post("/add")
def add_student(student: Student):
    data = load_data()
    
    if student.id in data:
        raise HTTPException(status_code=400, detail="Record already exists..")
    
    data[student.id] = student.model_dump(exclude={"id"}, mode="json")
    
    save_data(data)
    
    return "Recoed Added successfully"         

app.include_router(student_router)


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})

@app.put("/update/{id}")
def update_student(id: str, student: Student):
    data = load_data()
    
    if id not in data:
        raise HTTPException(status_code=404, detail="Record not found")
    
    data[id] = student.model_dump(exclude={'id'}, mode="json")
    
    save_data(data)
    
    return "Record updated successfully"


@app.delete("/delete/{id}")
def delete_student(id: str):
    data = load_data()
    
    if id not in data:
        raise HTTPException(status_code=404, detail="Record not found")
    
    del data[id]
    
    save_data(data)
    
    return "Record deleted successfully"