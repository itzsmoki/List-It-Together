import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required
from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
import json
import aiohttp
import asyncio
import random
import string

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///list.db")


def check_format(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        image_data = response.content
        img = Image.open(BytesIO(image_data))
        img_format = img.format
        if img_format.lower() in ['jpeg', 'png', 'jpg', 'webp', 'svg', 'bmp', 'tiff']:
            return True
        else:
            return False
    except requests.Timeout:
        raise TimeoutError("Timeout error")
    except Exception as e:
        return False


def escape(name):
    name = name.replace("'", "§quote§")
    name = name.replace('"', "§double_quotes§")
    name = name.replace("&", "§and§")
    name = name.replace("'", "§quote§")
    return name


def generate_code():
    chars = string.digits + string.ascii_uppercase
    while (True):
        code = ''.join(random.choice(chars) for _ in range(7))
        codes = db.execute("SELECT code FROM lists")
        if str(code) not in str(codes):
            return code


async def fetch(session, url):
    headers = {'Accept': 'text/html'}
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def find(word):
    if " " in word:
        word = word.replace(" ", "+")
    url = f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={word}&search_simple=1&action=process'
    domain = "https://world.openfoodfacts.org"

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)

        soup = BeautifulSoup(html, 'lxml')

        mydivs = soup.find_all("a")
        mydivs1 = soup.find_all("img")
        names = []
        brands = []
        images = []
        i = 0
        a = 0

        for a_tag in mydivs:
            if 'href' in a_tag.attrs:
                href = a_tag['href']
                if "/product" in href and "cgi" not in href:
                    i += 1
                    link = domain + href
                    letters = []
                    for letter in link:
                        if letter >= '0' and letter <= '9':
                            letters.append(letter)
                        if (letter < '0' or letter > '9') and len(letters) >= 8:
                            break
                    code = "".join(letters)

                    async with session.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json") as response:
                        json_data = await response.json()

                    if 'brands' in json_data.get('product', {}):
                        brand_name = json_data['product']['brands']
                        brand_name = escape(brand_name)
                        brands.append(brand_name)
                    else:
                        brands.append(" ")
                    if 'product_name' in json_data.get('product', {}):
                        product_name = json_data['product']['product_name']
                        product_name = escape(product_name)
                        names.append(product_name)
                    else:
                        names.append(" ")

        for div in mydivs1:
            img = div['src']
            if "products" in img:
                img = div['src']
                imghd = img.replace("100.jpg", "200.jpg")
                images.append(imghd)
                a += 1
            elif "silhouette.svg" in img:
                images.append("/static/image.svg")
                a += 1

        return names, brands, images


@app.route('/search/<word>', methods=['GET'])
@login_required
def search(word):
    if request.method == "GET":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        names, brands, images = loop.run_until_complete(find(word))
        if 'list' not in session:
            return redirect("/")

        return render_template("search.html", names=names, brands=brands, images=images, word=word)


