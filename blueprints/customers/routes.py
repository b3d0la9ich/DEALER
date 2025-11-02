from flask import render_template, request, redirect, url_for, flash
from . import bp
from extensions import db
from models import Customer
from forms import CustomerForm

@bp.route('/')
def list_():
    q = request.args.get('q', '').strip()
    query = Customer.query
    if q:
        like = f"%{q}%"
        query = query.filter((Customer.full_name.ilike(like)) | (Customer.phone.ilike(like)))
    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/list.html', customers=customers, q=q)

@bp.route('/create', methods=['GET','POST'])
def create():
    form = CustomerForm()
    if form.validate_on_submit():
        c = Customer(full_name=form.full_name.data, phone=form.phone.data, email=form.email.data)
        db.session.add(c)
        db.session.commit()
        flash('Клиент добавлен', 'success')
        return redirect(url_for('customers.list_'))
    return render_template('customers/form.html', form=form, title='Добавить клиента')

@bp.route('/<int:customer_id>/edit', methods=['GET','POST'])
def edit(customer_id):
    c = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=c)
    if form.validate_on_submit():
        form.populate_obj(c)
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
