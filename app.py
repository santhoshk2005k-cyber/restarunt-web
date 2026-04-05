from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# ── MySQL Configuration ─────────────────────────────────────────────────────
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'San@0725'
app.config['MYSQL_DB']       = 'saffron_smoke'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_CHARSET']  = 'utf8mb4'
app.config['MYSQL_CONNECT_ARGS'] = {'charset': 'utf8mb4'}

mysql = MySQL(app)

# ── Helper ──────────────────────────────────────────────────────────────────
def db():
    return mysql.connection.cursor()

def commit():
    mysql.connection.commit()

# ════════════════════════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ════════════════════════════════════════════════════════════════════════════
#  MENU API
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/menu', methods=['GET'])
def get_menu():
    cur = db()
    cur.execute("SELECT * FROM menu_items ORDER BY cuisine, name")
    items = cur.fetchall()
    return jsonify(items)

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    cur = db()
    cur.execute(
        """INSERT INTO menu_items (name, chef, cuisine, price, description, emoji, available)
           VALUES (%s, %s, %s, %s, %s, %s, 1)""",
        (data['name'], data['chef'], data['cuisine'],
         data['price'], data.get('desc', ''), data.get('emoji', '🍽️'))
    )
    commit()
    return jsonify({'success': True, 'id': cur.lastrowid})

@app.route('/api/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    cur = db()
    fields, vals = [], []
    if 'price' in data:
        fields.append('price=%s'); vals.append(data['price'])
    if 'available' in data:
        fields.append('available=%s'); vals.append(int(data['available']))
    if 'name' in data:
        fields.append('name=%s'); vals.append(data['name'])
    if not fields:
        return jsonify({'success': False, 'error': 'Nothing to update'}), 400
    vals.append(item_id)
    cur.execute(f"UPDATE menu_items SET {', '.join(fields)} WHERE id=%s", vals)
    commit()
    return jsonify({'success': True})

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    cur = db()
    cur.execute("DELETE FROM menu_items WHERE id=%s", (item_id,))
    commit()
    return jsonify({'success': True})

# ════════════════════════════════════════════════════════════════════════════
#  RESERVATIONS API
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/reservations/booked-tables', methods=['GET'])
def booked_tables():
    """Return list of table numbers that are already booked (non-cancelled)."""
    cur = db()
    cur.execute(
        "SELECT table_number FROM reservations WHERE status != 'Cancelled'"
    )
    rows = cur.fetchall()
    return jsonify([r['table_number'] for r in rows])

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    cur = db()
    cur.execute("SELECT * FROM reservations ORDER BY created_at DESC")
    rows = cur.fetchall()
    # convert date objects to strings
    for r in rows:
        if r.get('res_date'):
            r['res_date'] = str(r['res_date'])
        if r.get('created_at'):
            r['created_at'] = str(r['created_at'])
    return jsonify(rows)

@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    data = request.json
    # Check table not already booked
    cur = db()
    cur.execute(
        "SELECT id FROM reservations WHERE table_number=%s AND status != 'Cancelled'",
        (data['table'],)
    )
    if cur.fetchone():
        return jsonify({'success': False, 'error': 'This table is already booked. Please choose another table.'}), 409

    cur.execute(
        """INSERT INTO reservations
           (first_name, last_name, phone, res_date, res_time, guests, table_number, note, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed')""",
        (data['firstName'], data['lastName'], data['phone'],
         data['date'], data['time'], data['guests'],
         data['table'], data.get('note', ''))
    )
    commit()
    return jsonify({'success': True, 'id': cur.lastrowid})

@app.route('/api/reservations/<int:res_id>', methods=['PUT'])
def update_reservation(res_id):
    data = request.json
    cur = db()
    cur.execute(
        "UPDATE reservations SET status=%s WHERE id=%s",
        (data['status'], res_id)
    )
    commit()
    return jsonify({'success': True})

# ════════════════════════════════════════════════════════════════════════════
#  ORDERS API
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/orders', methods=['GET'])
def get_orders():
    cur = db()
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cur.fetchall()
    for o in orders:
        if o.get('created_at'):
            o['created_at'] = str(o['created_at'])
        o['total'] = float(o['total'])
        # fetch items
        cur.execute("SELECT * FROM order_items WHERE order_id=%s", (o['id'],))
        items = cur.fetchall()
        for i in items:
            i['price'] = float(i['price'])
        o['items'] = items
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.json          # { items: [{id,name,chef,cuisine,emoji,price,qty}], total }
    cur = db()
    cur.execute(
        "INSERT INTO orders (total, status) VALUES (%s, 'Pending')",
        (data['total'],)
    )
    order_id = cur.lastrowid
    for item in data['items']:
        cur.execute(
            """INSERT INTO order_items (order_id, item_name, chef, cuisine, emoji, price, quantity)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (order_id, item['name'], item.get('chef', ''),
             item.get('cuisine', ''), item.get('emoji', ''),
             item['price'], item['qty'])
        )
    commit()
    return jsonify({'success': True, 'id': order_id})

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    cur = db()
    cur.execute(
        "UPDATE orders SET status=%s WHERE id=%s",
        (data['status'], order_id)
    )
    commit()
    return jsonify({'success': True})

# ════════════════════════════════════════════════════════════════════════════
#  DASHBOARD STATS API
# ════════════════════════════════════════════════════════════════════════════

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    cur = db()

    # Revenue & completed orders (Done only, excludes Cancelled)
    cur.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as rev FROM orders WHERE status='Done'")
    row = cur.fetchone()
    completed = int(row['cnt'])
    revenue   = float(row['rev'])

    # Active reservations
    cur.execute("SELECT COUNT(*) as cnt FROM reservations WHERE status != 'Cancelled'")
    active_res = int(cur.fetchone()['cnt'])

    # Menu counts
    cur.execute("SELECT COUNT(*) as total, SUM(available) as active FROM menu_items")
    m = cur.fetchone()
    total_menu  = int(m['total']  or 0)
    active_menu = int(m['active'] or 0)

    # Revenue last 7 days (completed only)
    cur.execute("""
        SELECT DATE(created_at) as day, SUM(total) as rev
        FROM orders
        WHERE status='Done' AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    rev_by_day = {str(r['day']): float(r['rev']) for r in cur.fetchall()}

    # Cuisine breakdown (completed orders only)
    cur.execute("""
        SELECT oi.cuisine, SUM(oi.quantity) as qty
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status='Done'
        GROUP BY oi.cuisine
    """)
    cuisine_data = {r['cuisine']: int(r['qty']) for r in cur.fetchall()}

    # Item sales (completed only)
    cur.execute("""
        SELECT oi.item_name as name, oi.chef, oi.emoji,
               SUM(oi.quantity) as qty,
               SUM(oi.quantity * oi.price) as revenue,
               oi.cuisine
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status='Done'
        GROUP BY oi.item_name, oi.chef, oi.emoji, oi.cuisine
        ORDER BY revenue DESC
        LIMIT 20
    """)
    item_sales = cur.fetchall()
    for i in item_sales:
        i['qty']     = int(i['qty'])
        i['revenue'] = float(i['revenue'])

    return jsonify({
        'revenue':      revenue,
        'completed':    completed,
        'active_res':   active_res,
        'total_menu':   total_menu,
        'active_menu':  active_menu,
        'rev_by_day':   rev_by_day,
        'cuisine_data': cuisine_data,
        'item_sales':   item_sales,
    })

# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, port=5000)
