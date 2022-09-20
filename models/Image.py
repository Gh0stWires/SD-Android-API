from flask import Flask
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Image(Base):
    __tablename__ = "image"
    id = Column("image_id", Integer, primary_key=True)
    title = Column(String(600))
    uri = Column(String)
    pub_date = Column(DateTime)

    def __init__(self, title, uri):
        self.title = title
        self.uri = uri
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return f"Image(id={self.id!r}, uri={self.uri!r})"