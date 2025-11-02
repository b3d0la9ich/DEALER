from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, Optional, Email, Length
from wtforms import StringField, IntegerField, DecimalField, SelectField, DateField, SubmitField, PasswordField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from wtforms.fields import DateTimeLocalField

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class CarForm(FlaskForm):
    price = DecimalField('Цена', validators=[DataRequired()])
    currency = SelectField('Валюта', choices=[('RUB','₽ Рубли'),('USD','$ Доллары'),('EUR','€ Евро')], default='RUB')
    status = SelectField('Статус', choices=[('in_stock','В наличии'),('reserved','Резерв'),('sold','Продано')])
    vin = StringField('VIN', validators=[DataRequired()])
    brand = StringField('Марка', validators=[DataRequired()])
    model = StringField('Модель', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    color = StringField('Цвет', validators=[Optional()])
    image_url = StringField('Фото (URL)', validators=[Optional()])
    image_file = FileField('Фото (файл)', validators=[Optional(), FileAllowed(['jpg','jpeg','png','gif','webp'], 'Только изображения!')])
    description = TextAreaField('Описание', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Сохранить')

class CustomerForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    submit = SubmitField('Сохранить')

class EmployeeForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    role = SelectField('Роль', choices=[('manager','Менеджер'),('seller','Продавец'),('admin','Админ')])
    submit = SubmitField('Сохранить')

class SaleForm(FlaskForm):
    car_id = SelectField('Автомобиль', coerce=int)
    customer_id = SelectField('Клиент', coerce=int)
    employee_id = SelectField('Сотрудник', coerce=int)
    sale_date = DateField('Дата продажи', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    payment_method = SelectField('Оплата', choices=[('cash','Наличные'),('card','Карта'),('transfer','Перевод')])
    submit = SubmitField('Сохранить')

class RegisterForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(max=128)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Роль', choices=[('buyer','Покупатель'),('seller','Продавец')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

# forms.py


class InquiryForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=5000)])
    preferred_time = DateTimeLocalField('Желаемое время встречи', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    contact_phone = StringField('Контактный телефон', validators=[Optional(), Length(max=32)])
    submit = SubmitField('Отправить заявку')
