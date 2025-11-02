from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.exceptions import RequestEntityTooLarge
from config import Config
from extensions import db, migrate, login_manager
from models import Car, Customer, Employee, Sale, User, Inquiry
from flask_login import current_user
from sqlalchemy import inspect
import os

from blueprints.cars import bp as cars_bp
from blueprints.customers import bp as customers_bp
from blueprints.sales import bp as sales_bp
from blueprints.employees import bp as employees_bp
from blueprints.auth import bp as auth_bp
from blueprints.admin import bp as admin_bp
from blueprints.inquiries import bp as inquiries_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprints
    app.register_blueprint(cars_bp, url_prefix='/cars')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')

    # ---- фильтры Jinja ----
    @app.template_filter('money')
    def money(value, cur='RUB'):
        """Форматирование суммы с символом валюты и пробелом-разделителем тысяч."""
        symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€'}
        try:
            v = f"{float(value):,.2f}".replace(",", " ")
        except Exception:
            v = value
        return f"{v} {symbols.get(cur, cur)}"

    @app.route('/')
    def index():
        stats = {
            'cars': Car.query.count(),
            'customers': Customer.query.count(),
            'employees': Employee.query.count(),
            'sales': Sale.query.count(),
        }
        return render_template(
            'index.html',
            stats=stats,
            user=current_user if current_user.is_authenticated else None
        )

    # ---- однократная инициализация данных (админ) ----
    def ensure_admin():
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        if not email or not password:
            return

        # создаём админа только если таблица users уже есть
        insp = inspect(db.engine)
        if not insp.has_table("users"):
            return  # миграции ещё не накатаны

        if not User.query.filter_by(email=email.lower()).first():
            u = User(email=email.lower(), role="admin", full_name="Администратор")
            u.set_password(password)
            db.session.add(u)
            db.session.commit()

    # обработчик слишком большого файла (HTTP 413)
    @app.errorhandler(RequestEntityTooLarge)
    def too_large(e):
        flash('Файл слишком большой. Максимальный размер 5 МБ.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # выполнить ensure_admin один раз при старте
    with app.app_context():
        ensure_admin()

    return app


app = create_app()
