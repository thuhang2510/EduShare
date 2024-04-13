from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import desc, func
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import extract

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
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    fullname = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255))
    number = db.Column(db.String(11), unique=True, index=True, nullable=False)
    status = db.Column(db.Boolean(), nullable=False, server_default='1')
    coin = db.Column(db.Integer , server_default='0')
    address = db.Column(db.String(255))
    number_download = db.Column(db.Integer, server_default='0')
    datetime_week_reset = db.Column(db.DateTime, default=datetime.utcnow)
    number_ask = db.Column(db.Integer, server_default='0')
    datetime_day_reset = db.Column(db.DateTime, default=datetime.utcnow)
    violation_count = db.Column(db.Integer, server_default='0')
    permission = db.relationship(
        'Permission',
        secondary='account_permission',
        backref=db.backref('account', lazy='dynamic'))
    transaction = db.relationship('Transaction', backref='account', lazy=True)
    evaluate = db.relationship('Evaluate', backref='account', lazy=True)
    purchase = db.relationship('Purchase', backref='account', lazy=True)
    document = db.relationship('Documents', backref='account', lazy=True)

    def __repr__(self):
        return self.fullname
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'fullname': self.fullname,
            'address': self.address,
            'number': self.number,
            'coin': self.coin,
            'number_ask': self.number_ask,
            'number_download': self.number_download,
            'datetime_week_reset': self.datetime_week_reset,
            'datetime_day_reset': self.datetime_day_reset,
            'purchase': Purchase.list_to_dict(self.purchase)
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
        return cls.query.filter_by(email=_email, status=True).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id, status=True).first()
    
    @classmethod
    def find_by_id_tuple(cls, _id):
        return cls.query.with_entities(cls.id, cls.fullname, cls.email, cls.address, cls.coin).filter_by(id=_id, status=True).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_permission(cls, permission_name):
        return cls.query.join(AccountPermission, AccountPermission.account_id == cls.id).\
            join(Permission, Permission.id == AccountPermission.permission_id).\
            filter(Permission.name==permission_name, cls.status==True).\
            first()

