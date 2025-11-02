from flask import render_template, request, redirect, url_for, flash
from . import bp
from extensions import db
from models import Sale, Car, Customer, Employee
from forms import SaleForm
from flask_login import login_required, current_user

@bp.route('/')
def list_():
    sales = (
        Sale.query
        .join(Sale.car)
        .join(Sale.customer)
        .join(Sale.employee)
        .order_by(Sale.sale_date.desc())
        .all()
    )
    return render_template('sales/list.html', sales=sales)

@bp.route('/create', methods=['GET','POST'])
def create():
    form = SaleForm()
    form.car_id.choices = [(c.id, f"{c.brand} {c.model} ({c.vin})") for c in Car.query.filter(Car.status!='sold').all()]
    form.customer_id.choices = [(c.id, c.full_name) for c in Customer.query.all()]
    form.employee_id.choices = [(e.id, f"{e.full_name} — {e.role}") for e in Employee.query.all()]

    if form.validate_on_submit():
        sale = Sale(
            car_id=form.car_id.data,
            customer_id=form.customer_id.data,
            employee_id=form.employee_id.data,
            sale_date=form.sale_date.data,
            price=form.price.data,
            payment_method=form.payment_method.data,
        )
        db.session.add(sale)
        car = Car.query.get(form.car_id.data)
        if car:
            car.status = 'sold'
        db.session.commit()
        flash('Продажа зарегистрирована', 'success')
        return redirect(url_for('sales.list_'))

    return render_template('sales/form.html', form=form, title='Новая сделка')

@bp.route('/<int:sale_id>/delete', methods=['POST'])
def delete(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    if sale.car:
        sale.car.status = 'in_stock'
    db.session.delete(sale)
    db.session.commit()
    flash('Продажа удалена', 'info')
    return redirect(url_for('sales.list_'))

@bp.route('/my')
@login_required
def my():  # <-- endpoint будет 'sales.my'
    # у покупателя при регистрации мы создаём связанного Customer
    customer = getattr(current_user, "customer", None)
    if not customer:
        flash("Для аккаунта не найден профиль клиента.", "warning")
        return redirect(url_for("index"))
    sales = Sale.query.filter_by(customer_id=customer.id).order_by(Sale.sale_date.desc()).all()
    return render_template("sales/list.html", sales=sales, my_list=True)
