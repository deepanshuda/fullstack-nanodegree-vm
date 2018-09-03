from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    first_name = Column(String(100), nullable = False)
    last_name = Column(String(100))
    username = Column(String(100), nullable = False)
    hash_password = Column(String(250), nullable = False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'username': self.username,
            'hashPassword': self.hash_password
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String(250), nullable=False)
    categoryId = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'categoryId': self.categoryId
        }



engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
