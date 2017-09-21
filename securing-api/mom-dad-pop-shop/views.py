from models import Base, User, Bagel
from flask import Flask, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


engine = create_engine('sqlite:///bagelShop.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

# Add @auth.verify_password here
@auth.verify_password
def verify_password(username, password):
    print "Looking for user %s" % username
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print "User not found"
        return False
    elif not user.verify_password(password):
        print "Unable to verify password"
        return False
    else:
        g.user = user
        return True


# Add a /users route here
@app.route('/users', methods=['POST'])
def newUser():
    # fetch and store username & password from json file
    username = request.json.get('username')
    password = request.json.get('password')
    # check if username or password is empty
    if username is None or password is None:
        print "missing arguments"
        abort(400)
    # check if user already exists
    if session.query(User).filter_by(username=username).first() is not None:
        print "user already exists"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200

    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username}), 201


@app.route('/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/bagels', methods=['GET','POST'])
# protect this route with a required login
@auth.login_required
def showAllBagels():
    if request.method == 'GET':
        bagels = session.query(Bagel).all()
        return jsonify(bagels=[bagel.serialize for bagel in bagels])
    elif request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        picture = request.json.get('picture')
        price = request.json.get('price')
        newBagel = Bagel(name=name, description=description, picture=picture, price=price)
        session.add(newBagel)
        session.commit()
        return jsonify(newBagel.serialize)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
