from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item, User


engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSesion = scoped_session(sessionmaker(bind = engine))
s = DBSesion()

app = Flask(__name__)


@app.route('/catalog/catalog.json')
def catalogList():
    categories = s.query(Category).all()
    categoriesObj = []
    for i in categories:
        items = s.query(Item).filter_by(categoryId = i.id)
        category = i.serialize
        category["items"] = [j.serialize for j in items]
        categoriesObj.append(category)

    return jsonify(categories=categoriesObj)


@app.route('/catalog/categories.json')
def categoriesList():
    categories = s.query(Category).all()

    return jsonify(categories=[j.serialize for j in categories])


@app.route('/catalog/<int:category_id>/items.json')
def itemsList(category_id):
    items = s.query(Item).filter_by(categoryId=category_id)

    return jsonify(items=[j.serialize for j in items])



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
