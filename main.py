from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from raw_data import users, orders, offers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DFSDFGFDF'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['DEBAG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint('age<120'))
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20))
    phone = db.Column(db.String(11), unique=True)
    # offers = relationship('Order')


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = relationship('User', foreign_keys='Order.customer_id')
    executor = relationship('User', foreign_keys='Order.executor_id')


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order = relationship('Order', foreign_keys='Offer.order_id')
    executor = relationship('User', foreign_keys='Offer.executor_id')


def insert_data_orders():
    new_order = []
    for order in orders:
        new_order.append(Order(
            id=order['id'],
            name=order['name'],
            description=order['description'],
            start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
            address=order['address'],
            price=order['price'],
            customer_id=order['customer_id'],
            executor_id=order['executor_id']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_order)


def insert_data_users():
    new_user = []
    for user in users:
        new_user.append(User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            age=user['age'],
            email=user['email'],
            role=user['role'],
            phone=user['phone']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_user)


def insert_data_offers():
    new_offer = []
    for offer in offers:
        new_offer.append(Offer(
            id=offer['id'],
            order_id=offer['order_id'],
            executor_id=offer['executor_id']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_offer)


@app.route('/users/', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        data = []
        all_user = User.query.all()
        for user in all_user:
            data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone})
        return jsonify(data)


@app.route('/users/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_user_pk(pk: int):
    if request.method == 'GET':
        print(pk)
        user = User.query.get(pk)
        data = {'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone
                }
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(pk)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.age = data['age']
        user.email = data['email']
        user.role = data['role']
        user.phone = data['phone']
        db.session.add(user)
        db.session.commit()
        return 'UPDATED', 200
    elif request.method == 'DELETE':
        user = User.query.get(pk)
        db.session.delete(user)
        db.session.commit()
        return 'DELETED', 200


@app.route('/orders/', methods=['GET', 'POST'])
def get_orders():
    if request.method == 'GET':
        data = []
        all_orders = Order.query.all()
        for order in all_orders:
            costomer = User.query.get(order.customer_id)
            executor = User.query.get(order.executor_id)
            data.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': costomer.last_name if costomer else 0,
                'executor_id': executor.last_name if executor else 0
            })
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        print(data)
        print(data['name'])
        new_order = Order(name=data['name'],
                          description=data['description'],
                          start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
                          end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
                          address=data['address'],
                          price=int(data['price']),
                          customer_id=int(data['customer_id']),
                          executor_id=int(data['executor_id']))
        with app.app_context():
            with db.session.begin():
                db.session.add(new_order)
        return 'OK', 200


