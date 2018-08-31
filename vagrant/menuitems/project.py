from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def RestaurantMenu(restaurant_id):
    menuitems = session.query(MenuItem).filter_by(id = restaurant_id)

    output = ""
    for menuitem in menuitems:
        output += menuitem.name
        output += "</br>"
        output += menuitem.price
        output += "</br>"
        output += menuitem.description
        output += "</br></br>"

    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)