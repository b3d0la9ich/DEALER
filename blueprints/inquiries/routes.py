from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from . import bp
from services.inquiries_client import create_inquiry, list_by_buyer, list_by_seller, update_status
from models import Car, User


def _require(role: str):
    """Быстрая проверка роли с 401/403."""
    if not current_user.is_authenticated:
        abort(401)
    ok = (
        (role == "buyer" and getattr(current_user, "is_buyer", False))
        or (role == "seller" and getattr(current_user, "is_seller", False))
        or (role == "admin" and getattr(current_user, "is_admin", False))
    )
    if not ok:
        abort(403)


@bp.route("/my")
@login_required
def my():
    """
    Покупатель — свои исходящие заявки.
    Продавец/админ — входящие заявки к ним.
    """
    if getattr(current_user, "is_buyer", False):
        items = list_by_buyer(current_user.id)
        return render_template("inquiries/my.html", items=items, role="buyer")

    if getattr(current_user, "is_seller", False) or getattr(current_user, "is_admin", False):
        items = list_by_seller(current_user.id)
        return render_template("inquiries/my.html", items=items, role="seller")

    abort(403)


@bp.route("/incoming")
@login_required
def incoming():
    """Страница входящих заявок для продавца/админа."""
    _require("seller")  # админ тоже пройдёт, если у него is_seller=True
    items = list_by_seller(current_user.id)
    return render_template("inquiries/incoming.html", items=items)


@bp.route("/new/<int:car_id>")
@login_required
def new(car_id: int):
    """Страница с формой создания заявки."""
    _require("buyer")
    car = Car.query.get_or_404(car_id)

    default_message = (
        f"Здравствуйте! Интересует {car.brand} {car.model} ({car.year}). "
        f"Хочу договориться о встрече/просмотре."
    )

    return render_template(
        "inquiries/new.html",
        car=car,
        default_message=default_message,
    )


@bp.route("/create/<int:car_id>", methods=["POST"])
@login_required
def create(car_id: int):
    """Обработка отправки формы заявки."""
    _require("buyer")
    car = Car.query.get_or_404(car_id)

    seller_id = car.seller_id
    if not seller_id:
        admin = User.query.filter_by(role="admin").first()
        seller_id = admin.id if admin else current_user.id

    payload = {
        "car_id": car.id,
        "buyer_id": current_user.id,
        "seller_id": seller_id,
        "message": request.form.get("message") or "",
        "contact_phone": request.form.get("contact_phone") or "",
    }

    pref = request.form.get("preferred_time") or ""
    if pref:
        # Go-сервис ожидает строку "YYYY-MM-DDTHH:MM"
        payload["preferred_time"] = pref

    try:
        create_inquiry(payload)
        flash("Заявка отправлена продавцу", "success")
    except Exception as e:
        flash(f"Не удалось отправить заявку: {e}", "danger")

    return redirect(url_for("cars.detail", car_id=car.id))


@bp.route("/<int:inq_id>/status", methods=["POST"])
@login_required
def set_status(inq_id: int):
    """Изменение статуса заявки продавцом/админом."""
    if not (getattr(current_user, "is_seller", False) or getattr(current_user, "is_admin", False)):
        abort(403)

    status = request.form.get("status", "accepted")
    try:
        update_status(inq_id, status)
        flash("Статус обновлён", "success")
    except Exception as e:
        flash(f"Ошибка обновления: {e}", "danger")

    return redirect(request.referrer or url_for("inq.incoming"))
