from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import bp
from extensions import db
from models import User, Customer
from forms import LoginForm, RegisterForm

@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Добро пожаловать!", "success")
            return redirect(request.args.get("next") or url_for("index"))
        flash("Неверный email или пароль", "danger")
    return render_template("auth/login.html", form=form)

@bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Вы вышли из системы", "info")
    return redirect(url_for("index"))

@bp.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует", "warning")
            return render_template("auth/register.html", form=form)
        user = User(email=email, role=form.role.data, full_name=form.full_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        # если это покупатель — создаём Customer, чтобы потом видеть «мои покупки»
        if user.role == "buyer":
            db.session.add(Customer(full_name=user.full_name or email, email=email, user_id=user.id))
        db.session.commit()
        flash("Регистрация выполнена. Войдите в систему.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
