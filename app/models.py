from app import db
from passlib.hash import pbkdf2_sha256

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class User(BaseModel):
    __tablename__ = 'user'
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password, location):
        self.username = username
        self.email = email
        self.password = pbkdf2_sha256.hash(password)
        self.location = location

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    @property
    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "location": self.location
        }