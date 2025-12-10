import os
import uuid
from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from . import bp
from extensions import db
from models import Car
from forms import CarForm
from decorators import seller_required

def _allowed_ext(filename: str) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())

def _save_image(file_storage):
    """Сохранить изображение и вернуть имя файла (или None)."""
    if not file_storage or file_storage.filename == '':
        return None
    filename = secure_filename(file_storage.filename)
    if not _allowed_ext(filename):
        flash('Недопустимый формат изображения', 'warning')
        return None
    ext = filename.rsplit('.', 1)[-1].lower()
    unique = f"{uuid.uuid4().hex}.{ext}"
    dst_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(dst_dir, exist_ok=True)
    file_storage.save(os.path.join(dst_dir, unique))
    return unique

def _remove_image(name: str):
    if not name:
        return
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], name))
    except FileNotFoundError:
        pass

@bp.route('/')
def list_():
    q = request.args.get('q', '').strip()
    query = Car.query
    if q:
        like = f"%{q}%"
        query = query.filter((Car.brand.ilike(like)) | (Car.model.ilike(like)) | (Car.vin.ilike(like)))
    cars = query.order_by(Car.created_at.desc()).all()
    return render_template('cars/list.html', cars=cars, q=q)

@bp.route('/my')
@seller_required
def my():
    cars = Car.query.filter_by(seller_id=current_user.id).order_by(Car.created_at.desc()).all()
    return render_template('cars/list.html', cars=cars, q="", my_list=True)

@bp.route('/create', methods=['GET','POST'])
@seller_required
def create():
    form = CarForm()
    if form.validate_on_submit():
        img_name = _save_image(form.image_file.data)
        car = Car(
            vin=form.vin.data.upper().strip(),  # Нормализуем VIN
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            color=form.color.data,
            price=form.price.data,
            currency=form.currency.data,
            status=form.status.data,
            image_url=form.image_url.data or None,
            image_path=img_name,
            description=form.description.data or None,
            seller_id=current_user.id
        )
        db.session.add(car)

        try:
            db.session.commit()
            flash('Объявление успешно создано!', 'success')
            return redirect(url_for('cars.my'))
        except IntegrityError as e:
            db.session.rollback()
            # Проверка конкретной ошибки уникальности
            error_msg = str(e.orig)
            if 'cars_vin_key' in error_msg or 'duplicate key' in error_msg:
                flash(f'Ошибка: Автомобиль с VIN {form.vin.data.upper().strip()} уже существует!', 'danger')
            else:
                flash('Произошла ошибка при создании объявления. Попробуйте еще раз.', 'danger')
            return render_template('cars/form.html', form=form, title='Новое объявление')

    return render_template('cars/form.html', form=form, title='Новое объявление')

@bp.route('/<int:car_id>/edit', methods=['GET','POST'])
@seller_required
def edit(car_id):
    car = Car.query.get_or_404(car_id)
    if not (current_user.is_admin or car.seller_id == current_user.id):
        abort(403)

    # Передаем car_id в форму для корректной валидации VIN
    form = CarForm(car_id=car.id, obj=car)

    if form.validate_on_submit():
        old_img = car.image_path
        form.populate_obj(car)  # обновит стандартные поля

        # Нормализуем VIN
        car.vin = form.vin.data.upper().strip()

        new_img = _save_image(form.image_file.data)
        if new_img:
            car.image_path = new_img
            _remove_image(old_img)

        try:
            db.session.commit()
            flash('Изменения успешно сохранены!', 'success')
            return redirect(url_for('cars.my'))
        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e.orig)
            if 'cars_vin_key' in error_msg or 'duplicate key' in error_msg:
                flash(f'Ошибка: Автомобиль с VIN {form.vin.data.upper().strip()} уже существует!', 'danger')
            else:
                flash('Произошла ошибка при сохранении изменений. Попробуйте еще раз.', 'danger')
            return render_template('cars/form.html', form=form, title='Редактировать объявление')

    return render_template('cars/form.html', form=form, title='Редактировать объявление')

@bp.route('/<int:car_id>/delete', methods=['POST'])
@seller_required
def delete(car_id):
    car = Car.query.get_or_404(car_id)
    if not (current_user.is_admin or car.seller_id == current_user.id):
        abort(403)
    _remove_image(car.image_path)
    db.session.delete(car)
    db.session.commit()
    flash('Объявление удалено', 'info')
    return redirect(url_for('cars.my'))

@bp.route('/<int:car_id>')
def detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('cars/detail.html', car=car)
