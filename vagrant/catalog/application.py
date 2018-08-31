from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSesion = sessionmaker(bind = engine)
session = DBSesion()

app = Flask(__name__)

categories = []

@app.route('/')
@app.route('/catalog')
def categoriesList():
    categories = session.query(Category).all()
    return render_template('home.html', categories = categories)


@app.route('/catalog/<int:category_id/items>', methods=['GET'])
def categoryItemsList(category_id):
    items = session.query(Item).filter_by(categoryId = category_id)
    return render_template('itemlist.html', categories = categories, items = items)


@app.route('/catalog/<int:category_id>/<int:item_id>', methods=['GET'])
def categoryItem(category_id, item_id):
    item = session.query(Item).filter_by(item_id).one()
    return render_template('item.html', item = item)



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)