import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from constant import TransactionChoices

class AccountPermission(db.Model):
    __tablename__ = 'account_permission'
    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.Integer(), db.ForeignKey(
        'account.id', ondelete='CASCADE'))
    permission_id = db.Column(db.Integer(), db.ForeignKey(
        'permission.id', ondelete='CASCADE'))

class Account(UserMixin, db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    fullname = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    number = db.Column(db.String(11), unique=True, index=True)
    status = db.Column(db.Boolean(), nullable=False, server_default='1')
    coin = db.Column(db.Integer , server_default='0')
    address = db.Column(db.String(255))
    permission = db.relationship(
        'Permission',
        secondary='account_permission',
        backref=db.backref('account', lazy='dynamic'))
    transaction = db.relationship('Transaction', backref='account', lazy=True)

    def __repr__(self):
        return '<Account {}>'.format(self.fullname)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'fullname': self.fullname,
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['fullname', 'email', 'number', 'password_hash', 'address']:
            if field in data:
                setattr(self, field, data[field])
                
        if new_user:
            db_roles = Permission.find_all()
            for role in db_roles:
                if role.name != 'admin':
                    self.permission.append(role)

            if 'password' in data:
                self.set_password(data['password'])

    def json(self):
        return {"id": self.id, "fullname": self.fullname}

    @classmethod
    def find_by_email(cls, _email):
        return cls.query.filter_by(email=_email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Model Permission `{}`>".format(self.name)
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    date = db.Column(db.DateTime, server_default=str(datetime.datetime.utcnow))
    information = db.Column(db.String(255))
    type = db.Column(db.String(255))
    status = db.Column(db.Boolean, nullable=False, server_default='1')
    amount = db.Column(db.Integer)
    wallet_balance = db.Column(db.Integer)
    result = db.Column(db.Integer)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
        nullable=False)
    
    def __init__(self, information, type, amount, result, account_id):
        self.information = information
        self.type = type
        self.amount = amount
        self.result = result
        self.account_id = account_id

    def set_datetime_from_timestamp(self, timestamp):
        self.date = datetime.datetime.fromtimestamp(timestamp/1000.0)

    def set_datetime(self, datetime):
        self.date = datetime

    def set_wallet_balance(self):
        user = Account.find_by_id(self.account_id)

        if self.type == TransactionChoices.RECHARGE.value or self.type == TransactionChoices.RECEIVE_MONEY.value:
            self.wallet_balance = user.coin + self.amount
        else:
            self.wallet_balance = user.coin - self.amount

    def get_datetime(self):
        return self.date.strftime("%d-%m-%Y %H:%M:%S")
    
    def get_amount(self):
        return format(self.amount, ',d')
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
