from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from database_setup import Category, Item, Base, User

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


def set_password(password):
    """Method - Get hash password"""

    return generate_password_hash(password)


hashedPass1 = set_password("deep1234")

user1 = User(first_name="Deep",
             last_name="Agar",
             username="deep",
             hash_password=hashedPass1)
session.add(user1)
session.commit()

user2 = User(first_name="Priya",
             last_name="Agar",
             username="priya",
             hash_password=hashedPass1)
session.add(user2)
session.commit()

category1 = Category(title="Soccer")
session.add(category1)
session.commit()

item1 = Item(title="Stick",
             description="New Description",
             categoryId=category1.id,
             userId=user1.id)
session.add(item1)
session.commit()

item2 = Item(title="Goggles",
             description="New Description",
             categoryId=category1.id,
             userId=user1.id)
session.add(item2)
session.commit()

category2 = Category(title="Basketball")
session.add(category2)
session.commit()

item3 = Item(title="Snowboard",
             description="New Description",
             categoryId=category2.id,
             userId=user2.id)
session.add(item3)
session.commit()

item4 = Item(title="Shinguards",
             description="New Description",
             categoryId=category2.id,
             userId=user2.id)
session.add(item4)
session.commit()

category3 = Category(title="Baseball")
session.add(category3)
session.commit()

category4 = Category(title="Frisbee")
session.add(category4)
session.commit()
