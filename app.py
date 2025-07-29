from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import session, flash
from flask import request
from math import ceil
import os

app = Flask(__name__)
app.secret_key = "Shaik123@"
# Setup database (SQLite file)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(200))
    visible = db.Column(db.Boolean, default=True)  # ← NEW COLUMN

def calculate_prices_and_conditions(phone):
    condition_mapping = {
        "Like New": {
            "X": "New", "Y": "3 Stars", "Z": "New"
        },
        "Good": {
            "X": "Good", "Y": "2 Stars", "Z": "Good"
        },
        "Fair": {
            "X": "Scrap", "Y": "1 Star", "Z": "As New"
        }
    }

    prices = {}
    conditions = {}

    # Calculate and check profitability (assume minimum profit ₹5 for all)
    min_profit = 5

    cost = phone.cost_price

    # Platform X
    x_price = round(cost / (1 - 0.10), 2)
    if x_price - cost >= min_profit:
        prices["X"] = x_price
        conditions["X"] = condition_mapping.get(phone.condition, {}).get("X", "N/A")

    # Platform Y
    y_price = round((cost + 2) / (1 - 0.08), 2)
    if y_price - (cost + 2) >= min_profit:
        prices["Y"] = y_price
        conditions["Y"] = condition_mapping.get(phone.condition, {}).get("Y", "N/A")

    # Platform Z
    z_price = round(cost / (1 - 0.12), 2)
    if z_price - cost >= min_profit:
        prices["Z"] = z_price
        conditions["Z"] = condition_mapping.get(phone.condition, {}).get("Z", "N/A")

    return prices, conditions


