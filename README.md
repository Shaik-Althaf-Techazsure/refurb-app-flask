# RefurbApp — Refurbished Phone Inventory & Sales Manager

RefurbApp is a full-stack web application designed to manage and sell refurbished phones across multiple e-commerce platforms (like Platform X, Y, Z). Built as a comprehensive academic assignment, this system simulates real-world inventory workflows — including dynamic pricing, smart stock management, image uploads, platform visibility, and a professional UI.

<img width="817" height="917" alt="Homepage" src="https://github.com/user-attachments/assets/a23c7424-c7cd-40d4-8635-e4e1ef734e01" />

##  Features

- **Admin Panel** for managing inventory (Add, Edit, Delete)
- Upload multiple phone images stored in per-phone folders
- **Smart Inventory Listing** with:
  - Condition filter
  - Search bar
  - Sorting by stock, name, and price
  - Pagination for large datasets
- **Platform-wise Price Mapping** (X, Y, Z)
- Auto-detection of low stock and optional visibility toggling
- Carousel display of products (3 visible at once)
- Clickable product cards linked to detailed view page
- Login & Logout with navbar update
- Professional & responsive UI using **Bootstrap 5**
- Marketing highlights + top features section in detail view

## Technologies Used

- Python & Flask (Backend)
- SQLite (Database)
- HTML, CSS, Bootstrap 5 (Frontend)
- Jinja2 Templating
- JavaScript (for Bootstrap components)
- <img width="1862" height="996" alt="code" src="https://github.com/user-attachments/assets/d14df10d-77a7-443f-ba1c-1930cfc3e670" />


## Project Structure
RefurbApp/
├── static/
│ └── images/
│ └── {phone_name}/ ← Image folders for each phone
├── templates/
│ ├── home.html
│ ├── inventory.html
│ ├── admin.html
│ ├── edit.html
│ ├── phone_detail.html
│ └── login.html
├── app.py
├── requirements.txt
└── README.md

## 🖼Screenshots

### Home Page with Hero Section and Carousel
<img width="817" height="917" alt="Homepage" src="https://github.com/user-attachments/assets/23b6695e-8b42-4995-9d7c-a95d7a5d8a8c" />


### Inventory Page with Sorting, Filtering & Pagination
<img width="835" height="918" alt="Inventory" src="https://github.com/user-attachments/assets/731abd0a-44ea-47c0-a01a-a2ca9297086e" />

### Admin Panel for Adding Phones
<img width="845" height="923" alt="Admin" src="https://github.com/user-attachments/assets/82355d2f-1612-4abe-b1a3-92fbc45e21dd" />


### Product Detail Page with Highlights
<img width="882" height="692" alt="Product details" src="https://github.com/user-attachments/assets/7f4b6752-f97f-4915-942d-2d72634be3b2" />



## Demo Walkthrough

🎥 **[Watch Full Demo on YouTube](https://youtu.be/ZGvIyqGWTcM?si=3sccnNmMYgOHEaz4)**  
See the full explanation, features, and UI walkthrough.

---

## 🔧 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shaik-Althaf-TechAZsure/refurb-app-flask.git
   cd refurb-app-flask

2. **Create virtual environment (optional but recommended):**
   python -m venv venv
   source venv/bin/activate

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Run the app:**
   python app.py

5. **Access locally:**
   Visit http://127.0.0.1:5000 in your browser.


**Admin Credentials**
1. **Username:** admin
2. **Password:** admin123
