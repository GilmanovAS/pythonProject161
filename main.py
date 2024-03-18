import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'DDDFSLF'

db = SQLAlchemy(app)


@app.route('/user/count')
def get_user_count():
    user_count = User.query.count()
    return json.dumps(user_count)


@app.route('/user/first')
def get_user_first():
    user_first = User.query.first()
    return json.dumps({"id": user_first.id,
                       "name": user_first.name})


@app.route('/user/<int:pk>')
def get_pk(pk: int):
    idd = User.query.get(pk)
    return json.dumps({"id": idd.id,
                       "name": idd.name})


@app.route('/user/all')
def get_all():
    all_user = User.query.all()
    response = []
    for user in all_user:
        response.append({"id": user.id,
                         "name": user.name}
                        )
    return response

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)


if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
        d1 = User(name='Albert2')
        db.session.add(d1)
        db.session.commit()
        d2 = User(name='Ameliya')
        d3 = User(name='Azaliya')
        db.session.add_all([d2, d3])
        db.session.commit()

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