@app.route('/add', methods=['POST'])
@login_required
def add():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session['user_id'], session['list']):
            session.pop('list')
            return ('Unauthorized action', 400)
        action = request.form.get("action")
        name = request.form.get('name')
        brand = request.form.get('brand')
        image = request.form.get('image')
        priority = request.form.get('priority')

        if action == 'product':
            if not image:
                image = "/static/image.svg"
            if name.isspace():
                return ("Invalid name", 400)
            if not name:
                return ('Missing name', 400)
            try:
                if check_format(image) == False:
                    image = "/static/image.svg"
            except TimeoutError:
                return redirect("/list")
            if not priority:
                priority = 1
            if int(priority) > 2 or int(priority) < 0:
                return ('Invalide priority level', 400)
            if len(name) > 60:
                return ('Product name is too long', 400)
            if len(brand) > 25:
                return ('Brand name is too long', 400)
            if db.execute("SELECT * FROM items WHERE name = ? AND image = ? AND brand = ? AND code = ?", name, image, brand, session['list']):
                return redirect("/list")
            name = escape(name)
            brand = escape(brand)
            image = escape(image)
            db.execute("DELETE FROM history WHERE name = ? AND image = ? AND brand = ? AND code = ?",
                       name, image, brand, session['list'])
            db.execute("INSERT INTO items (name, brand, image, priority, code, user_id, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       name, brand, image, priority, session['list'], session['user_id'], datetime.now())
            return ("Item successfully added", 200)

        if action == 'favorite':
            if not image:
                image = "/static/image.svg"
            if name.isspace():
                return ("Invalid name", 400)
            if not name:
                return ('Missing name', 400)
            try:
                if check_format(image) == False:
                    image = "/static/image.svg"
            except TimeoutError:
                return redirect("/list")
            if len(name) > 60:
                return ('Product name is too long', 400)
            if len(brand) > 25:
                return ('Brand name is too long', 400)
            if db.execute("SELECT * FROM favorites WHERE name = ? AND image = ? AND brand = ? AND user_id = ?", name, image, brand, session['user_id']):
                return redirect("/list")
            name = escape(name)
            brand = escape(brand)
            image = escape(image)
            db.execute("INSERT INTO favorites (name, brand, image, user_id, date) VALUES (?, ?, ?, ?, ?)",
                       name, brand, image, session['user_id'], datetime.now())
            return ("Item successfully added", 200)


@app.route('/favorite', methods=['POST'])
@login_required
def favorite():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        name = request.form.get('name')
        brand = request.form.get('brand')
        image = request.form.get('image')
        if not image:
            image = "/static/image.svg"
        if name.isspace():
            return ("Invalid name", 400)
        if not name:
            return ('Missing name', 400)
        try:
            check_format(image)
        except TimeoutError:
            return redirect("/list")
        except Exception as e:
            image = "/static/image.svg"
        if len(name) > 60:
            return ('Product name is too long', 400)
        if len(brand) > 25:
            return ('Brand name is too long', 400)
        if db.execute("SELECT * FROM favorites WHERE name = ? AND image = ? AND brand = ? AND user_id = ?", name, image, brand, session['user_id']):
            return redirect("/list")
        name = escape(name)
        brand = escape(brand)
        image = escape(image)
        db.execute("INSERT INTO favorites (name, brand, image, user_id, date) VALUES (?, ?, ?, ?, ?)",
                   name, brand, image, session['user_id'], datetime.now())
        return ("Items successfully added", 200)


@app.route('/edit', methods=['POST'])
@login_required
def edit():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session['user_id'], session['list']):
            session.pop('list')
            return ('Unauthorized action', 400)
        action = request.form.get("action")
        name = request.form.get('name')
        brand = request.form.get('brand')
        image = request.form.get('image')
        priority = request.form.get('priority')
        product = request.form.get('product')

        if action == "product":
            if not db.execute("SELECT * FROM items WHERE code = ? AND id = ?", session['list'], product):
                return ('Unauthorized action', 400)
            if not image:
                image = "/static/image.svg"
            if name.isspace():
                return ("Invalid name", 400)
            if not name:
                return ('Missing name', 400)
            try:
                if check_format(image) == False:
                    image = "/static/image.svg"
            except TimeoutError:
                return redirect("/list")
            if not priority:
                priority = 1
            if int(priority) > 2 or int(priority) < 0:
                return ('Invalide priority level', 400)
            if len(name) > 60:
                return ('Product name is too long', 400)
            if len(brand) > 25:
                return ('Brand name is too long', 400)
            if db.execute("SELECT * FROM items WHERE name = ? AND brand = ? AND image = ? AND code = ? AND priority = ?", name, brand, image, session['list'], priority):
                return redirect('/list')
            name = escape(name)
            brand = escape(brand)
            image = escape(image)
            db.execute("UPDATE items SET name = ?, brand = ?, image = ?, priority = ?, date = ? WHERE id = ?",
                       name, brand, image, priority, datetime.now(), product)
            return ("Item successfully updated", 200)

        if action == "favorite":
            if not db.execute("SELECT * FROM favorites WHERE user_id = ? AND id = ?", session['user_id'], product):
                return ('Unauthorized action', 400)
            if not image:
                image = "/static/image.svg"
            if name.isspace():
                return ("Invalid name", 400)
            if not name:
                return ('Missing name', 400)
            try:
                if check_format(image) == False:
                    image = "/static/image.svg"
            except TimeoutError:
                return redirect("/list")
            if len(name) > 60:
                return ('Product name is too long', 400)
            if len(brand) > 25:
                return ('Brand name is too long', 400)
            if db.execute("SELECT * FROM favorites WHERE name = ? AND brand = ? AND image = ? AND user_id = ?", name, brand, image, session['user_id']):
                return redirect('/list')
            name = escape(name)
            brand = escape(brand)
            image = escape(image)
            db.execute("UPDATE favorites SET name = ?, brand = ?, image = ?, date = ? WHERE id = ?",
                       name, brand, image, datetime.now(), product)
            return ("Item successfully updated", 200)


