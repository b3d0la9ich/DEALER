from flask import render_template, request, redirect, url_for, flash
from . import bp
from extensions import db
from models import Employee
from forms import EmployeeForm
from decorators import admin_required

@bp.route('/')
@admin_required
def list_():
    q = request.args.get('q', '').strip()
    query = Employee.query
    if q:
        like = f"%{q}%"
        query = query.filter(Employee.full_name.ilike(like))
    employees = query.order_by(Employee.created_at.desc()).all()
    return render_template('employees/list.html', employees=employees, q=q)

@bp.route('/create', methods=['GET','POST'])
@admin_required
def create():
    form = EmployeeForm()
    if form.validate_on_submit():
        e = Employee(full_name=form.full_name.data, role=form.role.data)
        db.session.add(e)
        db.session.commit()
        flash('Сотрудник добавлен', 'success')
        return redirect(url_for('employees.list_'))
    return render_template('employees/form.html', form=form, title='Добавить сотрудника')

@bp.route('/<int:employee_id>/edit', methods=['GET','POST'])
@admin_required
def edit(employee_id):
    e = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=e)
    if form.validate_on_submit():
        form.populate_obj(e)
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