class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
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
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    information = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    wallet_balance = db.Column(db.Integer, nullable=False)
    result = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False, server_default='1')
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
        nullable=False)
    
    def __init__(self, information, type, amount, result, account_id):
        self.information = information
        self.type = type
        self.amount = amount
        self.result = result
        self.account_id = account_id

    def set_datetime_from_timestamp(self, timestamp):
        self.date = datetime.fromtimestamp(timestamp/1000.0)

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
    
    @classmethod
    def get_by_account_id_with_paginate(cls, _account_id, page, per_page):
        return cls.query.order_by(desc(cls.date))\
                        .filter(cls.account_id == _account_id)\
                        .paginate(page=page, per_page=per_page)
    
    @classmethod
    def get_month_stats_with_account_id(cls, _account_id, year):
        return cls.query.with_entities(extract('month', cls.date), func.sum(cls.amount))\
                    .order_by(cls.date)\
                    .filter(cls.account_id==_account_id, extract('year', cls.date)==year, cls.type != "Mua tài liệu", cls.result==0)\
                    .group_by(extract('month', cls.date))\
                    .all()
    
    @classmethod
    def get_month_stats(cls, year):
        return cls.query.with_entities(extract('month', cls.date), func.sum(cls.amount))\
                    .order_by(cls.date)\
                    .filter(extract('year', cls.date)==year, cls.type.like("Nhận hoa hồng"), cls.result==0)\
                    .group_by(extract('month', cls.date))\
                    .all()
    
    @classmethod
    def get_total(cls, account_id, type):
        return cls.query.with_entities(func.sum(cls.amount))\
                    .filter(cls.account_id==account_id, cls.type==type, cls.result==0)\
                    .scalar()
    
    def to_dict(self):
        data = {
            'id': self.id,
            'date': self.date,
            'information': self.information,
            'type': self.type,
            'status': self.status,
            'amount': self.amount,
            'wallet_balance': self.wallet_balance,
            'result': self.result,
            'account_id': self.account_id
        }

        return data

    @classmethod
    def list_to_dict(cls, transactions):
        data = []

        for transaction in transactions:
            data.append(transaction.to_dict())

        return data
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    parent_id = db.Column(db.Integer)

    @classmethod
    def find_by_parent_id(cls, _parent_id):
        return cls.query.filter_by(parent_id=_parent_id).all()
    
    @classmethod
    def find_by_name(cls, _name):
        return cls.query.filter_by(name=_name).first()
    
    @classmethod
    def find_all_parent(cls):
        return cls.query.filter_by(parent_id=None).all()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    @classmethod
    def find_with_name(cls, _name):
        query = cls.query

        if _name:
            query = query.filter(cls.name.ilike('%' + _name + '%'))

        return query.all()
        
    @classmethod
    def find_by_document_id(cls, _document_id):
        return cls.query.join(DocumentCategories).filter(DocumentCategories.document_id == _document_id).all()

    @classmethod
    def find_by_id(cls, category_id):
        return cls.query.filter(cls.id == category_id).first()
    
    @classmethod
    def get_stats(cls):
        return cls.query.with_entities(cls.name)\
                        .join(DocumentCategories, DocumentCategories.category_id == cls.id, isouter=True)\
                        .join(Documents, Documents.id == DocumentCategories.document_id, isouter=True)\
                        .add_column(func.count(Documents.id))\
                        .filter(cls.parent_id == None)\
                        .group_by(cls.name)\
                        .all()
    
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id
        }
        return data
    
    @classmethod
    def list_to_dict(cls, categories):
        data = []

        for categorie in categories:
            data.append(categorie.to_dict())

        return data
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
class Documents(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key = True, index=True, autoincrement=True)
    document_name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(5), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, server_default='0', nullable=False)
    download_count = db.Column(db.Integer, server_default='0')
    view_count = db.Column(db.Integer, server_default='0')
    image = db.Column(db.String(255))
    deletion_reason = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, onupdate=datetime.utcnow)    
    status = db.Column(db.Boolean(), nullable=False, server_default='1')
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
        nullable=False)
    categories = db.relationship(
        'Categories',
        secondary='document_categories',
        backref=db.backref('documents', lazy='dynamic'))
    evaluate = db.relationship('Evaluate', backref='documents', lazy=True)
    purchase = db.relationship('Purchase', backref='documents', lazy=True)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'document_name': self.document_name,
            'description': self.description,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'price': self.price,
            'type': self.type,
            'account_id': self.account_id,
            'image': self.image,
            'categories': Categories.list_to_dict(self.categories),
            'evaluate': Evaluate.list_to_dict(self.evaluate),
            'purchase': Purchase.list_to_dict(self.purchase)
        }

        return data
    
    def to_dict_has_evaluate(self):
        data = {
            'id': self.id,
            'document_name': self.document_name,
            'description': self.description,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'price': self.price,
            'type': self.type,
            'account_id': self.account_id,
            'creation_date': self.creation_date,
            'image': self.image,
            'evaluate': Evaluate.list_to_dict(self.evaluate)
        }

        return data
    
    @classmethod
    def to_dict_tuple(self, tuple):
        document = tuple[0]
        fullname_account = tuple[1]

        data = {
            'id': document.id,
            'document_name': document.document_name,
            'description': document.description,
            'view_count': document.view_count,
            'download_count': document.download_count,
            'price': document.price,
            'type': document.type,
            'account_id': document.account_id,
            'image': document.image,
            'categories': Categories.list_to_dict(document.categories),
            'evaluate': Evaluate.list_to_dict(document.evaluate),
            'fullname': fullname_account
        }

        return data
    
    def from_dict(self, data):
        for field in ['document_name', 'description', 'price', 'type']:
            if field in data:
                setattr(self, field, data[field])

    @classmethod
    def list_to_dict(cls, documents):
        data = []

        for document in documents:
            data.append(cls.to_dict_tuple(document))

        return data
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    @classmethod
    def get_month_stats_document(cls, _account_id, year):
        return cls.query.with_entities(extract('month', cls.creation_date), func.count())\
                    .order_by(cls.creation_date)\
                    .filter(cls.account_id==_account_id, extract('year', cls.creation_date)==year, cls.status==True)\
                    .group_by(extract('month', cls.creation_date))\
                    .all()
    
    @classmethod
    def get_month_stats_all_document(cls, year):
        return cls.query.with_entities(extract('month', cls.creation_date), func.count())\
                    .order_by(cls.creation_date)\
                    .filter(extract('year', cls.creation_date)==year, cls.status==True)\
                    .group_by(extract('month', cls.creation_date))\
                    .all()
    
    @classmethod
    def get_month_stats_view_document(cls, _account_id):
        return cls.query.with_entities(cls.document_name, cls.view_count)\
                    .order_by(desc(cls.view_count))\
                    .filter(cls.account_id==_account_id, cls.status==True, cls.view_count > 0)\
                    .limit(5)\
                    .all()
    
    @classmethod
    def get_month_stats_download_document(cls, _account_id):
        return cls.query.with_entities(cls.document_name, cls.download_count)\
                    .order_by(desc(cls.download_count))\
                    .filter(cls.account_id==_account_id, cls.status==True, cls.download_count > 0)\
                    .limit(5)\
                    .all()

    @classmethod
    def find_by_name(cls, _document_name):
        return cls.query.filter_by(document_name=_document_name, status=True).first()
    
    @classmethod
    def find_all_new(cls, limit=None):
        query = cls.query.filter(cls.status==True).order_by(desc(cls.creation_date)).join(Account).add_column(Account.fullname)

        if limit != None:
            query = query.limit(limit)

        return query.all()
    
    @classmethod
    def find_all_view(cls, limit=None):
        query = cls.query.filter_by(status=True).order_by(desc(cls.view_count)).join(Account).add_column(Account.fullname)
        if limit != None:
            query = query.limit(limit)

        return query.all()
    
    @classmethod
    def find_all_saved(cls, _account_id, limit=None):
        query= cls.query.join(Evaluate, Evaluate.document_id==cls.id).\
            join(Account, Account.id == cls.account_id).\
            filter(Evaluate.type=='save', Documents.status==True, Evaluate.account_id==_account_id).\
            add_columns(Account.fullname)
        
        if limit != None:
            query = query.limit(limit)

        return query.all()
    
    @classmethod
    def find_by_id_with_account(cls, _id):
        return cls.query.join(Account).filter(cls.id==_id, cls.status==True).add_column(Account.fullname).first()
    
    @classmethod
    def find_by_id_tuple_with_categories(cls, _id):
        return cls.query.\
            join(cls.categories, isouter=True).\
            with_entities(cls.id, cls.document_name, cls.price, cls.image, cls.description).\
            filter(cls.id==_id, cls.status==True).\
            add_entity(Categories).\
            all()
    
    @classmethod
    def find_by_id_tuple_with_account(cls, _id):
        return cls.query.\
            with_entities(cls.id, cls.document_name, cls.description, cls.view_count, cls.download_count, cls.price, cls.type, cls.account_id, cls.image).\
            join(Account).\
            filter(cls.id==_id, cls.status==True).\
            add_columns(Account.fullname, Account.email).\
            first()
    
    @classmethod
    def find_by_id_and_status(cls, _id):
        return cls.query.filter(cls.id==_id, cls.status==True).first()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter(cls.id==_id).first()
    
    @classmethod
    def find_by_account_id(cls, _account_id):
        return cls.query.\
            join(cls.evaluate, isouter=True).\
            with_entities(cls.id, cls.document_name, cls.view_count, cls.download_count, cls.creation_date, cls.price, cls.image ,Evaluate.type).\
            filter(cls.account_id==_account_id, cls.status==True).\
            all()
    
    @classmethod
    def find_by_account_id_with_paginate(cls, _account_id, page, per_page, type, keyword):
        query = cls.query.filter(cls.account_id==_account_id, cls.status==True)
            
        if type == "free":
            query = query.filter(cls.price==0)
        elif type == "pay_fees":
            query = query.filter(cls.price>0)

        if keyword != "":
            query = query.filter(cls.document_name.ilike('%' + keyword + '%'))
        
        return query.paginate(page=page, per_page=per_page) 
    
    @classmethod
    def find_by_purchase(cls, _id, _account_id):
        return cls.query.join(Purchase, Purchase.document_id==cls.id).\
            join(Account, Account.id==Purchase.account_id).\
            filter(Purchase.account_id==_account_id, cls.id==_id, cls.status==True).\
            order_by(desc(Purchase.date)).\
            add_columns(Account.fullname).\
            first()
    
    @classmethod
    def find_by_category(cls, _category_name, limit):
        return cls.query.join(DocumentCategories, DocumentCategories.document_id==cls.id).\
            join(Categories, Categories.id == DocumentCategories.category_id).\
            filter(Categories.name==_category_name, cls.status==True).\
            join(Account, Account.id==cls.account_id).\
            add_column(Account.fullname).\
            limit(limit).\
            all()
    
    @classmethod
    def find_by_category_with_paginate(cls, _category_name, page, per_page):
        return cls.query.join(DocumentCategories, DocumentCategories.document_id==cls.id).\
            join(Categories, Categories.id == DocumentCategories.category_id).\
            filter(Categories.name==_category_name, cls.status==True).\
            join(Account, Account.id==cls.account_id).\
            add_column(Account.fullname).\
            paginate(page=page, per_page=per_page) 
    
    @classmethod
    def search(cls, page, per_page, value, sort, price, cat_id):
        query =  cls.query.\
            join(Account).\
            add_column(Account.fullname).\
            filter(cls.document_name.ilike('%' + value + '%') | Account.fullname.ilike('%' + value + '%'), cls.status==True)
        
        if (sort == 1):
            query = query.order_by(desc(cls.download_count))
        elif (sort == 2):
            query = query.order_by(desc(cls.view_count))

        if price == 1:
            query = query.filter(cls.price == 0)
        elif price == 2:
            query = query.filter(cls.price > 0)

        if cat_id != 0:
            query = query.join(DocumentCategories, DocumentCategories.document_id==cls.id).\
                    join(Categories, Categories.id == DocumentCategories.category_id).\
                    filter(Categories.id == cat_id)
            
        return query.paginate(page=page, per_page=per_page)        

