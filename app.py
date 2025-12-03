from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.exceptions import RequestEntityTooLarge
from flask_login import current_user
from sqlalchemy import inspect
import os

from config import Config
from extensions import db, migrate, login_manager

# блюпринты можно импортировать сразу
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

    # инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ВАЖНО: импорт моделей ПОСЛЕ db.init_app, чтобы избежать циклов
    from models import Car, Customer, Employee, Sale, User, Inquiry  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # локальный импорт во избежание циклов
        return User.query.get(int(user_id))

    # регистрация блюпринтов
    app.register_blueprint(cars_bp, url_prefix='/cars')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(inquiries_bp, url_prefix='/inquiries')

    # фильтр Jinja
    @app.template_filter('money')
    def money(value, cur='RUB'):
        symbols = {'RUB': '₽', 'USD': '$', 'EUR': '€'}
        try:
            v = f"{float(value):,.2f}".replace(",", " ")
        except Exception:
            v = value
        return f"{v} {symbols.get(cur, cur)}"

    @app.route('/')
    def index():
        insp = inspect(db.engine)
        # защищаемся на момент пустой БД (до миграций)
        cars_count = Car.query.count() if insp.has_table("cars") else 0
        customers_count = Customer.query.count() if insp.has_table("customers") else 0
        employees_count = Employee.query.count() if insp.has_table("employees") else 0
        sales_count = Sale.query.count() if insp.has_table("sales") else 0

        stats = {
            'cars': cars_count,
            'customers': customers_count,
            'employees': employees_count,
            'sales': sales_count,
        }
        return render_template(
            'index.html',
            stats=stats,
            user=current_user if current_user.is_authenticated else None
        )

    # однократная инициализация админа после миграций
    def ensure_admin():
        from models import User  # локальный импорт
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        if not email or not password:
            return
        insp = inspect(db.engine)
        if not insp.has_table("users"):
            return
        if not User.query.filter_by(email=email.lower()).first():
            u = User(
                email=email.lower(),
                role="admin",
                last_name="Администратор",
                first_name="Админ",
                middle_name=None,
            )
            u.set_password(password)
            db.session.add(u)
            db.session.commit()

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(e):
        flash('Файл слишком большой. Максимальный размер 5 МБ.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # with app.app_context():
    #     ensure_admin()

    return app


app = create_app()
