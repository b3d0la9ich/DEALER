from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    IntegerField,
    DecimalField,
    SelectField,
    DateField,
    SubmitField,
    PasswordField,
    TextAreaField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, Length, ValidationError
from models import Car, User
from flask import current_app


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class CarForm(FlaskForm):
    price = DecimalField('Цена', validators=[DataRequired()])
    currency = SelectField(
        'Валюта',
        choices=[
            ('RUB', '₽ Рубли'),
            ('USD', '$ Доллары'),
            ('EUR', '€ Евро'),
        ],
        default='RUB',
    )
    status = SelectField(
        'Статус',
        choices=[
            ('in_stock', 'В наличии'),
            ('reserved', 'Резерв'),
            ('sold', 'Продано'),
        ],
    )
    vin = StringField('VIN', validators=[
        DataRequired(),
        Length(min=10, max=32, message='VIN должен содержать от 10 до 32 символов')
    ])
    brand = StringField('Марка', validators=[DataRequired()])
    model = StringField('Модель', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    color = StringField('Цвет', validators=[Optional()])
    image_url = StringField('Фото (URL)', validators=[Optional()])
    image_file = FileField(
        'Фото (файл)',
        validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения!')],
    )
    description = TextAreaField('Описание', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Сохранить')

    def __init__(self, car_id=None, *args, **kwargs):
        """Инициализация формы с возможностью передачи ID автомобиля для редактирования"""
        super().__init__(*args, **kwargs)
        self.car_id = car_id

    def validate_vin(self, field):
        """Проверка уникальности VIN"""
        vin = field.data.upper().strip()  # Приводим к верхнему регистру и убираем пробелы

        # Проверка формата VIN
        if not all(c.isalnum() for c in vin):
            raise ValidationError('VIN может содержать только буквы и цифры')

        # Проверка на запрещенные буквы (в реальном VIN их нет)
        invalid_chars = ['I', 'O', 'Q']
        for char in invalid_chars:
            if char in vin:
                raise ValidationError(f'VIN не может содержать букву "{char}"')

        # Проверка уникальности
        query = Car.query.filter_by(vin=vin)

        # При редактировании исключаем текущий автомобиль из проверки
        if self.car_id:
            query = query.filter(Car.id != self.car_id)

        existing_car = query.first()

        if existing_car:
            raise ValidationError(f'Автомобиль с VIN {vin} уже существует в базе')


class CustomerForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Optional()])
    phone = StringField('Телефон', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Сохранить')


class EmployeeForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Optional()])
    role = SelectField(
        'Роль',
        choices=[
            ('manager', 'Менеджер'),
            ('seller', 'Продавец'),
            ('admin', 'Админ'),
        ],
    )
    submit = SubmitField('Сохранить')


class SaleForm(FlaskForm):
    car_id = SelectField('Автомобиль', coerce=int)
    customer_id = SelectField('Клиент', coerce=int)
    employee_id = SelectField('Сотрудник', coerce=int)
    sale_date = DateField('Дата продажи', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    payment_method = SelectField(
        'Оплата',
        choices=[
            ('cash', 'Наличные'),
            ('card', 'Карта'),
            ('transfer', 'Перевод'),
        ],
    )
    submit = SubmitField('Сохранить')


class RegisterForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField(
        'Роль',
        choices=[
            ('buyer', 'Покупатель'),
            ('seller', 'Продавец'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        """Проверка уникальности email"""
        email = field.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValidationError('Пользователь с таким email уже зарегистрирован')


class InquiryForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[DataRequired(), Length(max=5000)])
    preferred_time = DateTimeLocalField(
        'Желаемое время встречи',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()],
    )
    contact_phone = StringField('Контактный телефон', validators=[Optional(), Length(max=32)])
    submit = SubmitField('Отправить заявку')
