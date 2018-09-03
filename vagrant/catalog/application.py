from flask import Flask, render_template, request, redirect, url_for, session, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item, User
from werkzeug.security import generate_password_hash, check_password_hash


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSesion = scoped_session(sessionmaker(bind = engine))
s = DBSesion()

app = Flask(__name__)

def set_password(password):
    return generate_password_hash(password)


def check_password(hashedPassword, password):
    return check_password_hash(hashedPassword, password)

@app.route('/')
@app.route('/catalog')
def categoriesList():
    categories = s.query(Category).all()
    items = s.query(Item).all()
    return render_template('home.html', categories = categories, items = items)


@app.route('/catalog/<string:categoryTitle>/items', methods=['GET'])
def categoryItemsList(categoryTitle):
    categories = s.query(Category).all()
    category = s.query(Category).filter_by(title = categoryTitle).one()
    items = s.query(Item).filter_by(categoryId = category.id)
    return render_template('itemlist.html', categories = categories, items = items)


@app.route('/catalog/<int:category_id>/<int:item_id>', methods=['GET'])
def categoryItem(category_id, item_id):
    item = s.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', item = item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addNewItem():
    if request.method == 'POST':
        newItem = Item(title = request.form['title'], description = request.form['desc'], categoryId = request.form['categoryId'])
        s.add(newItem)
        s.commit()
        return redirect(url_for('categoriesList'))
    else:
        categories = s.query(Category).all()
        return render_template('addItem.html', categories = categories)


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    item = s.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        item.title = request.form['title']
        item.description = request.form['desc']
        item.categoryId = request.form['categoryId']
        s.add(item)
        s.commit()
        return redirect(url_for('categoryItem', category_id = item.categoryId, item_id = item.id))
    else:
        categories = s.query(Category).all()
        return render_template('editItem.html', item = item, categories = categories)


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    item = s.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        s.delete(item)
        s.commit()
        return redirect(url_for('categoriesList'))
    else:
        return render_template('deleteItem.html', item = item)


@app.route('/login', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("fetching")
        result = s.query(User).filter_by(username = username).first()
        print("RESULT: ", result.first_name)
        if result:
            if check_password(result.hash_password, password):
                session['logged_in'] = True
                return redirect(url_for('categoriesList'))
            else:
                session['logged_in'] = False
                return render_template('login.html')
        else:
            session['logged_in'] = False
            return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def userSignup():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        hashedPassword = set_password(request.form['password'])
        user = User(first_name = firstname, last_name = lastname, username = username, hash_password = hashedPassword)
        s.add(user)
        s.commit()
        session['logged_in'] = True
        return redirect(url_for('categoriesList'))
    else:
        return render_template('signup.html')


@app.route('/logout', methods=['GET', 'POST'])
def userLogout():
    if request.method == 'POST':
        session['logged_in'] = False
        return redirect(url_for('categoriesList'))
    else:
        return render_template('logout.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)


