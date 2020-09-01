from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)

    def __str__(self):
        return f'user_id: {self.id}, chat_id: {self.id}'


Base.metadata.create_all(engine)
