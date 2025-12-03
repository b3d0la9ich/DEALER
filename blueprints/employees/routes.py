from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func

from . import bp
from extensions import db
from models import Employee
from forms import EmployeeForm
from decorators import admin_required


def split_full_name(full_name: str):
    parts = (full_name or "").strip().split()
    last = parts[0] if len(parts) > 0 else ""
    first = parts[1] if len(parts) > 1 else ""
    middle = " ".join(parts[2:]) if len(parts) > 2 else None
    return last, first, middle


@bp.route('/')
@admin_required
def list_():
    q = request.args.get('q', '').strip()
    query = Employee.query
    if q:
        like = f"%{q}%"
        name_expr = func.concat_ws(' ', Employee.last_name, Employee.first_name, Employee.middle_name)
        query = query.filter(name_expr.ilike(like))
    employees = query.order_by(Employee.created_at.desc()).all()
    return render_template('employees/list.html', employees=employees, q=q)


@bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    form = EmployeeForm()
    if form.validate_on_submit():
        last, first, middle = split_full_name(form.full_name.data)
        e = Employee(
            last_name=last,
            first_name=first,
            middle_name=middle,
            role=form.role.data,
        )
        db.session.add(e)
        db.session.commit()
        flash('Сотрудник добавлен', 'success')
        return redirect(url_for('employees.list_'))
    return render_template('employees/form.html', form=form, title='Добавить сотрудника')


@bp.route('/<int:employee_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(employee_id):
    e = Employee.query.get_or_404(employee_id)
    form = EmployeeForm()

    if request.method == 'GET':
        form.full_name.data = e.full_name
        form.role.data = e.role

    if form.validate_on_submit():
        last, first, middle = split_full_name(form.full_name.data)
        e.last_name = last
        e.first_name = first
        e.middle_name = middle
        e.role = form.role.data

        db.session.commit()
        flash('Изменения сохранены', 'success')
        return redirect(url_for('employees.list_'))

    return render_template('employees/form.html', form=form, title='Редактировать сотрудника')


@bp.route('/<int:employee_id>/delete', methods=['POST'])
@admin_required
def delete(employee_id):
    e = Employee.query.get_or_404(employee_id)
    db.session.delete(e)
    db.session.commit()
    flash('Сотрудник удалён', 'info')
    return redirect(url_for('employees.list_'))
