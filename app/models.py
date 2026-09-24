from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship

from app.database import Base


# ==========================================
# RELAÇÃO PROJECT x TECHNOLOGY
# ==========================================

project_technology = Table(
    "project_technology",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id"),
        primary_key=True
    ),
    Column(
        "technology_id",
        Integer,
        ForeignKey("technologies.id"),
        primary_key=True
    )
)


# ==========================================
# PROFILE
# ==========================================

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    github_url = Column(String(255), nullable=True)

    projects = relationship(
        "Project",
        back_populates="profile"
    )


# ==========================================
# TECHNOLOGY
# ==========================================

class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    projects = relationship(
        "Project",
        secondary=project_technology,
        back_populates="technologies"
    )


# ==========================================
# PROJECT
# ==========================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    repository_url = Column(
        String(255),
        nullable=True
    )

    # Quantidade de votos do projeto
    upvotes = Column(
        Integer,
        default=0
    )

    # Média das avaliações recebidas
    average_rating = Column(
        Float,
        default=0.0
    )

    profile_id = Column(
        Integer,
        ForeignKey("profiles.id"),
        nullable=False
    )

    profile = relationship(
        "Profile",
        back_populates="projects"
    )

    technologies = relationship(
        "Technology",
        secondary=project_technology,
        back_populates="projects"
    )

    feedbacks = relationship(
        "Feedback",
        back_populates="project",
        cascade="all, delete-orphan"
    )


# ==========================================
# FEEDBACK
# ==========================================

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Nota entre 1 e 5
    rating = Column(
        Integer,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    project = relationship(
        "Project",
        back_populates="feedbacks"
    )