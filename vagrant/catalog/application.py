from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSesion = sessionmaker(bind = engine)
session = DBSesion()

app = Flask(__name__)

@app.route('/')
@app.route('/hello')
def helloWorld():
    return "Hello World"



if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)