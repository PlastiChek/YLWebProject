from flask import Flask, render_template, redirect, session
from forms.AddForm import AddForm
from forms.RegisterForm import RegisterForm
from forms.Loginform import LoginForm
from forms.OfficeForm import OfficeForm
from forms.FindForm import FindForm
from data.users import User
from data.products import Product
from data import db_session
import sys
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/shops.sqlite')
db_session.global_init('db/basket.sqlite')
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
    return render_template('home.html', title='Домашняя страница', username='username')


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
    return render_template('shop.html', title='Домашняя страница')


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
    print(user.password)
    form.nickname.data = user.nickname
    form.name.data = user.name
    form.email.data = user.email
    form.password.data = user.password
    return render_template('office.html', title='Ваш аккаунт', form=form)


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
        if db_sess.query(Product).filter(Product.name == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.name == form.find.data):
                id.append(i.id)
            for index in id:
                stroka = (
                    f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
                    f"Тип продукта: {types[index - 1]}")
                result.append(stroka)
            return render_template('find.html', title='Поиск товаров',
                                   form=form, list=result)
        elif db_sess.query(Product).filter(Product.price == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.price == form.find.data):
                id.append(i.id)
            for index in id:
                stroka = (
                    f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
                    f"Тип продукта: {types[index - 1]}")
                result.append(stroka)
            return render_template('find.html', title='Поиск товаров',
                                   form=form, list=result)

        elif db_sess.query(Product).filter(Product.provider == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.provider == form.find.data):
                id.append(i.id)
            for index in id:
                stroka = (
                    f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
                    f"Тип продукта: {types[index - 1]}")
                result.append(stroka)
            return render_template('find.html', title='Поиск товаров',
                                   form=form, list=result)

        elif db_sess.query(Product).filter(Product.type == form.find.data).first():
            for i in db_sess.query(Product).filter(Product.type == form.find.data):
                id.append(i.id)
            for index in id:
                stroka = (
                    f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
                    f"Тип продукта: {types[index - 1]}")
                result.append(stroka)
            return render_template('find.html', title='Поиск товаров',
                                   form=form, list=result)

        return redirect('/success')

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
        return redirect('/add')
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
    for index in range(len(names)):
        stroka = (
            f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
            f"Тип продукта: {types[index - 1]}")
        result.append(stroka)

    return render_template('catalog.html', list=result)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
    db_sess = db_session.create_session()
    products_db = db_sess.query(Product).all()
    names = [product.name for product in products_db]
    prices = [product.price for product in products_db]
    providers = [product.provider for product in products_db]
    types = [product.type for product in products_db]
    result = []
    for index in range(len(names)):
        stroka = (
            f"Название: {names[index - 1]}, Цена: {prices[index - 1]}, Поставщик: {providers[index - 1]}, "
            f"Тип продукта: {types[index - 1]}")
        result.append(stroka)

    return render_template('catalog.html', list=result)


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')