from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item, User


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSesion = scoped_session(sessionmaker(bind = engine))
session = DBSesion()

app = Flask(__name__)


@app.route('/')
@app.route('/catalog')
def categoriesList():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('home.html', categories = categories, items = items)


@app.route('/catalog/<string:categoryTitle>/items', methods=['GET'])
def categoryItemsList(categoryTitle):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(title = categoryTitle).one()
    items = session.query(Item).filter_by(categoryId = category.id)
    return render_template('itemlist.html', categories = categories, items = items)


@app.route('/catalog/<int:category_id>/<int:item_id>', methods=['GET'])
def categoryItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', item = item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addNewItem():
    if request.method == 'POST':
        newItem = Item(title = request.form['title'], description = request.form['desc'], categoryId = 1)
        session.add(newItem)
        session.commit()
        return redirect(url_for('categoriesList'))
    else:
        return render_template('addItem.html')


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        item.title = request.form['title']
        item.description = request.form['desc']
        session.add(item)
        session.commit()
        return redirect(url_for('categoryItem', category_id = item.categoryId, item_id = item.id))
    else:
        return render_template('editItem.html', item = item)


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('categoriesList'))
    else:
        return render_template('deleteItem.html', item = item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)