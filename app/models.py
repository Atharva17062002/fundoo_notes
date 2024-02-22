from app import db
from passlib.hash import pbkdf2_sha256
from settings import settings
from datetime import datetime, timedelta
from .utils import JWT
from sqlalchemy.orm import Mapped
from typing import List

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

collaborators = db.Table(
    'collaborators',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False),
    db.Column('notes_id', db.Integer, db.ForeignKey('notes.id', ondelete="CASCADE"), nullable=False),
    db.Column("access_type", db.String(10), default= 'read-only'),
)

class User(BaseModel):
    __tablename__ = 'user'
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    notes = db.relationship('Notes',back_populates="user")
    label = db.relationship('Label',back_populates="user")
    c_notes: Mapped[List["Notes"]] = db.relationship(secondary=collaborators,back_populates="c_users")

    def __init__(self, username, email, password, location):
        self.username = username
        self.email = email
        self.password = pbkdf2_sha256.hash(password)
        self.location = location

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    def generate_token(self, aud = "Default", exp = 15):
        payload = {"user_id":self.id, "aud":aud, "exp":datetime.utcnow() + timedelta(minutes=exp)}
        return JWT.to_encode(payload)

    @property
    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "location": self.location
        }


class Notes(BaseModel):
    __tablename__ = 'notes'
    id=db.Column(db.Integer,primary_key=True,nullable=False, autoincrement=True)
    title=db.Column(db.String(50),nullable=True)
    description=db.Column(db.Text,nullable=False)
    color = db.Column(db.String(20))
    reminder = db.Column(db.DateTime, default=None, nullable=True)
    is_archived = db.Column(db.Boolean, default=False)
    is_trash = db.Column(db.Boolean, default=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id', ondelete="CASCADE"),nullable=False)
    user=db.relationship('User',back_populates="notes")
    c_users: Mapped[List["User"]] = db.relationship(secondary=collaborators,back_populates='c_notes')

    def _str_(self) -> str:
        return f'{self.title}-{self.id}'

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "color": self.color,
            "reminder": str(self.reminder),
            "is_archived": self.is_archived,
            "is_trash": self.is_trash,
            "user_id": self.user_id
        }

class Label(BaseModel):
    __tablename__ = 'label'
    name = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', back_populates="label")

    def to_json(self):
        return {
            "name": self.name,
            "user_id": self.user_id
        }

