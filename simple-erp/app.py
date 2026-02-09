from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATABASE = 'database/erp.db'

# Database helper functions
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database with required tables"""
    db = get_db()
    
    # Users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products/Inventory table
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            description TEXT,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            unit_price REAL NOT NULL,
            reorder_level INTEGER DEFAULT 10,
            supplier_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    ''')
    
    # Customers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Suppliers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            contact_person TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales Orders table
    db.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            notes TEXT,
            created_by INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Sales Order Items table
    db.execute('''
        CREATE TABLE IF NOT EXISTS sales_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES sales_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Purchase Orders table
    db.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            supplier_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            notes TEXT,
            created_by INTEGER,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Purchase Order Items table
    db.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Transactions table (for financial tracking)
    db.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL,
            category TEXT,
            amount REAL NOT NULL,
            description TEXT,
            reference_type TEXT,
            reference_id INTEGER,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    db.commit()
    
    # Create default admin user if not exists
    cursor = db.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        db.execute(
            "INSERT INTO users (username, password, full_name, role, email) VALUES (?, ?, ?, ?, ?)",
            ('admin', hashed_pw, 'System Administrator', 'admin', 'admin@company.com')
        )
        db.commit()
    
    db.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    
    # Get statistics
    stats = {
        'total_products': db.execute('SELECT COUNT(*) as count FROM products').fetchone()['count'],
        'low_stock': db.execute('SELECT COUNT(*) as count FROM products WHERE quantity <= reorder_level').fetchone()['count'],
        'total_customers': db.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count'],
        'pending_orders': db.execute('SELECT COUNT(*) as count FROM sales_orders WHERE status = "pending"').fetchone()['count'],
        'total_sales': db.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM sales_orders WHERE status = "completed"').fetchone()['total'],
        'recent_orders': db.execute('''
            SELECT so.*, c.name as customer_name 
            FROM sales_orders so 
            JOIN customers c ON so.customer_id = c.id 
            ORDER BY so.order_date DESC LIMIT 5
        ''').fetchall()
    }
    
    db.close()
    return render_template('dashboard.html', stats=stats)

# Product/Inventory routes
@app.route('/products')
@login_required
def products():
    db = get_db()
    products = db.execute('''
        SELECT p.*, s.name as supplier_name 
        FROM products p 
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.name
    ''').fetchall()
    db.close()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO products (name, sku, description, category, quantity, unit_price, reorder_level, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['sku'],
            request.form.get('description', ''),
            request.form.get('category', ''),
            int(request.form['quantity']),
            float(request.form['unit_price']),
            int(request.form.get('reorder_level', 10)),
            int(request.form['supplier_id']) if request.form.get('supplier_id') else None
        ))
        db.commit()
        db.close()
        return redirect(url_for('products'))
    
    db = get_db()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    db.close()
    return render_template('product_form.html', product=None, suppliers=suppliers)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE products 
            SET name=?, sku=?, description=?, category=?, quantity=?, unit_price=?, reorder_level=?, supplier_id=?, updated_at=?
            WHERE id=?
        ''', (
            request.form['name'],
            request.form['sku'],
            request.form.get('description', ''),
            request.form.get('category', ''),
            int(request.form['quantity']),
            float(request.form['unit_price']),
            int(request.form.get('reorder_level', 10)),
            int(request.form['supplier_id']) if request.form.get('supplier_id') else None,
            datetime.now(),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('products'))
    
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    db.close()
    return render_template('product_form.html', product=product, suppliers=suppliers)

@app.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('products'))

# Customer routes
@app.route('/customers')
@login_required
def customers():
    db = get_db()
    customers = db.execute('SELECT * FROM customers ORDER BY name').fetchall()
    db.close()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO customers (name, email, phone, address, company)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form.get('email', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('company', '')
        ))
        db.commit()
        db.close()
        return redirect(url_for('customers'))
    
    return render_template('customer_form.html', customer=None)

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE customers 
            SET name=?, email=?, phone=?, address=?, company=?
            WHERE id=?
        ''', (
            request.form['name'],
            request.form.get('email', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('company', ''),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('customers'))
    
    customer = db.execute('SELECT * FROM customers WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('customer_form.html', customer=customer)

# Supplier routes
@app.route('/suppliers')
@login_required
def suppliers():
    db = get_db()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    db.close()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO suppliers (name, email, phone, address, contact_person)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form.get('email', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('contact_person', '')
        ))
        db.commit()
        db.close()
        return redirect(url_for('suppliers'))
    
    return render_template('supplier_form.html', supplier=None)

@app.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE suppliers 
            SET name=?, email=?, phone=?, address=?, contact_person=?
            WHERE id=?
        ''', (
            request.form['name'],
            request.form.get('email', ''),
            request.form.get('phone', ''),
            request.form.get('address', ''),
            request.form.get('contact_person', ''),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('suppliers'))
    
    supplier = db.execute('SELECT * FROM suppliers WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('supplier_form.html', supplier=supplier)

# Sales Order routes
@app.route('/sales')
@login_required
def sales():
    db = get_db()
    orders = db.execute('''
        SELECT so.*, c.name as customer_name 
        FROM sales_orders so 
        JOIN customers c ON so.customer_id = c.id
        ORDER BY so.order_date DESC
    ''').fetchall()
    db.close()
    return render_template('sales.html', orders=orders)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        db = get_db()
        
        # Generate order number
        order_count = db.execute('SELECT COUNT(*) as count FROM sales_orders').fetchone()['count']
        order_number = f'SO-{order_count + 1:05d}'
        
        # Insert order
        cursor = db.execute('''
            INSERT INTO sales_orders (order_number, customer_id, status, notes, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            order_number,
            int(request.form['customer_id']),
            request.form.get('status', 'pending'),
            request.form.get('notes', ''),
            session['user_id']
        ))
        
        order_id = cursor.lastrowid
        
        # Insert order items and update inventory
        items = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('unit_price[]')
        
        total = 0
        for i in range(len(items)):
            if items[i]:
                product_id = int(items[i])
                quantity = int(quantities[i])
                unit_price = float(prices[i])
                subtotal = quantity * unit_price
                total += subtotal
                
                db.execute('''
                    INSERT INTO sales_order_items (order_id, product_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, product_id, quantity, unit_price, subtotal))
                
                # Update inventory if order is completed
                if request.form.get('status') == 'completed':
                    db.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', (quantity, product_id))
        
        # Update order total
        db.execute('UPDATE sales_orders SET total_amount = ? WHERE id = ?', (total, order_id))
        
        # Add transaction record
        db.execute('''
            INSERT INTO transactions (type, category, amount, description, reference_type, reference_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('income', 'sales', total, f'Sales Order {order_number}', 'sales_order', order_id, session['user_id']))
        
        db.commit()
        db.close()
        return redirect(url_for('sales'))
    
    db = get_db()
    customers = db.execute('SELECT * FROM customers ORDER BY name').fetchall()
    products = db.execute('SELECT * FROM products ORDER BY name').fetchall()
    db.close()
    return render_template('sales_form.html', customers=customers, products=products)

# Reports route
@app.route('/reports')
@login_required
def reports():
    db = get_db()
    
    reports_data = {
        'inventory_value': db.execute('SELECT SUM(quantity * unit_price) as value FROM products').fetchone()['value'] or 0,
        'low_stock_items': db.execute('SELECT * FROM products WHERE quantity <= reorder_level').fetchall(),
        'top_products': db.execute('''
            SELECT p.name, SUM(soi.quantity) as total_sold, SUM(soi.subtotal) as revenue
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            GROUP BY p.id
            ORDER BY total_sold DESC
            LIMIT 5
        ''').fetchall(),
        'monthly_sales': db.execute('''
            SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as total
            FROM sales_orders
            WHERE status = 'completed'
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        ''').fetchall(),
        'top_customers': db.execute('''
            SELECT c.name, COUNT(so.id) as order_count, SUM(so.total_amount) as total_spent
            FROM customers c
            JOIN sales_orders so ON c.id = so.customer_id
            WHERE so.status = 'completed'
            GROUP BY c.id
            ORDER BY total_spent DESC
            LIMIT 5
        ''').fetchall()
    }
    
    db.close()
    return render_template('reports.html', data=reports_data)

# API endpoints for dynamic data
@app.route('/api/products')
@login_required
def api_products():
    db = get_db()
    products = db.execute('SELECT id, name, sku, unit_price, quantity FROM products ORDER BY name').fetchall()
    db.close()
    return jsonify([dict(p) for p in products])

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists('database'):
        os.makedirs('database')
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
