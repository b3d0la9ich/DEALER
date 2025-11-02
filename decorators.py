from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user, login_required
from flask import abort

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        if not current_user.is_admin:
            flash("Доступ запрещён (нужна роль admin).", "warning")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return login_required(wrapped)

def seller_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        if not (current_user.is_seller or current_user.is_admin):
            flash("Доступ только для продавцов.", "warning")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return login_required(wrapped)

def owner_or_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        return view(*args, **kwargs)
    return login_required(wrapped)


def buyer_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.is_buyer):
            abort(403)
        return view(*args, **kwargs)
    return wrapped
