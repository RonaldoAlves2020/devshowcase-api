from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional


# ==========================================
# PROFILE
# ==========================================

class ProfileCreate(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    github_url: Optional[HttpUrl] = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    bio: Optional[str] = None
    github_url: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# TECHNOLOGY
# ==========================================

class TechnologyCreate(BaseModel):
    name: str


class TechnologyResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ==========================================
# PROJECT
# ==========================================

class ProjectCreate(BaseModel):
    title: str
    description: str
    repository_url: Optional[HttpUrl] = None
    profile_id: int
    technology_ids: list[int] = []


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    repository_url: Optional[str] = None

    # Quantidade de votos
    upvotes: int

    # Média das avaliações
    average_rating: float = 0.0

    profile_id: int

    technologies: list[TechnologyResponse] = []

    class Config:
        from_attributes = True


# ==========================================
# FEEDBACK
# ==========================================

class FeedbackCreate(BaseModel):

    # Aceita somente notas entre 1 e 5
    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str


class FeedbackResponse(BaseModel):
    id: int
    rating: int
    comment: str
    project_id: int

    class Config:
        from_attributes = True   