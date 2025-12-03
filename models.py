from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---- Пользователи ----
class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="buyer")  # buyer | seller | admin

    # ФИО – в атомарном виде
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64), nullable=True)

    # продавец -> его объявления
    cars = db.relationship("Car", backref="seller", lazy=True)

    # --- утилиты пароля ---
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # --- роли ---
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_seller(self):
        return self.role == "seller"

    @property
    def is_buyer(self):
        return self.role == "buyer"

    @property
    def is_staff(self):
        return self.role in ("seller", "admin")  # для совместимости

    # вычисляемое свойство – чтобы в шаблонах можно было вызывать user.full_name
    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


# ---- Бизнес-сущности ----
class Car(db.Model, TimestampMixin):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(32), unique=True, nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(32))
    price = db.Column(db.Numeric(12, 2), nullable=False)

    # НОВОЕ:
    currency = db.Column(db.String(3), nullable=False, default='RUB')  # RUB | USD | EUR

    status = db.Column(db.String(16), default='in_stock')
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    image_path = db.Column(db.String(255), nullable=True)

    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    sales = db.relationship('Sale', back_populates='car', cascade='all, delete-orphan')


class Customer(db.Model, TimestampMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)

    # ФИО клиента – тоже атомарно
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64), nullable=True)

    phone = db.Column(db.String(32))
    email = db.Column(db.String(128))

    # опциональная привязка к пользователю сайта
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    user = db.relationship('User', backref=db.backref('customer', uselist=False))

    sales = db.relationship('Sale', back_populates='customer', cascade='all, delete-orphan')

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


class Employee(db.Model, TimestampMixin):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)

    # ФИО сотрудника – атомарно
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64), nullable=True)

    role = db.Column(db.String(32), nullable=False, default='manager')

    sales = db.relationship('Sale', back_populates='employee', cascade='all, delete-orphan')

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


class Sale(db.Model, TimestampMixin):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)

    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(32), default='cash')

    car = db.relationship('Car', back_populates='sales')
    customer = db.relationship('Customer', back_populates='sales')
    employee = db.relationship('Employee', back_populates='sales')


class Inquiry(db.Model, TimestampMixin):
    __tablename__ = "inquiries"

    id = db.Column(db.Integer, primary_key=True)

    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    message = db.Column(db.Text, nullable=False)
    preferred_time = db.Column(db.DateTime, nullable=True)
    contact_phone = db.Column(db.String(32), nullable=True)
    status = db.Column(db.String(16), nullable=False, default='new')  # new|accepted|declined|done

    # связи
    car = db.relationship('Car', backref=db.backref('inquiries', lazy='dynamic'))
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])