@app.route('/orders/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_orders_pk(pk: int):
    if request.method == 'GET':
        print(pk)
        order = Order.query.get(pk)
        costomer = User.query.get(order.customer_id)
        executor = User.query.get(order.executor_id)
        data = {
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': costomer.last_name if costomer else 0,
            'executor_id': executor.last_name if executor else 0
        }
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        order = Order.query.get(pk)
        order.name = data['name']
        order.description = data['description']
        order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
        order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
        order.address = data['address']
        order.price = int(data['price'])
        order.customer_id = int(data['customer_id'])
        order.executor_id = int(data['executor_id'])
        db.session.add(order)
        db.session.commit()
        return 'UPDATED', 200
    elif request.method == 'DELETE':
        order = Order.query.get(pk)
        db.session.delete(order)
        db.session.commit()
        return 'DELETED', 200


if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    # insert_data_orders()
    # insert_data_users()
    # insert_data_offers()
    with app.app_context():
        print(Order.query.first())
        print(Order.query.first().name)
    app.run()

# import json
# import random
#
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import or_
# from sqlalchemy.orm import relationship
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SECRET_KEY'] = 'SDFFAS'
#
# db = SQLAlchemy(app)
#
#
# class User(db.Model):
#     __tabelname__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, db.CheckConstraint('age>18'))
#     group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
#     group = relationship('Group')
#
#
# class Group(db.Model):
#     __tablename__ = 'group'
#     id = db.Column(db.Integer, primary_key=True)
#     group_name = db.Column(db.String(200), nullable=False)
#     users = relationship('User')
#
#
# @app.route('/user/all')
# def user_all():
#     temp = User.query.all()
#     ret = []
#     for tm in temp:
#         ret.append({'id': tm.id, 'name': tm.name, 'group': tm.group.group_name})
#     return json.dumps(ret)
#
#
# @app.route('/user/first')
# def user_first():
#     tm = User.query.first()
#     return json.dumps({'id': tm.id, 'name': tm.name, 'group': tm.group.group_name})
#
#
# @app.route('/user/count')
# def user_count():
#     temp = User.query.count()
#     return json.dumps({'count': temp})
#
#
# @app.route('/user/<int:id>')
# def user_get(id: int):
#     temp = User.query.get(id)
#     return json.dumps({'id': temp.id, 'name': temp.name, 'group': temp.group.group_name})
#
#
# @app.route('/user/<name>/and/<int:age>')
# def op_and(name: str, age: int):
#     temp = User.query.filter(User.name == name, User.age == age)
#     print(temp)
#     print(temp.all())
#     return temp.first().group.group_name
#
#
# @app.route('/user/<name>/or/<int:age>')
# def op_or(name: str, age: int):
#     temp = User.query.filter(or_(User.name == name, User.age == age))
#     print(temp)
#     print(temp.all())
#     return temp.first().group.group_name
#
#
# @app.route('/user/<int:age1>/in/<int:age2>')
# def op_in(age1: int, age2: int):
#     temp = User.query.filter((User.age.in_([age1, age2])))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/<int:age1>/notin/<int:age2>')
# def op_notin(age1: int, age2: int):
#     temp = User.query.filter((User.age.notin_([age1, age2])))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/<int:age1>/between/<int:age2>')
# def op_between(age1: int, age2: int):
#     temp = User.query.filter((User.age.between(age1, age2)))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/like/<like_>')
# def op_like(like_: str):
#     temp = User.query.filter((User.name.like(like_ + '%')))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/none/')
# def op_none():
#     temp = User.query.filter((User.name == None))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/isnone/')
# def op_isnone():
#     temp = User.query.filter((User.name != None))
#     print(temp)
#     all_u = []
#     for _ in temp.all():
#         all_u.append({'id': _.id, 'name': _.name, 'age': _.age, 'group': _.group.group_name})
#     print(all_u)
#     return json.dumps(all_u)
#
#
# @app.route('/user/update/<name>/')
# def op_update(name: str):
#     # temp = User.query.filter(User.name == name)
#     temp = User.query.first()
#     print(temp)
#     temp2 = {'id': temp.id, 'name': temp.name, 'age': temp.age, 'group': temp.group.group_name}
#     print(temp2)
#     temp.name = 'DDDDDD'
#     db.session.add(temp)
#     db.session.commit()
#     temp = User.query.get(temp.id)
#     print(temp)
#     temp2 = {'id': temp.id, 'name': temp.name, 'age': temp.age, 'group': temp.group.group_name}
#     print(temp2)
#     return json.dumps(temp2)
#
#
# @app.route('/user/delete/<name>/')
# def op_delete(name: str):
#     temp = User.query.filter(User.name == name)
#     print(temp)
#     temp = temp.query.first()
#     print(temp)
#     temp2 = {'id': temp.id, 'name': temp.name, 'age': temp.age, 'group': temp.group.group_name}
#     print(temp2)
#     db.session.delete(temp)
#     db.session.commit()
#     temp = User.query.all()
#     print(temp)
#     return json.dumps('OK')
#
#
# #
# # @app.route('/user/and/<int:age>')
# # def op_and(age: int):
# #     temp = User.query.filter(User.name == 'Azaliya841', User.age == age)
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/like/<tex>')
# # def op_like(tex):
# #     temp = User.query.filter(User.name.like(tex + '%'))
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/or/<int:age>')
# # def op_or(age: int):
# #     temp = User.query.filter(or_(User.name == 'Azaliya841', User.age == age))
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/in/<int:age>')
# # def op_in(age: int):
# #     temp = User.query.filter(User.age.in_([18, age]))
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/notin/<int:age>')
# # def op_notin(age: int):
# #     temp = User.query.filter(User.age.notin_([18, age]))
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/null')
# # def op_null():
# #     temp = User.query.filter(User.age == None)
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/notnull')
# # def op_notnull():
# #     temp = User.query.filter(User.age != None)
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
# #
# #
# # @app.route('/user/between')
# # def op_between():
# #     temp = User.query.filter(User.age.between(20,21))
# #     print(temp)
# #     print(temp.all())
# #     return temp.first().name
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         # db.drop_all()
#         db.create_all()
#         g1 = Group(group_name='g1')
#         name = 'Azaliya2' + str(random.randint(1, 1000))
#         p1 = User(name=name, age=random.randint(19, 25), group=g1)
#         name = 'Ameliya2' + str(random.randint(1, 1000))
#         p2 = User(name=name, age=random.randint(19, 25))
#         name = 'Ameliya2' + str(random.randint(1, 1000))
#         p3 = User(name=name, age=random.randint(19, 25))
#         g2 = Group(group_name='g2', users=[p2, p3])
#
#         with db.session.begin():
#             db.session.add(p1)
#             db.session.add(g2)
#         # print(User.query.filter(User.name == 'Azaliya2391').first().name)
#         # db.session.commit()
#
#     app.run(debug=True)
#
# # import json
# #
# # from flask import Flask
# # from flask_sqlalchemy import SQLAlchemy
# # from sqlalchemy import or_
# # from sqlalchemy.orm import relationship
# #
# # app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# # app.config['SECRET_KEY'] = 'DDDFSLF'
# #
# # db = SQLAlchemy(app)
# #
# #
# # class User(db.Model):
# #     __tablename__ = 'user'
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False, unique=True)
# #     age = db.Column(db.Integer, db.CheckConstraint('age>18'))
# #     group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
# #     group = relationship('Group')
# #
# #
# # class Group(db.Model):
# #     __tablename__ = 'group'
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     users = relationship('User')
# #
# #
# # @app.route("/users/first")
# # def get_user_first():
# #     ret = User.query.first()
# #     return json.dumps({'id': ret.id, 'name': ret.name, 'group': ret.group.name})
# #
# #
# # @app.route('/users/all')
# # def get_user_all():
# #     all_users = User.query.all()
# #     temp = []
# #     for user in all_users:
# #         temp.append({'id': user.id, 'name': user.name, 'group': user.group.name})
# #     return json.dumps(temp)
# #
# #
# # @app.route('/users/count')
# # def get_count():
# #     count1 = User.query.count()
# #     return json.dumps(count1)
# #
# #
# # @app.route('/users/<int:id>')
# # def get_user_pk(id: int):
# #     pk = User.query.get(id)
# #     return json.dumps({'id': pk.id, 'name': pk.name, 'group': pk.group.name})
# #
# #
# # if __name__ == '__main__':
# #     with app.app_context():
# #         db.drop_all()
# #         db.create_all()
# #         group01 = Group(name='Group01')
# #         d1 = User(name='Albert', age=19, group=group01)
# #
# #         d2 = User(name='Azaliya', age=19)
# #         d3 = User(name='Gulcvbcx', age=21)
# #         d4 = User(name='Azaliya2', age=19)
# #         group02 = Group(name='Group02', users=[d2, d3, d4])
# #
# #         db.session.add(d1)
# #         db.session.add(group02)
# #         db.session.commit()
# #         # d2 = User(name='Ameliya')
# #         # d3 = User(name='Azaliya')
# #         # # d4 = User()
# #         # db.session.add_all([d2, d3])
# #         # db.session.commit()
# #         temp = User.query.filter(User.name == 'Albert')
# #         print(temp)
# #         print(temp.first().name)
# #         # and
# #         temp = User.query.filter(User.name == 'Albert', User.age == 19)
# #         print(temp)
# #         print(temp.all())
# #         # like
# #         temp = User.query.filter(User.name.like('A%'))
# #         print(temp)
# #         print(temp.all())
# #         #   or_
# #         temp = User.query.filter(or_(User.name == 'Albert', User.age == 21))
# #         print(temp)
# #         print(temp.all())
# #         #   none
# #         temp = User.query.filter(User.name == None)
# #         print(temp)
# #         print(temp.all())
# #         #   none
# #         temp = User.query.filter(User.name != None)
# #         print(temp)
# #         print(temp.all())
# #         #   in_
# #         temp = User.query.filter(User.age.in_([18, 19]))
# #         print(temp)
# #         print(temp.all())
# #         #   notin_
# #         temp = User.query.filter(User.id.notin_([2, 3]))
# #         print(temp)
# #         print(temp.all())
# #         #   none
# #         temp = User.query.filter(User.id.between(2, 3))
# #         print(temp)
# #         print(temp.all())
# #
# #     app.run(debug=True)
# #
# # # from flask import Flask
# # # from flask_sqlalchemy import SQLAlchemy
# # # import sqlalchemy
# # #
# # # app = Flask(__name__)
# # # # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# # # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
# # # app.config['SECRET_KEY'] = 'your_secret_key_here'
# # # db = SQLAlchemy(app)
# # #
# # #
# # # class Article(db.Model):
# # #     id = db.Column(db.Integer, primary_key=True)
# # #     title = db.Column(db.String(100), nullable=False)
# # #
# # #
# # # # db.create_all()
# # #
# # #
# # #
# # # # @app.route('/')
# # # # def hello():
# # # #     return 'hi'
# # #
# # #
# # # # Press the green button in the gutter to run the script.
# # # if __name__ == '__main__':
# # #     with app.app_context():
# # #         # db.drop_all()
# # #         db.create_all()
# # #         tes = Article(id=1, title='123')
# # #         tes1 = Article(id=2, title='111')
# # #         tes2 = Article(title='222')
# # #         db.session.add(tes)
# # #         db.session.commit()
# # #         ttt = [tes1, tes2]
# # #         db.session.add_all(ttt)
# # #         print(db.session.new)
# # #         db.session.commit()
# # #         print(Article.query.first().title)
# # #     app.run(debug=True)
# # #
# # # # See PyCharm help at https://www.jetbrains.com/help/pycharm/
