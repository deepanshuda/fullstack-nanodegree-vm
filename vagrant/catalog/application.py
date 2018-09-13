from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
    jsonify,
    g,
    flash
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item, User
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask_httpauth import HTTPBasicAuth

import httplib2
import json
import random
import string
import requests

engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSesion = scoped_session(sessionmaker(bind=engine))
s = DBSesion()

app = Flask(__name__)

auth = HTTPBasicAuth()

GOOGLE_CLIENT_ID = json.loads(open('client_secret_json.json', 'r')
                              .read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"
GOOGLE_CONNECT_URL = \
    'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
GOOGLE_DISCONNECT_URL = \
    "https://accounts.google.com/o/oauth2/revoke?token=%s"


def set_password(password):
    """Method - Get hash password"""

    return generate_password_hash(password)


def check_password(hashedPassword, password):
    """Method - check hash password with provided one"""

    return check_password_hash(hashedPassword, password)


@auth.verify_password
def verify_pw(username, password):
    """Method - Verify Password

    This method verifies whether the provided username
    and password are valid or not
    """

    user = s.query(User).filter_by(username=username).first()
    if not user or not check_password(user.hash_password, password):
        return False

    g.user = user
    return True


@app.route('/')
@app.route('/catalog')
def categoriesList():
    """Method - Categories List

    This method list down all categories and items im catalog
    """

    categories = s.query(Category).all()
    items = s.query(Item).all()
    return render_template('home.html',
                           categories=categories,
                           items=items)


@app.route('/catalog/<string:categoryTitle>/items', methods=['GET'])
def categoryItemsList(categoryTitle):
    """Method - Category Items

    This method shows items of selected category
    """

    categories = s.query(Category).all()
    category = s.query(Category).filter_by(title=categoryTitle).one()
    items = s.query(Item).filter_by(categoryId=category.id)
    return render_template('itemlist.html',
                           categories=categories,
                           items=items,
                           category=category)


@app.route('/catalog/<int:category_id>/<int:item_id>', methods=['GET'])
def categoryItem(category_id, item_id):
    """Method - show item

    This method shows details of item selected
    """

    item = s.query(Item).filter_by(id=item_id).one()
    return render_template('item.html',
                           item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
@auth.login_required
def addNewItem():
    """Method - Add new item

    This method has two methods
    GET - opens add new item page
    POST - adds new item in database
    """

    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                       description=request.form['desc'],
                       categoryId=request.form['categoryId'])
        s.add(newItem)
        s.commit()
        flash(u'new menu item created', 'success')
        return redirect(url_for('categoriesList'))
    else:
        categories = s.query(Category).all()
        return render_template('addItem.html',
                               categories=categories)


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
@auth.login_required
def editItem(item_id):
    """Method - Edit item

    This method has two methods
    GET - opens edit item page
    POST - updates item in database
    """

    item = s.query(Item).filter_by(id=item_id).one()

    if g.user is not None:
        user_id = g.user.id
        if not user_id == item.userId:
            categories = s.query(Category).all()
            flash(u'Selected item is not owned by you. You can create a new item and then edit it.', 'danger')
            return render_template('addItem.html',
                                   categories=categories)

    if request.method == 'POST':
        item.title = request.form['title']
        item.description = request.form['desc']
        item.categoryId = request.form['categoryId']
        s.add(item)
        s.commit()
        flash(u'menu item edited', 'success')
        return redirect(url_for('categoryItem',
                                category_id=item.categoryId,
                                item_id=item.id))
    else:
        categories = s.query(Category).all()
        return render_template('editItem.html',
                               item=item,
                               categories=categories)


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
@auth.login_required
def deleteItem(item_id):
    """Method - Delete item

    This method has two methods
    GET - opens delete item page
    POST - deletes item from database
    """

    item = s.query(Item).filter_by(id=item_id).one()

    if g.user is not None:
        user_id = g.user.id
        if not user_id == item.userId:
            categories = s.query(Category).all()
            flash(u'Selected item is not owned by you. You can create a new item and then delete it.', 'danger')
            return render_template('addItem.html',
                                   categories=categories)

    if request.method == 'POST':
        s.delete(item)
        s.commit()
        flash(u'menu item deleted', 'success')
        return redirect(url_for('categoriesList'))
    else:
        return render_template('deleteItem.html', item=item)


@app.route('/login', methods=['GET', 'POST'])
def userLogin():
    """Method - user login

    This method has two methods
    GET - opens login page
    POST - checks if user specified is available
    If yes, then open categories home page
    """

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("fetching")
        result = s.query(User).filter_by(username=username).first()

        if result:
            print("RESULT: ", result.first_name)
            if check_password(result.hash_password, password):
                session['logged_in'] = True
                g.user = result
                return redirect(url_for('categoriesList'))
            else:
                session['logged_in'] = False
                g.user = None
                return render_template('login.html')
        else:
            session['logged_in'] = False
            g.user = None
            return render_template('login.html')

    else:
        state = '' \
            .join(random.choice(string.ascii_uppercase + string.digits)
                  for x in range(32))
        session['state'] = state
        return render_template('login.html', STATE=state)


@app.route('/signup', methods=['GET', 'POST'])
def userSignup():
    """Method - user signup

    This method has two methods
    GET - opens login page
    POST - checks if user specified is available
    If yes, then open categories home page
    """

    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        hashedPassword = set_password(request.form['password'])
        user = User(first_name=firstname,
                    last_name=lastname,
                    username=username,
                    hash_password=hashedPassword)
        s.add(user)
        s.commit()
        session['logged_in'] = True
        g.user = user
        return redirect(url_for('categoriesList'))
    else:
        return render_template('signup.html')


@app.route('/logout', methods=['GET', 'POST'])
def userLogout():
    """Method - get user id

    :parameter - username
    :returns - userId
    """

    if request.method == 'POST':
        access_token = session.get('access_token')
        if access_token is not None:
            result = gdisconnect()
            print("result is: ")
            # result_json = json.loads(result)
            print(result)

            return redirect(url_for('categoriesList'))
        else:
            session['logged_in'] = False
            g.user = None
            return redirect(url_for('categoriesList'))
    else:
        return render_template('logout.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Method - Google Connect

    This method helps connect with google account
    Also fetches google data
    """

    # Valid State Token
    if request.args.get('state') != session['state']:
        response = Response(json.dumps('Invalid state parameter'),
                            status=401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secret_json.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = Response(json.dumps('Failed to upgrade authorization code'),
                            status=401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = GOOGLE_CONNECT_URL % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = Response(json.dumps(result.get('error')),
                            status=500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = Response(json.dumps("Token's userId does not match"),
                            status=401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = Response(json.dumps("Token's clientId does not match"),
                            status=401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = Response(json.dumps('Current user is already connected'),
                            status=200)
        response.headers['Content-Type'] = 'application/json'
        return response

    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    session['logged_in'] = True

    userId = getUserId(session['email'])
    if userId is None:
        userId = createUser(session)

    session['user_id'] = userId
    g.user = getUserInfo(userId)

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; ' \
              'height: 300px;' \
              'border-radius: 150px;' \
              '-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % session['username'])
    print("done!")
    print("access token is %s" % session['access_token'])
    return output


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    """Method - Google Disconnect

    This method helps disconnect with google account
    """

    access_token = session.get('access_token')
    if access_token is None:
        print("Access token is none")
        response = Response(json.dumps('Current user not connected'),
                            status=401,
                            mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response

    # print("access token is %s" % access_token)
    # print("username is:")
    # print(session['username'])

    url = GOOGLE_DISCONNECT_URL % access_token
    h = httplib2.Http()

    result = h.request(url, 'GET')[0]
    print("result is")
    print(result)

    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        session['logged_in'] = False
        g.user = None
        response = Response(json.dumps("Successfully disconnected."),
                            status=200,
                            mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = Response(json.dumps('Failed to revoke token for user.'),
                            status=400,
                            mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/catalog.json')
@auth.login_required
def catalogJsonList():
    """Method - Catalog json

    End point to get whole catalog json data
    This is authentication secured and required user login
    before returning result
    """

    categories = s.query(Category).all()
    categoriesObj = []
    for i in categories:
        items = s.query(Item).filter_by(categoryId=i.id)
        category = i.serialize
        category["items"] = [j.serialize for j in items]
        categoriesObj.append(category)

    return jsonify(categories=categoriesObj)


@app.route('/catalog/categories.json')
@auth.login_required
def categoriesJsonList():
    """Method - Categories json

    End point to get categories json data
    This is authentication secured and required user login
    before returning result
    """

    categories = s.query(Category).all()

    return jsonify(categories=[j.serialize for j in categories])


@app.route('/catalog/<int:category_id>/items.json')
@auth.login_required
def itemsJsonList(category_id):
    """Method - Items json

    End point to get items json data of a category
    This is authentication secured and required user login
    before returning result
    """

    items = s.query(Item).filter_by(categoryId=category_id)

    return jsonify(items=[j.serialize for j in items])


def getUserId(username):
    """Method - get user id

    :parameter - username
    :returns - userId
    """

    try:
        user = s.query(User).filter_by(username=username).one()
        return user
    except:
        return None


def getUserInfo(user_id):
    """Method - get user information

    :parameter - user_id
    :returns - user
    """

    user = s.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    """Method - create user

    :parameter - login_session
    :returns - user id
    """

    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    s.add(newUser)
    s.commit()
    user = s.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
