# Saffron & Smoke — Setup Guide

## Project Structure
```
saffron_smoke/
├── app.py              ← Flask backend (all API routes)
├── schema.sql          ← MySQL database schema
├── requirements.txt    ← Python dependencies
├── templates/
│   ├── index.html      ← Customer website
│   └── admin.html      ← Admin portal
└── README.md
```

---

## Step 1 — Create the MySQL Database

Open your terminal and run:

```bash
mysql -u root -p < schema.sql
```

This creates the `saffron_smoke` database with 4 tables:
- `menu_items`
- `reservations`
- `orders`
- `order_items`

---

## Step 2 — Edit Database Credentials

Open `app.py` and update these lines:

```python
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'       # ← your MySQL username
app.config['MYSQL_PASSWORD'] = ''           # ← your MySQL password
app.config['MYSQL_DB']       = 'saffron_smoke'
```

---

## Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you get an error on Windows, install mysqlclient manually:
```bash
pip install mysqlclient
```

Or use PyMySQL instead — change `requirements.txt` to:
```
Flask==3.0.3
Flask-MySQLdb==2.0.0
PyMySQL==1.1.1
cryptography==42.0.8
```

And add this line at the top of `app.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 4 — Run the Server

```bash
python app.py
```

Flask will start on: **http://localhost:5000**

---

## URLs

| Page | URL |
|------|-----|
| Customer Website | http://localhost:5000/ |
| Admin Portal | http://localhost:5000/admin |

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/menu | Get all menu items |
| POST | /api/menu | Add new menu item |
| PUT | /api/menu/:id | Edit price / toggle availability |
| DELETE | /api/menu/:id | Delete menu item |
| GET | /api/reservations | Get all reservations |
| POST | /api/reservations | Book a table |
| GET | /api/reservations/booked-tables | Tables already booked |
| GET | /api/orders | Get all orders |
| POST | /api/orders | Place an order |
| PUT | /api/orders/:id | Update order status |
| GET | /api/dashboard | Dashboard stats (completed only) |

---

## How Revenue Logic Works

- **Pending / Preparing** → not counted in revenue or totals
- **Done** → added to total revenue and completed orders count
- **Cancelled** → completely excluded from all stats and revenue