class DocumentCategories(db.Model):
    __tablename__ = 'document_categories'

    id = db.Column(db.Integer(), primary_key=True)
    document_id = db.Column(db.Integer(), db.ForeignKey(
        'documents.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer(), db.ForeignKey(
        'categories.id', ondelete='CASCADE'))
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find(cls, _document_id, _category_id):
        return cls.query.filter_by(document_id=_document_id, category_id=_category_id).first()

class Evaluate(db.Model):
    __tablename__ = 'evaluate'

    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    document_id = db.Column(db.Integer(), db.ForeignKey(
        'documents.id', ondelete='CASCADE'))
    account_id = db.Column(db.Integer(), db.ForeignKey(
        'account.id', ondelete='CASCADE'))
    
    def to_dict(self):
        data = {
            'id': self.id,
            'type': self.type,
            'document_id': self.document_id,
            'account_id': self.account_id
        }

        return data
    
    @classmethod
    def list_to_dict(cls, evaluate):
        data = []

        for item in evaluate:
            data.append(item.to_dict())

        return data
    
    @classmethod
    def list_to_dict_tuple(cls, evaluate):
        data = []

        for item in evaluate:
            data.append(cls.to_dict_tuple(item))

        return data
    
    @classmethod
    def to_dict_tuple(self, tuple):
        evaluate = tuple[0]
        document = tuple[1]
        fullname_account = tuple[2]
        data = {
            'id': evaluate.id,
            'type': evaluate.type,
            'document_id': evaluate.document_id,
            'account_id': evaluate.account_id,
            'document_name': document.document_name,
            'description': document.description,
            'view_count': document.view_count,
            'download_count': document.download_count,
            'price': document.price,
            'fullname': fullname_account
        }

        return data
    
    @classmethod
    def find_by_type(cls, _document_id, _account_id, _type):
        return cls.query.filter_by(document_id=_document_id, account_id=_account_id, type=_type).first()
    
    @classmethod
    def find(cls, _document_id, _account_id):
        return cls.query.filter_by(document_id=_document_id, account_id=_account_id).all()
    
    @classmethod
    def find_by_document_id_with_tuple(cls, _document_id):
        return cls.query.with_entities(cls.type).filter_by(document_id=_document_id).all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
class Purchase(db.Model):
    __tablename__ = 'purchase'

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Boolean(), nullable=False, server_default='1')
    amount = db.Column(db.Integer(), nullable=False)
    document_id = db.Column(db.Integer(), db.ForeignKey(
        'documents.id', ondelete='CASCADE'))
    account_id = db.Column(db.Integer(), db.ForeignKey(
        'account.id', ondelete='CASCADE'))
    
    def to_dict(self):
        data = {
            'id': self.id,
            'date': self.date,
            'document_id': self.document_id,
            'account_id': self.account_id,
            'amount': self.amount
        }

        return data
    
    @classmethod
    def list_to_dict(cls, purchase):
        data = []

        for item in purchase:
            data.append(item.to_dict())

        return data
    
    @classmethod
    def find(cls, _document_id, _account_id):
        return cls.query.filter(cls.document_id==_document_id, cls.account_id==_account_id).order_by(desc(cls.date)).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
