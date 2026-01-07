from enum import Enum
from typing import Annotated
from fastapi import FastAPI, Query, Path, HTTPException, Cookie
from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field
import json

class Gender(Enum):
	MALE = "male"
	FEMALE = "female"

class Department(Enum):
    COMPUTER_SCIENCE = "computer science"
    MATHEMATICS = "Mathematics"
    PHYSICS = "Physics"


class AddStudent(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    age: int = Field(gt=18, lt=100)
    gender: Gender
    department: Department
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    
    @field_validator("email")
    @classmethod
    def email_validator(cls, value):
        valid_domains = ["gmail.com", "student.com"]
        
        #abe@gmail.com
        domain_name = value.split('@')[-1]
        
        if domain_name not in valid_domains:
            raise HTTPException(status_code=400, detail="not a valid email")
        
        return value
    
    @computed_field
    @property
    def confirm_password(self) -> str:
        confirm_pass = self.password
        return confirm_pass
    
    model_config={
        "json_schema_extra":{
            "examples": [
                {
                    "name":"abc",
                    "age":18,
                    "gender":"male",
                    "department":"computer science",
                    "email":"abc@gmail.com",
                    "password":"abc12345"
                }
            ]
        }
    }


 
def load_data():
    with open("data.json", 'r') as f:
        data = json.load(f)
    return data

app = FastAPI()

@app.get('/')
def root():
    return {"message" : "Welcome to ABC College"}


@app.get("/student/view/")
def view_all(st_id: Annotated[str | None, Cookie()] = None):
    data = load_data()
    return {"data" : data, "st_id" : st_id}


@app.get("/student/view/{student_id}")
def get_student_record(student_id: Annotated[str, Path(title="View Student data", description="ID of the student", examples="S001")]):
    data = load_data()
    if student_id in data:
        return {"message" : "Student Retrieved Successfully", "student_id": student_id, "student": data[student_id]}
    raise HTTPException(status_code=404, detail="Student record not found")


@app.get("/student/sort/")
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


@app.post("/student/add/{student_id}")
def add_student(student_id: str, student: AddStudent):
    data = load_data()
    
    data[student_id] = (student.model_dump())
    # return data[student_id]