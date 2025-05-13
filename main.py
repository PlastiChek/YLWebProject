from flask import Flask, render_template, redirect, session
from forms.AddForm import AddForm
from forms.RegisterForm import RegisterForm
from forms.Loginform import LoginForm
from forms.OfficeForm import OfficeForm
from forms.FindForm import FindForm
from forms.AddingBasketForm import AddingBasketForm
from forms.DeleteForm import DeleteForm
from data.users import User
from data.products import Product
from data.basket import Basket
from data import db_session
import sys
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/shops.sqlite')
db_sess = db_session.create_session()


def map_image():
    map_request = "http://static-maps.yandex.ru/1.x/?ll=37.681281,55.677089&spn=0.01,0.01&size=600,450&l=map&pt=37.681281,55.677089,pm2pnm~37.681281,55.677089,pm2pnm"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "static/img/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)


map_image()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if not db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Такого пользователя нет")
        if not db_sess.query(User).filter(User.password == form.password.data).first():
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Неверный пароль")
        session["user_id"] = user.id
        return redirect('/success')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def login1():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой никнейм уже есть")
        elif db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже есть")
        elif db_sess.query(User).filter(User.password == form.password.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пароль уже есть")
        user = User(
            nickname=form.nickname.data,
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/success')
def main():
    return render_template('shop.html')


@app.route("/office", methods=['GET', 'POST'])
def my_office():
    """
    Обработка страницы профиля
    :return: страничка user
    """
    form = OfficeForm()
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    user = db_sess.query(User).get(user_id)
    form.nickname.data = user.nickname
    form.name.data = user.name
    form.email.data = user.email
    form.password.data = user.password
    return render_template('office.html', title='Ваш аккаунт', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/find', methods=['GET', 'POST'])
def find():
    form = FindForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        products_db = db_sess.query(Product).all()
        names = [product.name for product in products_db]
        prices = [product.price for product in products_db]
        providers = [product.provider for product in products_db]
        types = [product.type for product in products_db]
        result = []
        id = []
        n, p, pr, ty = [], [], [], []
        if db_sess.query(Product).filter(Product.name == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.name == form.find.data):
                id.append(i.id)
            for index in id:
                n.append(names[index - 1])
                p.append(prices[index - 1])
                pr.append(providers[index - 1])
                ty.append(types[index - 1])
            return render_template('find-success.html', list=n, list1=p, list2=pr,
                                   list3=ty)
        elif db_sess.query(Product).filter(Product.price == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.price == form.find.data):
                id.append(i.id)
            for index in id:
                n.append(names[index - 1])
                p.append(prices[index - 1])
                pr.append(providers[index - 1])
                ty.append(types[index - 1])
            return render_template('find-success.html', list=n, list1=p, list2=pr,
                                   list3=ty)

        elif db_sess.query(Product).filter(Product.provider == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.provider == form.find.data):
                id.append(i.id)
            for index in id:
                n.append(names[index - 1])
                p.append(prices[index - 1])
                pr.append(providers[index - 1])
                ty.append(types[index - 1])
            return render_template('find-success.html', list=n, list1=p, list2=pr,
                                   list3=ty)

        elif db_sess.query(Product).filter(Product.type == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.type == form.find.data):
                id.append(i.id)
            for index in id:
                n.append(names[index - 1])
                p.append(prices[index - 1])
                pr.append(providers[index - 1])
                ty.append(types[index - 1])
            return render_template('find-success.html', list=n, list1=p, list2=pr,
                                   list3=ty)

        return render_template('find.html', title='Поиск товаров',
                               form=form, message="Неверные данные")

    return render_template('find.html', title='Поиск товаров', form=form)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        if not (form.price.data).isdigit():
            return render_template('add.html', title='Добавить товар',
                                   form=form,
                                   message="Цена может содержать только цифры")
        elif not ((form.name.data).replace(" ", "")).isalpha():
            return render_template('add.html', title='Добавить товар',
                                   form=form,
                                   message="Название товара может содержать только буквы")
        elif not ((form.provider.data).replace(" ", "")).isalpha():
            return render_template('add.html', title='Добавить товар',
                                   form=form,
                                   message="Поставщик товара может содержать только буквы")
        elif not ((form.type.data).replace(" ", "")).isalpha():
            return render_template('add.html', title='Добавить товар',
                                   form=form,
                                   message="Тип товара может содержать только буквы")
        product = Product(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            type=form.type.data,
        )
        db_sess.add(product)
        db_sess.commit()
        return render_template('add.html', title='Добавить товар',
                               form=form,
                               message="Товар добавлен")
    return render_template('add.html', title='Добавить товар', form=form)


@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    db_sess = db_session.create_session()
    products_db = db_sess.query(Product).all()
    names = [product.name for product in products_db]
    prices = [product.price for product in products_db]
    providers = [product.provider for product in products_db]
    types = [product.type for product in products_db]
    result = []
    for i in range(len(names)):
        result.append([names[i], prices[i], providers[i], types[i]])
    return render_template('catalog.html', title='Домашняя страница', list=names, list1=prices, list2=providers,
                           list3=types)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
    db_sess = db_session.create_session()
    products_db = db_sess.query(Basket).all()
    names = [product.name for product in products_db]
    prices = [product.price for product in products_db]
    providers = [product.provider for product in products_db]
    numbers = [product.number for product in products_db]
    result = []
    for i in range(len(names)):
        result.append([names[i], prices[i], providers[i], numbers[i]])
    return render_template('basket.html', title='Домашняя страница', list=names, list1=prices, list2=providers,
                           list3=numbers)


@app.route('/adding-basket', methods=['GET', 'POST'])
def adding_basket():
    form = AddingBasketForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(Product).filter(Product.name == form.name.data).first():
            return render_template('adding-basket.html', title='Добавить товар в корзину',
                                   form=form, message='Такого названия товара нет')
        elif not db_sess.query(Product).filter(Product.price == form.price.data).first():
            return render_template('adding-basket.html', title='Добавить товар в корзину',
                                   form=form, message='Такой цены товара нет')

        elif not db_sess.query(Product).filter(Product.provider == form.provider.data).first():
            return render_template('adding-basket.html', title='Добавить товар в корзину',
                                   form=form, message='Такого поставщика товара нет')
        elif form.number.data == 0 or not form.number.data.isdigit():
            return render_template('adding-basket.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('adding-basket.html', title='Добавить товар в корзину',
                               form=form, message='Товар в корзине')

    return render_template('adding-basket.html', title='Добавить товар в корзину', form=form)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    form = DeleteForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(Basket).filter(Basket.name == form.name.data).first():
            return render_template('adding-basket.html', title='Удалить товар',
                                   form=form, message='Такого названия товара нет')
        elif not db_sess.query(Basket).filter(Basket.price == form.price.data).first():
            return render_template('delete.html', title='Удалить товар',
                                   form=form, message='Такой цены товара нет')

        elif db_sess.query(Basket).filter(Basket.provider == form.provider.data).first():
            return render_template('delete.html', title='Удалить товар',
                                   form=form, message='Такого поставщика товара нет')
        elif db_sess.query(Basket).filter(Basket.provider == form.provider.data).first():
            return render_template('delete.html', title='Удалить товар',
                                   form=form, message='Такого кол-ва товара нет')

        product = db_sess.query(User).filter(Basket.name == form.name.data, Basket.price == form.price.data,
                                             Basket.provider == form.provider.data,
                                             Basket.number == form.number.data).first()
        db_sess.delete(product)
        db_sess.commit()

        return render_template('delete.html', title='Удалить товар',
                               form=form, message='Товар удалён')

    return render_template('delete.html', title='Удалить товар', form=form)


@app.route('/buy', methods=['GET', 'POST'])
def buy():
    db_sess = db_session.create_session()
    products_db = db_sess.query(Basket).all()
    names = [product.name for product in products_db]
    prices = [product.price for product in products_db]
    providers = [product.provider for product in products_db]
    numbers = [product.number for product in products_db]
    result = []
    count = 0
    for i in range(len(names)):
        count += prices[i] * numbers[i]
        result.append([names[i], prices[i], providers[i], numbers[i]])
    return render_template('buy.html', title='Домашняя страница', list=names, list1=prices, list2=providers,
                           list3=numbers, message=f"Итого: {count} рублей")


class Popular(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = StringField('Цена', validators=[DataRequired()])
    provider = StringField('Поставщик', validators=[DataRequired()])
    type = StringField('Тип товара', validators=[DataRequired()])
    number = StringField('Кол-во', validators=[DataRequired()])
    submit = SubmitField('Добавить в корзину')


@app.route('/cola', methods=['GET', 'POST'])
def cola():
    form = Popular()
    form.name.data = "Кока-кола"
    form.price.data = 150
    form.provider.data = "Россия"
    form.type.data = "Продукты"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/eclipse', methods=['GET', 'POST'])
def eclipse():
    form = Popular()
    form.name.data = "Жвачка eclipse"
    form.price.data = 23
    form.provider.data = "Россия"
    form.type.data = "Продукты"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/liner', methods=['GET', 'POST'])
def liner():
    form = Popular()
    form.name.data = "Лайнер"
    form.price.data = 215
    form.provider.data = "Китай"
    form.type.data = "Концелярия"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/milka', methods=['GET', 'POST'])
def milka():
    form = Popular()
    form.name.data = "Милка"
    form.price.data = 180
    form.provider.data = "Россия"
    form.type.data = "Продукты"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/notebook', methods=['GET', 'POST'])
def notebook():
    form = Popular()
    form.name.data = "Блокнот"
    form.price.data = 100
    form.provider.data = "Россия"
    form.type.data = "Концелярия"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/pencil', methods=['GET', 'POST'])
def pencil():
    form = Popular()
    form.name.data = "Карандаш"
    form.price.data = 120
    form.provider.data = "Россия"
    form.type.data = "Концелярия"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


@app.route('/lipton', methods=['GET', 'POST'])
def lipton():
    form = Popular()
    form.name.data = "Липтон"
    form.price.data = 80
    form.provider.data = "Россия"
    form.type.data = "Продукты"
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.number.data == "0" or not form.number.data.isdigit():
            return render_template('popular.html', title='Добавить товар в корзину',
                                   form=form, message='Введите кол-во товаров')

        product = Basket(
            name=form.name.data,
            price=form.price.data,
            provider=form.provider.data,
            number=form.number.data
        )
        db_sess.add(product)
        db_sess.commit()

        return render_template('popular.html', title='Добавить товар в корзину',
                               form=form, message="Товар в корзине")

    return render_template('popular.html', title='Популярные товары', form=form)


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