@app.route('/delete', methods=['POST'])
@login_required
def delete():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session['user_id'], session['list']):
            session.pop('list')
            return ('Unauthorized action', 400)
        action = request.form.get("action")
        product = request.form.get('product')

        if action == "history":
            if not db.execute("SELECT * FROM history WHERE code = ? AND id = ?", session['list'], product):
                return ('Unauthorized action', 400)
            db.execute("DELETE FROM history WHERE id = ?", product)
            return ("Item successfully deleted", 200)

        if action == "favorite":
            if not db.execute("SELECT * FROM favorites WHERE user_id = ? AND id = ?", session['user_id'], product):
                return ('Unauthorized action', 400)
            db.execute("DELETE FROM favorites WHERE id = ?", product)
            return ("Item successfully deleted", 200)


@app.route('/kick', methods=['POST'])
@login_required
def kick():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        user = request.form.get('user')
        if db.execute("SELECT founder_id FROM lists WHERE code = ?", session['list'])[0]['founder_id'] != session['user_id']:
            return ('Unauthorized action', 400)
        if not db.execute("SELECT participant_id FROM participants WHERE list_id = (SELECT id FROM lists WHERE code = ?) AND participant_id = ?", session['list'], user):
            return ('User is not participating in this list', 400)
        if int(db.execute("SELECT founder_id FROM lists WHERE code = ?", session['list'])[0]['founder_id']) == int(user):
            return ('Founder is not kickable', 400)

        db.execute("DELETE FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)",
                   user, session['list'])
        return ('User successfully kicked', 200)


