import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'DDDFSLF'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer, db.CheckConstraint('age>18'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = relationship('Group')


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    users = relationship('User')


@app.route("/users/first")
def get_user_first():
    ret = User.query.first()
    return json.dumps({'id': ret.id, 'name': ret.name, 'group': ret.group.name})


@app.route('/users/all')
def get_user_all():
    all_users = User.query.all()
    temp = []
    for user in all_users:
        temp.append({'id': user.id, 'name': user.name, 'group': user.group.name})
    return json.dumps(temp)


@app.route('/users/count')
def get_count():
    count1 = User.query.count()
    return json.dumps(count1)


@app.route('/users/<int:id>')
def get_user_pk(id: int):
    pk = User.query.get(id)
    return json.dumps({'id': pk.id, 'name': pk.name, 'group': pk.group.name})


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        group01 = Group(name='Group01')
        d1 = User(name='Albert', age=19, group=group01)

        d2 = User(name='Azaliya', age=19)
        d3 = User(name='Gulcvbcx', age=21)
        d4 = User(name='Azaliya2', age=19)
        group02 = Group(name='Group02', users=[d2, d3, d4])

        db.session.add(d1)
        db.session.add(group02)
        db.session.commit()
        # d2 = User(name='Ameliya')
        # d3 = User(name='Azaliya')
        # # d4 = User()
        # db.session.add_all([d2, d3])
        # db.session.commit()
        temp = User.query.filter(User.name == 'Albert')
        print(temp)
        print(temp.first().name)
        # and
        temp = User.query.filter(User.name == 'Albert', User.age == 19)
        print(temp)
        print(temp.all())
        # like
        temp = User.query.filter(User.name.like('A%'))
        print(temp)
        print(temp.all())
        #   or_
        temp = User.query.filter(or_(User.name == 'Albert', User.age == 21))
        print(temp)
        print(temp.all())
        #   none
        temp = User.query.filter(User.name == None)
        print(temp)
        print(temp.all())
        #   none
        temp = User.query.filter(User.name != None)
        print(temp)
        print(temp.all())
        #   in_
        temp = User.query.filter(User.age.in_([18, 19]))
        print(temp)
        print(temp.all())
        #   notin_
        temp = User.query.filter(User.id.notin_([2, 3]))
        print(temp)
        print(temp.all())
        #   none
        temp = User.query.filter(User.id.between(2, 3))
        print(temp)
        print(temp.all())

    app.run(debug=True)

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# import sqlalchemy
#
# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
# app.config['SECRET_KEY'] = 'your_secret_key_here'
# db = SQLAlchemy(app)
#
#
# class Article(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#
#
# # db.create_all()
#
#
#
# # @app.route('/')
# # def hello():
# #     return 'hi'
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     with app.app_context():
#         # db.drop_all()
#         db.create_all()
#         tes = Article(id=1, title='123')
#         tes1 = Article(id=2, title='111')
#         tes2 = Article(title='222')
#         db.session.add(tes)
#         db.session.commit()
#         ttt = [tes1, tes2]
#         db.session.add_all(ttt)
#         print(db.session.new)
#         db.session.commit()
#         print(Article.query.first().title)
#     app.run(debug=True)
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
