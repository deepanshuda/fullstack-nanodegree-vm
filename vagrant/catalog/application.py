from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Category, Item, User
from werkzeug.security import generate_password_hash, check_password_hash


from flask import Response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random, string
import requests


engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSesion = scoped_session(sessionmaker(bind = engine))
s = DBSesion()

app = Flask(__name__)

GOOGLE_CLIENT_ID = json.loads(open('client_secret_json.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"





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
    return render_template('itemlist.html', categories = categories, items = items, category = category)


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
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        session['state'] = state
        return render_template('login.html', STATE = state)


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
        access_token = session.get('access_token')
        if access_token is not None:
            result = gdisconnect()
            print("result is: ")
            # result_json = json.loads(result)
            print(result)

            return redirect(url_for('categoriesList'))
        else:
            session['logged_in'] = False
            return redirect(url_for('categoriesList'))
    else:
        return render_template('logout.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Valid State Token
    if request.args.get('state') != session['state']:
        response = Response(json.dumps('Invalid state parameter'), status = 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secret_json.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = Response(json.dumps('Failed to upgrade the authorization code'), status = 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = Response(json.dumps(result.get('error')), status = 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = Response(json.dumps("Token's user id does not match given userId"), status = 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = Response(json.dumps("Token's client id does not match with app's."), status = 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = Response(json.dumps('Current user is already connected.'), status = 200)
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

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % session['username'])
    print("done!")
    print("access token is %s" % session['access_token'])
    return output


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        print("Access token is none")
        response = Response(json.dumps('Current user not connected'), status = 401, mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response

    print("access token is %s" % access_token)
    print("username is:")
    print(session['username'])

    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % session.get('access_token')
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
        response = Response(json.dumps("Successfully disconnected."), status = 200, mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = Response(json.dumps('Failed to revoke token for given user.'), status = 400, mimetype='application/json')
        response.headers['Content-Type'] = 'application/json'
        return response



def getUserId(email):
    try:
        user = s.query(User).filter_by(email=email).one()
        return user
    except:
        return None

def getUserInfo(user_id):
    user = s.query(User).filter_by(id=user_id).one()
    return user

def createUser(login_session):
    newUser = User(username=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    s.add(newUser)
    s.commit()
    user = s.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)


