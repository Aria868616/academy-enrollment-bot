from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# ۱. اسکیما جدول کاربران
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True) 
    full_name: str                                       
    phone: str                                           
    # 👇 اصلاح این بخش
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    enrollments: List["Enrollment"] = Relationship(back_populates="user")


# ۲. اسکیما جدول دوره‌های آموزشی
class Course(SQLModel, table=True):
    __tablename__ = "courses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str                                           
    description: Optional[str] = Field(default=None)     
    price: Optional[int] = Field(default=0)              
    capacity: Optional[int] = Field(default=None)        
    
    enrollments: List["Enrollment"] = Relationship(back_populates="course")


# ۳. اسکیما جدول ثبت‌نام (جدول واسط)
class Enrollment(SQLModel, table=True):
    __tablename__ = "enrollments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="courses.id")
    # 👇 اصلاح این بخش
    enrolled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    user: User = Relationship(back_populates="enrollments")
    course: Course = Relationship(back_populates="enrollments")