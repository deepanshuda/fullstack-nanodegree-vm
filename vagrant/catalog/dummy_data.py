from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Item, Base

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()


category1 = Category(title = "Soccer")
session.add(category1)
session.commit()

item1 = Item(title = "Stick", description = "New Description", categoryId = category1.id)
session.add(item1)
session.commit()

item2 = Item(title = "Goggles", description = "New Description", categoryId = category1.id)
session.add(item2)
session.commit()

category2 = Category(title = "Basketball")
session.add(category2)
session.commit()

item3 = Item(title = "Snowboard", description = "New Description", categoryId = category2.id)
session.add(item3)
session.commit()

item4 = Item(title = "Shinguards", description = "New Description", categoryId = category2.id)
session.add(item4)
session.commit()

category3 = Category(title = "Baseball")
session.add(category3)
session.commit()

category4 = Category(title = "Frisbee")
session.add(category4)
session.commit()
