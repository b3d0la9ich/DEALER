from flask import render_template, request, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import bp
from services.inquiries_client import create_inquiry, list_by_buyer, list_by_seller, update_status
from models import Car, User


def _require(role: str):
    """Быстрая проверка роли с 401/403."""
    if not current_user.is_authenticated:
        abort(401)
    ok = (
        (role == 'buyer'  and getattr(current_user, 'is_buyer',  False)) or
        (role == 'seller' and getattr(current_user, 'is_seller', False)) or
        (role == 'admin'  and getattr(current_user, 'is_admin',  False))
    )
    if not ok:
        abort(403)


@bp.route("/my")
@login_required
def my():
    # Покупателю — его исходящие заявки,
    # Продавцу/админу — входящие (как в вашем текущем шаблоне)
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
    # Отдельная страница входящих заявок для продавца (то, что просит меню)
    _require('seller')  # админ тоже пройдёт, если у него is_seller=False — поменяйте при желании
    items = list_by_seller(current_user.id)
    return render_template("inquiries/incoming.html", items=items)


@bp.route("/create/<int:car_id>", methods=["POST"])
@login_required
def create(car_id):
    _require('buyer')
    car = Car.query.get_or_404(car_id)

    # Продавец — владелец объявления; если нет — подстрахуемся админом (или текущим пользователем как продавцом)
    seller_id = car.seller_id
    if not seller_id:
        admin = User.query.filter_by(role="admin").first()
        seller_id = admin.id if admin else current_user.id

    payload = {
        "car_id": car.id,
        "buyer_id": current_user.id,
        "seller_id": seller_id,
        "message": request.form.get("message") or "",
        "contact_phone": request.form.get("phone") or "",
    }
    pref = request.form.get("preferred_time") or ""
    if pref:
        # Go-сервис ожидает ISO 8601
        payload["preferred_time"] = pref

    try:
        create_inquiry(payload)
        flash("Заявка отправлена продавцу", "success")
    except Exception as e:
        flash(f"Не удалось отправить заявку: {e}", "danger")
    return redirect(url_for("cars.detail", car_id=car.id))


@bp.route("/<int:inq_id>/status", methods=["POST"])
@login_required
def set_status(inq_id):
    if not (getattr(current_user, "is_seller", False) or getattr(current_user, "is_admin", False)):
        abort(403)
    status = request.form.get("status", "accepted")
    try:
        update_status(inq_id, status)
        flash("Статус обновлён", "success")
    except Exception as e:
        flash(f"Ошибка обновления: {e}", "danger")
    # Вернёмся туда, откуда пришли, иначе — на входящие
    return redirect(request.referrer or url_for("inq.incoming"))
