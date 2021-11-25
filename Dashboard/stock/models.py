from datetime import datetime
from stock import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120),nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') 
    mobileno = db.Column(db.String(10), nullable=False, default='2342244')
    adharno = db.Column(db.String(100), nullable=False, default='23727474')
    panno = db.Column(db.String(100), nullable=False, default='839284823')
    stocks = db.relationship('Stock', backref='author', lazy=True)
    watch = db.relationship('Watch', backref='author', lazy=True)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.name}', '{self.mobileno}'')"


class Stock(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    stock_symbol = db.Column(db.String(20), nullable=False)
    number_of_shares = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Integer, nullable=False)
    prchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)




    def __repr__(self):
        return f'{self.stock_symbol} - {self.number_of_shares} shares purchased at ${self.purchase_price / 100} on {self.prchase_date}'

class Watch(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    stock_symbol = db.Column(db.String(20), nullable=False)
    current_price = db.Column(db.Integer,nullable=False)
    day_high = db.Column(db.Integer,nullable=False)
    day_low = db.Column(db.Integer,nullable=False)
    previous_close = db.Column(db.Integer,nullable=False)
    company_name = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