# Homepage
@app.route('/')
def home():
    phones = Phone.query.all()
    platform_data = {"X": [], "Y": [], "Z": []}

    for phone in phones:
        if phone.stock > 0:
            prices, conditions = calculate_prices_and_conditions(phone)
            for platform in prices:
                platform_data[platform].append({
                    "id": phone.id,  # ← important
                    "name": phone.name,
                    "condition": phone.condition,
                    "image_filename": phone.image_filename,
                    "platform_prices": prices,
                    "platform_conditions": conditions
                })

    return render_template('home.html', platform_data=platform_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# Show inventory
@app.route('/inventory')
def inventory():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Get query params
    search = request.args.get('search', '').lower()
    condition_filter = request.args.get('condition', '')
    sort_by = request.args.get('sort', '')
    page = int(request.args.get('page', 1))
    per_page = 6

    phones = Phone.query.all()
    listed_phones = []
    unlisted_phones = []

    for phone in phones:
        prices, conditions = calculate_prices_and_conditions(phone)

        # Search and filter
        if search and search not in phone.name.lower():
            continue
        if condition_filter and phone.condition != condition_filter:
            continue

        # Get all images
        image_folder = os.path.join(app.config['UPLOAD_FOLDER'], phone.name)
        images = []
        if os.path.exists(image_folder):
            for file in os.listdir(image_folder):
                if file.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                    images.append(f"{phone.name}/{file}")

        phone_data = {
            "id": phone.id,
            "name": phone.name,
            "images": images,
            "condition": phone.condition,
            "stock": phone.stock,
            "cost_price": phone.cost_price,
            "platform_prices": prices,
            "platform_conditions": conditions
        }

        if phone.stock <= 0 or not prices:
            unlisted_phones.append({
                "id": phone.id,
                "name": phone.name,
                "condition": phone.condition,
                "stock": phone.stock,
                "image_filename": phone.image_filename,
                "images": images
            })
        else:
            listed_phones.append(phone_data)

    # Sort
    if sort_by == "name_asc":
        listed_phones.sort(key=lambda x: x['name'])
    elif sort_by == "name_desc":
        listed_phones.sort(key=lambda x: x['name'], reverse=True)
    elif sort_by == "stock_asc":
        listed_phones.sort(key=lambda x: x['stock'])
    elif sort_by == "stock_desc":
        listed_phones.sort(key=lambda x: x['stock'], reverse=True)
    elif sort_by == "price_asc":
        listed_phones.sort(key=lambda x: x['cost_price'])
    elif sort_by == "price_desc":
        listed_phones.sort(key=lambda x: x['cost_price'], reverse=True)

    # Pagination
    total_pages = ceil(len(listed_phones) / per_page)
    paginated_phones = listed_phones[(page - 1) * per_page: page * per_page]

    return render_template(
        'inventory.html',
        phones=paginated_phones,
        unlisted_phones=unlisted_phones,
        search_query=search,
        selected_condition=condition_filter,
        selected_sort=sort_by,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        cost_price = float(request.form['cost_price'])
        condition = request.form['condition']
        stock = int(request.form['stock'])

        # Create folder for phone images
        phone_folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
        os.makedirs(phone_folder, exist_ok=True)

        image_files = request.files.getlist('images')
        saved_images = []

        for i, image in enumerate(image_files):
            if image and image.filename != '':
                filename = f"{i+1}.jpg"
                full_path = os.path.join(phone_folder, filename)
                image.save(full_path)
                if i == 0:  # First image used as cover
                    cover_image = os.path.join(name, filename).replace("\\", "/")

        new_phone = Phone(
            name=name,
            cost_price=cost_price,
            condition=condition,
            stock=stock,
            image_filename=cover_image  # Cover image for display
        )

        db.session.add(new_phone)
        db.session.commit()

        return redirect(url_for('admin'))

        # Load all existing phones for the bottom inventory display
    phones = Phone.query.all()

    phone_cards = []
    for phone in phones:
        folder = os.path.join(app.config['UPLOAD_FOLDER'], phone.name)
        images = []
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    images.append(f"{phone.name}/{file}".replace("\\", "/"))
        phone_cards.append({
            'id': phone.id,
            'name': phone.name,
            'cost_price': phone.cost_price,
            'condition': phone.condition,
            'stock': phone.stock,
            'images': images
        })

    return render_template('admin.html', phones=phone_cards)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

phone_specs = {
    "Iphone 13": {
        "highlights": [
            "A15 Bionic chip for blazing fast performance",
            "Super Retina XDR Display – 6.1-inch OLED",
            "Dual 12MP camera system with Night mode",
            "Up to 19 hours video playback",
            "IP68 water resistance"
        ],
        "marketing_text": "Experience the future of smartphones with iPhone 13 — unmatched speed, camera, and style."
    },
    "Samsung Galaxy S21": {
        "highlights": [
            "Snapdragon 888 processor",
            "Dynamic AMOLED 2X – 120Hz refresh rate",
            "64MP triple rear camera with 30x Space Zoom",
            "8K video recording support",
            "4000mAh intelligent battery"
        ],
        "marketing_text": "Galaxy S21 redefines productivity and creativity in one sleek powerhouse."
    },
    "Google Pixel 9A": {
        "highlights": [
            "Google Tensor G2 chip",
            "Magic Eraser and Night Sight Camera",
            "Pure Android experience with 5 years of updates",
            "Titan M2 Security Chip",
            "Adaptive Battery – 24+ hours"
        ],
        "marketing_text": "Capture magical moments effortlessly with Pixel 9A – smart, secure, and smooth."
    },
    "OnePlus Nord CE 3 Lite": {
        "highlights": [
            "Snapdragon 695 5G",
            "108MP AI Camera",
            "5000mAh battery with 67W SUPERVOOC",
            "120Hz LCD display",
            "Expandable storage up to 1TB"
        ],
        "marketing_text": "Power-packed and affordable — Nord CE 3 Lite is built to perform every day."
    },
    "Redmi Note 12 Pro": {
        "highlights": [
            "MediaTek Dimensity 1080",
            "50MP Sony IMX766 sensor with OIS",
            "120Hz AMOLED Display",
            "67W Turbo Charge",
            "Dolby Atmos dual speakers"
        ],
        "marketing_text": "Shoot stunning photos and enjoy seamless gaming with the Note 12 Pro."
    },
    "Realme Narzo 60": {
        "highlights": [
            "Dimensity 6020 5G processor",
            "64MP Nightscape Camera",
            "Super AMOLED 90Hz display",
            "Stylish leather design",
            "5000mAh battery"
        ],
        "marketing_text": "The Narzo 60 is bold in design and built for non-stop action."
    },
    "iPhone SE (3rd Gen)": {
        "highlights": [
            "A15 Bionic chip – same as iPhone 13",
            "Compact 4.7-inch Retina display",
            "5G capable",
            "Home button with Touch ID",
            "Water and dust resistant"
        ],
        "marketing_text": "Small in size. Big on power. Perfect for iOS lovers who want speed and simplicity."
    },
    "Samsung Galaxy A53": {
        "highlights": [
            "Exynos 1280 chipset",
            "64MP Quad Camera",
            "120Hz Super AMOLED Display",
            "Stereo speakers with Dolby Atmos",
            "5000mAh battery + 25W fast charge"
        ],
        "marketing_text": "Work, play, and create with the elegant Galaxy A53 – made for multitaskers."
    },
    "Vivo V27 Pro": {
        "highlights": [
            "MediaTek Dimensity 8200",
            "50MP Sony IMX766V Camera",
            "Color Changing Fluorite AG Glass",
            "120Hz 3D curved AMOLED",
            "66W FlashCharge"
        ],
        "marketing_text": "Vivo V27 Pro brings studio-level portraits and dazzling design to your hands."
    },
    "Motorola Edge 40": {
        "highlights": [
            "MediaTek Dimensity 8020",
            "144Hz POLED display",
            "IP68 rated for dust and water",
            "68W TurboPower fast charge",
            "32MP selfie with AI beauty"
        ],
        "marketing_text": "Sleek, secure, and superfast — the Edge 40 is your all-in-one performance buddy."
    },
    "Nothing Phone (1)": {
        "highlights": [
            "Glyph Interface LED design",
            "Qualcomm Snapdragon 778G+",
            "50MP dual camera with OIS",
            "120Hz OLED display",
            "Nothing OS based on Android"
        ],
        "marketing_text": "Nothing Phone (1) is refreshingly unique — a bold take on smartphone design."
    },
    "Infinix Zero 5G 2023": {
        "highlights": [
            "Dimensity 920 5G chipset",
            "120Hz display",
            "50MP AI camera",
            "5000mAh battery",
            "18W fast charging"
        ],
        "marketing_text": "Zero compromise on speed or performance — Infinix Zero 5G delivers smart multitasking."
    },
    "Lava Blaze 5G": {
        "highlights": [
            "MediaTek Dimensity 6020",
            "Glass back design",
            "128GB UFS 2.2 storage",
            "50MP dual camera",
            "Widevine L1 certified"
        ],
        "marketing_text": "India’s budget 5G phone with stunning looks and rock-solid features."
    },
    "POCO X5 Pro": {
        "highlights": [
            "Snapdragon 778G processor",
            "Turbo 67W fast charging",
            "120Hz AMOLED screen",
            "Dolby Vision + Atmos",
            "7.9mm slim design"
        ],
        "marketing_text": "POCO X5 Pro is performance-oriented and tuned for power gamers and creators."
    },
    "iQOO Neo 7": {
        "highlights": [
            "MediaTek Dimensity 8200",
            "120Hz AMOLED display",
            "5000mAh battery + 120W FlashCharge",
            "Motion control gaming",
            "Ultra Game Mode"
        ],
        "marketing_text": "Engineered for gaming. Built for power. iQOO Neo 7 pushes limits effortlessly."
    }
}

@app.route('/phone/<int:phone_id>')
def phone_detail(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    prices, conditions = calculate_prices_and_conditions(phone)

    # Load image paths
    image_folder = os.path.join(app.config['UPLOAD_FOLDER'], phone.name)
    images = []
    if os.path.exists(image_folder):
        for file in sorted(os.listdir(image_folder)):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                images.append(f"{phone.name}/{file}")

    # Get spec content or fallback
    spec = phone_specs.get(phone.name, {
        "highlights": ["No details available for this model."],
        "marketing_text": "Specifications will be updated soon."
    })

    return render_template("phone_detail.html", phone={
        "id": phone.id,
        "name": phone.name,
        "condition": phone.condition,
        "stock": phone.stock,
        "platform_prices": prices,
        "platform_conditions": conditions,
        "images": images,
        "highlights": spec["highlights"],
        "marketing_text": spec["marketing_text"]
    })

@app.route('/edit/<int:phone_id>', methods=['GET', 'POST'])
def edit_phone(phone_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    phone = Phone.query.get_or_404(phone_id)

    if request.method == 'POST':
        phone.name = request.form['name']
        phone.cost_price = float(request.form['cost_price'])
        phone.condition = request.form['condition']
        phone.stock = int(request.form['stock'])

        # Handle new image uploads
        image_files = request.files.getlist('images')
        if image_files and image_files[0].filename != '':
            # Clear old images
            phone_folder = os.path.join(app.config['UPLOAD_FOLDER'], phone.name)
            if os.path.exists(phone_folder):
                for old_file in os.listdir(phone_folder):
                    os.remove(os.path.join(phone_folder, old_file))
            else:
                os.makedirs(phone_folder)

            for i, image in enumerate(image_files):
                filename = f"{i+1}.jpg"
                image.save(os.path.join(phone_folder, filename))
                if i == 0:
                    phone.image_filename = f"{phone.name}/{filename}"

        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit.html', phone=phone)


@app.route('/delete/<int:phone_id>')
def delete_phone(phone_id):
    phone = Phone.query.get_or_404(phone_id)

    # Delete image folder
    folder = os.path.join(app.config['UPLOAD_FOLDER'], phone.name)
    if os.path.exists(folder):
        import shutil
        shutil.rmtree(folder)

    db.session.delete(phone)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/toggle_visibility/<int:phone_id>', methods=['POST'])
def toggle_visibility(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    phone.visible = not phone.visible
    db.session.commit()
    return redirect(url_for('admin'))


# This runs once: creates DB file and table
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
