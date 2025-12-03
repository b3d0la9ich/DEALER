from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func

from . import bp
from extensions import db
from models import Customer
from forms import CustomerForm


def split_full_name(full_name: str):
    """
    Разбивает строку 'Фамилия Имя Отчество...' на части.
    Минимум — фамилия; имя/отчество могут быть пустыми.
    """
    parts = (full_name or "").strip().split()
    last = parts[0] if len(parts) > 0 else ""
    first = parts[1] if len(parts) > 1 else ""
    middle = " ".join(parts[2:]) if len(parts) > 2 else None
    return last, first, middle


@bp.route('/')
def list_():
    q = request.args.get('q', '').strip()
    query = Customer.query
    if q:
        like = f"%{q}%"
        # поиск по склеенному ФИО + телефону
        name_expr = func.concat_ws(' ', Customer.last_name, Customer.first_name, Customer.middle_name)
        query = query.filter((name_expr.ilike(like)) | (Customer.phone.ilike(like)))
    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/list.html', customers=customers, q=q)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    form = CustomerForm()
    if form.validate_on_submit():
        last, first, middle = split_full_name(form.full_name.data)
        c = Customer(
            last_name=last,
            first_name=first,
            middle_name=middle,
            phone=form.phone.data,
            email=form.email.data,
        )
        db.session.add(c)
        db.session.commit()
        flash('Клиент добавлен', 'success')
        return redirect(url_for('customers.list_'))
    return render_template('customers/form.html', form=form, title='Добавить клиента')


@bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit(customer_id):
    c = Customer.query.get_or_404(customer_id)
    form = CustomerForm()

    if request.method == 'GET':
        # в форму подаём склеенное ФИО из свойства модели
        form.full_name.data = c.full_name
        form.phone.data = c.phone
        form.email.data = c.email

    if form.validate_on_submit():
        last, first, middle = split_full_name(form.full_name.data)
        c.last_name = last
        c.first_name = first
        c.middle_name = middle
        c.phone = form.phone.data
        c.email = form.email.data

        db.session.commit()
        flash('Изменения сохранены', 'success')
        return redirect(url_for('customers.list_'))

    return render_template('customers/form.html', form=form, title='Редактировать клиента')


@bp.route('/<int:customer_id>/delete', methods=['POST'])
def delete(customer_id):
    c = Customer.query.get_or_404(customer_id)
    db.session.delete(c)
    db.session.commit()
    flash('Клиент удалён', 'info')
    return redirect(url_for('customers.list_'))