@app.route('/complete', methods=['POST'])
@login_required
def complete():
    if request.method == "POST":
        if 'list' not in session:
            return ('List not initialized', 400)
        if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session['user_id'], session['list']):
            session.pop('list')
            return ('Unauthorized action', 400)
        product = request.form.get('product')
        if not db.execute("SELECT * FROM items WHERE code = ? AND id = ?", session['list'], product):
            return ('Unauthorized action', 400)
        item = db.execute("SELECT name, brand, image, priority, code FROM items WHERE id = ?", product)
        if db.execute("SELECT * FROM history WHERE name = ? AND image = ? AND brand = ? AND code = ?", item[0]['name'], item[0]['image'], item[0]['brand'], session['list']):
            history_id = db.execute("SELECT id FROM history WHERE name = ? AND image = ? AND brand = ? AND code = ?",
                                    item[0]['name'], item[0]['image'], item[0]['brand'], session['list'])
            db.execute("UPDATE history SET date = ? WHERE id = ?", datetime.now(), history_id[0]['id'])
            db.execute("DELETE FROM items WHERE id = ?", product)
            return ("Status succesfully set to 'complete'", 200)

        db.execute("INSERT INTO history (name, brand, image, priority, code, user_id, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   item[0]['name'], item[0]['brand'], item[0]['image'], item[0]['priority'], item[0]['code'], session['user_id'], datetime.now())
        db.execute("DELETE FROM items WHERE id = ?", product)
        return ("Status succesfully set to 'complete'", 200)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def get_search():
    if request.method == "POST":
        searched = request.form.get("search")
        searched = searched.replace("/", "")
        searched = searched.replace("\\", "")
        if not searched or searched.isspace():
            return redirect("/list")
        if searched:
            return redirect("/search/" + searched)

    if request.method == "GET":
        if 'list' not in session:
            return redirect("/lists")
        return render_template("search.html")


@app.route('/lists', methods=['GET', 'POST'])
@login_required
def my_lists():
    if request.method == "POST":
        action = request.form.get("action")
        number_lists = db.execute("SELECT founder_id FROM lists WHERE founder_id = ?", session["user_id"])
        code = session.get('code')
        name = request.form.get("name")
        new_name = request.form.get("new-name")
        new_number = request.form.get("new-number")
        generate = request.form.get("generate")
        edit_list = request.form.get("list")
        number = request.form.get("number")
        join = request.form.get("code")
        delete = request.form.get("delete")
        leave = request.form.get("list-quit")
        enter = request.form.get("enter")

        if enter:
            if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session["user_id"], enter):
                return redirect("/lists")
            session["list"] = enter
            return redirect("/list")

        if action == "create":
            for char in number:
                if not char.isdigit():
                    return redirect("/lists")
            if len(name) > 35 or not name:
                return redirect("/lists")
            if not number:
                return redirect("/lists")
            if int(number) > 100 or int(number) < 1:
                return redirect("/lists")
            if len(number_lists) >= 30:
                return redirect("/lists")
            name = escape(name)
            if not db.execute("SELECT code FROM lists WHERE code = ?", code):
                db.execute("INSERT INTO lists (founder_id, creation_date, last_change_date, name, code, capacity) VALUES (?, ?, ?, ?, ?, ?)",
                           session["user_id"], datetime.now(), datetime.now(), name, code, number)
                list_id_create = db.execute("SELECT id FROM lists WHERE code = ?", code)
                db.execute("INSERT INTO participants (participant_id, list_id) VALUES (?, ?)",
                           session["user_id"], list_id_create[0]['id'])
                return redirect("/lists")

        if action == "join":
            for char in join:
                if not char.isalpha() and not char.isdigit():
                    return redirect("/lists")
            list_id_join = db.execute("SELECT id FROM lists WHERE code = ?", join.upper())
            if not list_id_join:
                return redirect("/lists")
            if int(db.execute("SELECT DISTINCT COUNT(*) AS length FROM participants WHERE list_id = ?", list_id_join[0]['id'])[0]['length']) >= int(db.execute("SELECT capacity FROM lists WHERE code = ?", join.upper())[0]['capacity']):
                return redirect("/lists")
            if not db.execute("SELECT code FROM lists WHERE code = ?", join.upper()):
                return redirect("/lists")
            if not db.execute("SELECT * FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session["user_id"], join.upper()):
                db.execute("INSERT INTO participants (participant_id, list_id) VALUES (?, ?)",
                           session["user_id"], list_id_join[0]['id'])
                return redirect("/lists")
            else:
                return redirect("/lists")

        if action == "edit":
            if (db.execute("SELECT founder_id FROM lists WHERE code = ?", edit_list))[0]['founder_id'] != session["user_id"]:
                return redirect("/lists")
            if len(new_name) > 35 or not new_name:
                return redirect("/lists")
            if not new_number:
                return redirect("/lists")
            if int(new_number) > 100 or int(new_number) < 1:
                return redirect("/lists")
            if int(new_number) < int(db.execute("SELECT DISTINCT COUNT(*) AS length FROM participants WHERE list_id = (SELECT id FROM lists WHERE code = ?)", edit_list)[0]['length']):
                return redirect("/lists")
            new_name = escape(new_name)
            db.execute("UPDATE lists SET name = ? WHERE code = ?", new_name, edit_list)
            db.execute("UPDATE lists SET capacity = ? WHERE code = ?", new_number, edit_list)
            db.execute("UPDATE lists SET last_change_date = ? WHERE code = ?", datetime.now(), edit_list)
            if generate == "true":
                new_code = generate_code()
                db.execute("UPDATE lists SET code = ? WHERE code = ?", new_code, edit_list)
                db.execute("UPDATE items SET code = ? WHERE code = ?", new_code, edit_list)
            return redirect("/lists")

        if action == "delete":
            if not delete:
                return redirect("/lists")
            if (db.execute("SELECT founder_id FROM lists WHERE code = ?", delete))[0]['founder_id'] != session["user_id"]:
                return redirect("/lists")
            if delete:
                db.execute("DELETE FROM items WHERE code = ?", delete)
                db.execute("DELETE FROM participants WHERE list_id = (SELECT id FROM lists WHERE code = ?)", delete)
                db.execute("DELETE FROM lists WHERE code = ?", delete)
                return redirect("/lists")
            return redirect("/lists")

        if action == "quit":
            if not leave:
                return redirect("/lists")
            if (db.execute("SELECT founder_id FROM lists WHERE code = ?", leave))[0]['founder_id'] == session["user_id"]:
                return redirect("/lists")
            if leave:
                db.execute(
                    "DELETE FROM participants WHERE participant_id = ? AND list_id = (SELECT id FROM lists WHERE code = ?)", session['user_id'], leave)
                return redirect("/lists")
            return redirect("/lists")

    if request.method == "GET":
        if 'list' in session:
            session.pop('list')
        founders = []
        users = []
        items = []
        lists = db.execute(
            "SELECT * FROM lists WHERE id in (SELECT DISTINCT list_id FROM participants WHERE participant_id = ?)", session["user_id"])
        for row in lists:
            users_number = db.execute("SELECT DISTINCT COUNT(*) AS length FROM participants WHERE list_id = ?", row['id'])
            users.append(users_number[0]['length'])
        for founder_id in lists:
            founder = db.execute("SELECT username FROM users WHERE id = ?", founder_id['founder_id'])
            item = db.execute("SELECT COUNT(*) as items FROM items WHERE code = ?", founder_id['code'])
            items.append(item[0]['items'])
            founders.append(founder)
        if 'code' in session:
            session.pop('code')
        code = generate_code()
        session['code'] = code
        return render_template("lists.html", code=code, lists=lists, founders=founders, users=users, user_id=session["user_id"], items=items)


@app.route('/list', methods=['GET'])
@login_required
def my_list():
    if request.method == "GET":
        if 'list' in session and db.execute("SELECT code FROM lists WHERE code = ?", session['list']):
            days = []
            history_days = []
            name = db.execute("SELECT name FROM lists WHERE code = ?", session['list'])
            items = db.execute("SELECT * FROM items WHERE code = ?", session['list'])
            history = db.execute("SELECT * FROM history WHERE code = ?", session['list'])
            favorites = db.execute("SELECT * FROM favorites WHERE user_id = ?", session['user_id'])
            favorites_count = db.execute("SELECT COUNT(*) as items FROM favorites WHERE user_id = ?", session['user_id'])
            items_count = db.execute("SELECT COUNT(*) as items FROM items WHERE code = ?", session['list'])
            history_count = db.execute("SELECT COUNT(*) as items FROM history WHERE code = ?", session['list'])
            users = db.execute(
                "SELECT username, id FROM users WHERE id IN (SELECT participant_id FROM participants WHERE list_id = (SELECT id FROM lists WHERE code = ?))", session['list'])
            founder = db.execute("SELECT id FROM users WHERE id = (SELECT founder_id FROM lists WHERE code = ?)", session['list'])
            you = db.execute("SELECT id FROM users WHERE id = ?", session['user_id'])
            users_counter = db.execute(
                "SELECT count(*) AS users FROM users WHERE id IN (SELECT participant_id FROM participants WHERE list_id = (SELECT id FROM lists WHERE code = ?))", session['list'])
            for item in items:
                item_date_raw = item['date']
                item_date = datetime.strptime(item_date_raw, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                difference = today - item_date
                days.append(difference.days)
                if item['brand'] == " ":
                    item['brand'] = "§none§"
            for item in history:
                item['user_id'] = db.execute("SELECT username FROM users WHERE id = ?", item['user_id'])
                item_date_raw = item['date']
                item_date = datetime.strptime(item_date_raw, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                difference = today - item_date
                history_days.append(difference.days)
                if item['brand'] == " ":
                    item['brand'] = "§none§"
            return render_template("list.html", items=items, items_count=items_count, days=days, history_days=history_days, name=name, history_count=history_count, history=history, favorites=favorites, favorites_count=favorites_count, users=users, founder=founder, you=you, users_counter=users_counter)
        else:
            return redirect("/lists")


@app.route('/reloaditems', methods=['GET'])
@login_required
def reload_list():
    if request.method == "GET":
        if 'list' in session and db.execute("SELECT code FROM lists WHERE code = ?", session['list']):
            days = []
            history_days = []
            history_count = db.execute("SELECT COUNT(*) as items FROM history WHERE code = ?", session['list'])
            name = db.execute("SELECT name FROM lists WHERE code = ?", session['list'])
            items = db.execute("SELECT * FROM items WHERE code = ?", session['list'])
            history = db.execute("SELECT * FROM history WHERE code = ?", session['list'])
            items_count = db.execute("SELECT COUNT(*) as items FROM items WHERE code = ?", session['list'])
            favorites = db.execute("SELECT * FROM favorites WHERE user_id = ?", session['user_id'])
            favorites_count = db.execute("SELECT COUNT(*) as items FROM favorites WHERE user_id = ?", session['user_id'])
            for item in items:
                item_date_raw = item['date']
                item_date = datetime.strptime(item_date_raw, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                difference = today - item_date
                days.append(difference.days)
                if item['brand'] == " ":
                    item['brand'] = "§none§"
            for item in history:
                item['user_id'] = db.execute("SELECT username FROM users WHERE id = ?", item['user_id'])
                item_date_raw = item['date']
                item_date = datetime.strptime(item_date_raw, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                difference = today - item_date
                history_days.append(difference.days)
                if item['brand'] == " ":
                    item['brand'] = "§none§"
            return render_template("items.html", items=items, items_count=items_count, days=days, name=name, history_days=history_days, history_count=history_count, history=history, favorites=favorites, favorites_count=favorites_count)
        else:
            return ("Reload error", 400)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("loginerror.html", message="Must provide username")

        elif not request.form.get("password"):
            return render_template("loginerror.html", message="Must provide password")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("loginerror.html", message="Invalid username and/or password")

        session["user_id"] = rows[0]["id"]

        return redirect("/lists")

    else:
        return render_template("login.html")


@app.route("/")
@login_required
def index():
    if request.method == "GET":
        return redirect("/lists")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        if len(username) < 5 or len(username) > 20:
            return render_template("regerror.html", message="Username length is invalid")
        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return render_template("regerror.html", message="Username already exists")
        password = request.form.get("password")
        if len(password) < 8:
            return render_template("regerror.html", message="Password length is invalid")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return render_template("regerror.html", message="Passwords do not match")
        if not username or not password or not confirmation:
            return render_template("regerror.html", message="Username/password is blank")
        cripted = generate_password_hash(password, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, cripted)
        return redirect("/lists")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
