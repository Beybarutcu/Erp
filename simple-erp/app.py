from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATABASE = 'database/erp.db'

# Load translations from JSON files
def load_translations():
    """Load translation files from translations/ directory"""
    translations = {}
    translation_dir = os.path.join(os.path.dirname(__file__), 'translations')
    
    for lang_code in ['tr', 'en']:
        file_path = os.path.join(translation_dir, f'{lang_code}.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                translations[lang_code] = json.load(f)
        else:
            # Fallback to empty dict if file not found
            translations[lang_code] = {}
    
    return translations

# Load translations once at startup
TRANSLATIONS = load_translations()

def get_translation(key, lang=None):
    """Get translation for a key"""
    if lang is None:
        lang = session.get('language', 'tr')
    return TRANSLATIONS.get(lang, TRANSLATIONS.get('tr', {})).get(key, key)

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
            language TEXT DEFAULT 'tr',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products/Inventory table - Enhanced for manufacturing
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            description TEXT,
            category TEXT,
            product_type TEXT DEFAULT 'finished_good',
            material_type TEXT,
            material_grade TEXT,
            color TEXT,
            piece_weight REAL,
            dimensions TEXT,
            quantity INTEGER DEFAULT 0,
            unit TEXT DEFAULT 'pcs',
            unit_price REAL NOT NULL,
            cost_price REAL,
            reorder_level INTEGER DEFAULT 10,
            supplier_id INTEGER,
            mold_id INTEGER,
            cycle_time INTEGER,
            pieces_per_hour INTEGER,
            technical_drawing_no TEXT,
            packaging_qty INTEGER,
            storage_location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (mold_id) REFERENCES molds(id)
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
    
    # Molds table - NEW
    db.execute('''
        CREATE TABLE IF NOT EXISTS molds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mold_code TEXT UNIQUE NOT NULL,
            mold_name TEXT NOT NULL,
            cavity_count INTEGER NOT NULL,
            compatible_materials TEXT,
            required_tonnage_min INTEGER,
            required_tonnage_max INTEGER,
            cycle_time INTEGER,
            status TEXT DEFAULT 'active',
            total_shots INTEGER DEFAULT 0,
            shots_since_maintenance INTEGER DEFAULT 0,
            maintenance_interval INTEGER DEFAULT 500000,
            last_maintenance_date DATE,
            next_maintenance_date DATE,
            location TEXT,
            weight REAL,
            dimensions TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Machines table - NEW
    db.execute('''
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_code TEXT UNIQUE NOT NULL,
            machine_name TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            tonnage INTEGER,
            injection_unit INTEGER,
            screw_diameter INTEGER,
            max_shot_weight INTEGER,
            min_mold_size INTEGER,
            max_mold_size INTEGER,
            power_consumption INTEGER,
            status TEXT DEFAULT 'idle',
            location TEXT,
            section TEXT,
            last_maintenance_date DATE,
            next_maintenance_date DATE,
            maintenance_interval_days INTEGER DEFAULT 90,
            total_hours INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Production Orders table - NEW
    db.execute('''
        CREATE TABLE IF NOT EXISTS production_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            product_id INTEGER NOT NULL,
            mold_id INTEGER NOT NULL,
            machine_id INTEGER,
            operator_name TEXT,
            planned_quantity INTEGER NOT NULL,
            produced_quantity INTEGER DEFAULT 0,
            scrap_quantity INTEGER DEFAULT 0,
            raw_material_used REAL DEFAULT 0,
            status TEXT DEFAULT 'planned',
            planned_start_date DATE,
            actual_start_date TIMESTAMP,
            planned_end_date DATE,
            actual_end_date TIMESTAMP,
            quality_status TEXT DEFAULT 'pending',
            quality_inspector TEXT,
            quality_date TIMESTAMP,
            quality_notes TEXT,
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (mold_id) REFERENCES molds(id),
            FOREIGN KEY (machine_id) REFERENCES machines(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
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
            "INSERT INTO users (username, password, full_name, role, email, language) VALUES (?, ?, ?, ?, ?, ?)",
            ('admin', hashed_pw, 'Sistem Yöneticisi', 'admin', 'admin@company.com', 'tr')
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
            session['language'] = user['language'] if user['language'] else 'tr'
            return redirect(url_for('dashboard'))
        
        error = get_translation('invalid_credentials', session.get('language', 'tr'))
        return render_template('login.html', error=error, t=get_translation)
    
    return render_template('login.html', t=get_translation)

@app.route('/set-language/<lang>')
def set_language(lang):
    """Dil değiştirme / Change language"""
    if lang in ['tr', 'en']:
        session['language'] = lang
        # Kullanıcı giriş yapmışsa veritabanını güncelle
        if 'user_id' in session:
            db = get_db()
            db.execute('UPDATE users SET language = ? WHERE id = ?', (lang, session['user_id']))
            db.commit()
            db.close()
    return redirect(request.referrer or url_for('dashboard'))

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
    return render_template('dashboard.html', stats=stats, t=get_translation)

# Product/Inventory routes
@app.route('/products')
@login_required
def products():
    db = get_db()
    products = db.execute('''
        SELECT p.*, s.name as supplier_name, m.mold_code
        FROM products p 
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN molds m ON p.mold_id = m.id
        ORDER BY p.name
    ''').fetchall()
    db.close()
    return render_template('products.html', products=products, t=get_translation)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO products (name, sku, description, category, product_type, material_type,
                                material_grade, color, piece_weight, dimensions, quantity, unit,
                                unit_price, cost_price, reorder_level, supplier_id, mold_id,
                                cycle_time, pieces_per_hour, technical_drawing_no, packaging_qty,
                                storage_location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['sku'],
            request.form.get('description', ''),
            request.form.get('category', ''),
            request.form.get('product_type', 'finished_good'),
            request.form.get('material_type', ''),
            request.form.get('material_grade', ''),
            request.form.get('color', ''),
            float(request.form.get('piece_weight', 0)) if request.form.get('piece_weight') else None,
            request.form.get('dimensions', ''),
            int(request.form.get('quantity', 0)),
            request.form.get('unit', 'pcs'),
            float(request.form['unit_price']),
            float(request.form.get('cost_price', 0)) if request.form.get('cost_price') else None,
            int(request.form.get('reorder_level', 10)),
            int(request.form['supplier_id']) if request.form.get('supplier_id') else None,
            int(request.form['mold_id']) if request.form.get('mold_id') else None,
            int(request.form.get('cycle_time', 0)) if request.form.get('cycle_time') else None,
            int(request.form.get('pieces_per_hour', 0)) if request.form.get('pieces_per_hour') else None,
            request.form.get('technical_drawing_no', ''),
            int(request.form.get('packaging_qty', 0)) if request.form.get('packaging_qty') else None,
            request.form.get('storage_location', '')
        ))
        db.commit()
        db.close()
        return redirect(url_for('products'))
    
    db = get_db()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    molds = db.execute('SELECT * FROM molds ORDER BY mold_code').fetchall()
    db.close()
    return render_template('product_form.html', product=None, suppliers=suppliers, molds=molds, t=get_translation)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE products 
            SET name=?, sku=?, description=?, category=?, product_type=?, material_type=?,
                material_grade=?, color=?, piece_weight=?, dimensions=?, quantity=?, unit=?,
                unit_price=?, cost_price=?, reorder_level=?, supplier_id=?, mold_id=?,
                cycle_time=?, pieces_per_hour=?, technical_drawing_no=?, packaging_qty=?,
                storage_location=?, updated_at=?
            WHERE id=?
        ''', (
            request.form['name'],
            request.form['sku'],
            request.form.get('description', ''),
            request.form.get('category', ''),
            request.form.get('product_type', 'finished_good'),
            request.form.get('material_type', ''),
            request.form.get('material_grade', ''),
            request.form.get('color', ''),
            float(request.form.get('piece_weight', 0)) if request.form.get('piece_weight') else None,
            request.form.get('dimensions', ''),
            int(request.form.get('quantity', 0)),
            request.form.get('unit', 'pcs'),
            float(request.form['unit_price']),
            float(request.form.get('cost_price', 0)) if request.form.get('cost_price') else None,
            int(request.form.get('reorder_level', 10)),
            int(request.form['supplier_id']) if request.form.get('supplier_id') else None,
            int(request.form['mold_id']) if request.form.get('mold_id') else None,
            int(request.form.get('cycle_time', 0)) if request.form.get('cycle_time') else None,
            int(request.form.get('pieces_per_hour', 0)) if request.form.get('pieces_per_hour') else None,
            request.form.get('technical_drawing_no', ''),
            int(request.form.get('packaging_qty', 0)) if request.form.get('packaging_qty') else None,
            request.form.get('storage_location', ''),
            datetime.now(),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('products'))
    
    product = db.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    molds = db.execute('SELECT * FROM molds ORDER BY mold_code').fetchall()
    db.close()
    return render_template('product_form.html', product=product, suppliers=suppliers, molds=molds, t=get_translation)

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
    return render_template('customers.html', customers=customers, t=get_translation)

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
    
    return render_template('customer_form.html', customer=None, t=get_translation)

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
    return render_template('customer_form.html', customer=customer, t=get_translation)

# Supplier routes
@app.route('/suppliers')
@login_required
def suppliers():
    db = get_db()
    suppliers = db.execute('SELECT * FROM suppliers ORDER BY name').fetchall()
    db.close()
    return render_template('suppliers.html', suppliers=suppliers, t=get_translation)

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
    
    return render_template('supplier_form.html', supplier=None, t=get_translation)

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
    return render_template('supplier_form.html', supplier=supplier, t=get_translation)

# Mold Management Routes
@app.route('/molds')
@login_required
def molds():
    db = get_db()
    molds = db.execute('SELECT * FROM molds ORDER BY mold_code').fetchall()
    db.close()
    return render_template('molds.html', molds=molds, t=get_translation)

@app.route('/molds/add', methods=['GET', 'POST'])
@login_required
def add_mold():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO molds (mold_code, mold_name, cavity_count, compatible_materials,
                             required_tonnage_min, required_tonnage_max, cycle_time, status,
                             total_shots, maintenance_interval, last_maintenance_date, 
                             next_maintenance_date, location, weight, dimensions, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['mold_code'],
            request.form['mold_name'],
            int(request.form['cavity_count']),
            request.form.get('compatible_materials', ''),
            int(request.form['required_tonnage_min']) if request.form.get('required_tonnage_min') else None,
            int(request.form['required_tonnage_max']) if request.form.get('required_tonnage_max') else None,
            int(request.form['cycle_time']) if request.form.get('cycle_time') else None,
            request.form.get('status', 'active'),
            int(request.form.get('total_shots', 0)),
            int(request.form.get('maintenance_interval', 500000)),
            request.form.get('last_maintenance_date'),
            request.form.get('next_maintenance_date'),
            request.form.get('location', ''),
            float(request.form.get('weight', 0)) if request.form.get('weight') else None,
            request.form.get('dimensions', ''),
            request.form.get('notes', '')
        ))
        db.commit()
        db.close()
        return redirect(url_for('molds'))
    
    return render_template('mold_form.html', mold=None, t=get_translation)

@app.route('/molds/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mold(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE molds 
            SET mold_code=?, mold_name=?, cavity_count=?, compatible_materials=?,
                required_tonnage_min=?, required_tonnage_max=?, cycle_time=?, status=?,
                total_shots=?, maintenance_interval=?, last_maintenance_date=?, 
                next_maintenance_date=?, location=?, weight=?, dimensions=?, notes=?
            WHERE id=?
        ''', (
            request.form['mold_code'],
            request.form['mold_name'],
            int(request.form['cavity_count']),
            request.form.get('compatible_materials', ''),
            int(request.form['required_tonnage_min']) if request.form.get('required_tonnage_min') else None,
            int(request.form['required_tonnage_max']) if request.form.get('required_tonnage_max') else None,
            int(request.form['cycle_time']) if request.form.get('cycle_time') else None,
            request.form.get('status', 'active'),
            int(request.form.get('total_shots', 0)),
            int(request.form.get('maintenance_interval', 500000)),
            request.form.get('last_maintenance_date'),
            request.form.get('next_maintenance_date'),
            request.form.get('location', ''),
            float(request.form.get('weight', 0)) if request.form.get('weight') else None,
            request.form.get('dimensions', ''),
            request.form.get('notes', ''),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('molds'))
    
    mold = db.execute('SELECT * FROM molds WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('mold_form.html', mold=mold, t=get_translation)

@app.route('/molds/delete/<int:id>')
@login_required
def delete_mold(id):
    db = get_db()
    db.execute('DELETE FROM molds WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('molds'))

# Machine Management Routes
@app.route('/machines')
@login_required
def machines():
    db = get_db()
    machines = db.execute('SELECT * FROM machines ORDER BY machine_code').fetchall()
    db.close()
    return render_template('machines.html', machines=machines, t=get_translation)

@app.route('/machines/add', methods=['GET', 'POST'])
@login_required
def add_machine():
    if request.method == 'POST':
        db = get_db()
        db.execute('''
            INSERT INTO machines (machine_code, machine_name, brand, model, tonnage,
                                injection_unit, screw_diameter, max_shot_weight,
                                min_mold_size, max_mold_size, power_consumption,
                                status, location, section, last_maintenance_date,
                                next_maintenance_date, maintenance_interval_days,
                                total_hours, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['machine_code'],
            request.form['machine_name'],
            request.form.get('brand', ''),
            request.form.get('model', ''),
            int(request.form['tonnage']) if request.form.get('tonnage') else None,
            int(request.form.get('injection_unit', 0)) if request.form.get('injection_unit') else None,
            int(request.form.get('screw_diameter', 0)) if request.form.get('screw_diameter') else None,
            int(request.form.get('max_shot_weight', 0)) if request.form.get('max_shot_weight') else None,
            int(request.form.get('min_mold_size', 0)) if request.form.get('min_mold_size') else None,
            int(request.form.get('max_mold_size', 0)) if request.form.get('max_mold_size') else None,
            int(request.form.get('power_consumption', 0)) if request.form.get('power_consumption') else None,
            request.form.get('status', 'idle'),
            request.form.get('location', ''),
            request.form.get('section', ''),
            request.form.get('last_maintenance_date'),
            request.form.get('next_maintenance_date'),
            int(request.form.get('maintenance_interval_days', 90)),
            int(request.form.get('total_hours', 0)),
            request.form.get('notes', '')
        ))
        db.commit()
        db.close()
        return redirect(url_for('machines'))
    
    return render_template('machine_form.html', machine=None, t=get_translation)

@app.route('/machines/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_machine(id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('''
            UPDATE machines 
            SET machine_code=?, machine_name=?, brand=?, model=?, tonnage=?,
                injection_unit=?, screw_diameter=?, max_shot_weight=?,
                min_mold_size=?, max_mold_size=?, power_consumption=?,
                status=?, location=?, section=?, last_maintenance_date=?,
                next_maintenance_date=?, maintenance_interval_days=?,
                total_hours=?, notes=?
            WHERE id=?
        ''', (
            request.form['machine_code'],
            request.form['machine_name'],
            request.form.get('brand', ''),
            request.form.get('model', ''),
            int(request.form['tonnage']) if request.form.get('tonnage') else None,
            int(request.form.get('injection_unit', 0)) if request.form.get('injection_unit') else None,
            int(request.form.get('screw_diameter', 0)) if request.form.get('screw_diameter') else None,
            int(request.form.get('max_shot_weight', 0)) if request.form.get('max_shot_weight') else None,
            int(request.form.get('min_mold_size', 0)) if request.form.get('min_mold_size') else None,
            int(request.form.get('max_mold_size', 0)) if request.form.get('max_mold_size') else None,
            int(request.form.get('power_consumption', 0)) if request.form.get('power_consumption') else None,
            request.form.get('status', 'idle'),
            request.form.get('location', ''),
            request.form.get('section', ''),
            request.form.get('last_maintenance_date'),
            request.form.get('next_maintenance_date'),
            int(request.form.get('maintenance_interval_days', 90)),
            int(request.form.get('total_hours', 0)),
            request.form.get('notes', ''),
            id
        ))
        db.commit()
        db.close()
        return redirect(url_for('machines'))
    
    machine = db.execute('SELECT * FROM machines WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('machine_form.html', machine=machine, t=get_translation)

@app.route('/machines/delete/<int:id>')
@login_required
def delete_machine(id):
    db = get_db()
    db.execute('DELETE FROM machines WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('machines'))

# Production Management Routes
@app.route('/production')
@login_required
def production():
    db = get_db()
    orders = db.execute('''
        SELECT po.*, p.name as product_name, p.sku, m.mold_code, mc.machine_code
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        JOIN molds m ON po.mold_id = m.id
        LEFT JOIN machines mc ON po.machine_id = mc.id
        ORDER BY po.created_at DESC
    ''').fetchall()
    db.close()
    return render_template('production.html', orders=orders, t=get_translation)

@app.route('/production/add', methods=['GET', 'POST'])
@login_required
def add_production():
    if request.method == 'POST':
        db = get_db()
        
        # Generate order number
        order_count = db.execute('SELECT COUNT(*) as count FROM production_orders').fetchone()['count']
        order_number = f'PO-{order_count + 1:05d}'
        
        db.execute('''
            INSERT INTO production_orders (order_number, product_id, mold_id, machine_id,
                                         operator_name, planned_quantity, planned_start_date,
                                         planned_end_date, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_number,
            int(request.form['product_id']),
            int(request.form['mold_id']),
            int(request.form['machine_id']) if request.form.get('machine_id') else None,
            request.form.get('operator_name', ''),
            int(request.form['planned_quantity']),
            request.form.get('planned_start_date'),
            request.form.get('planned_end_date'),
            request.form.get('notes', ''),
            session['user_id']
        ))
        db.commit()
        db.close()
        return redirect(url_for('production'))
    
    db = get_db()
    products = db.execute('SELECT * FROM products WHERE product_type = "finished_good" ORDER BY name').fetchall()
    molds = db.execute('SELECT * FROM molds WHERE status = "active" ORDER BY mold_code').fetchall()
    machines = db.execute('SELECT * FROM machines ORDER BY machine_code').fetchall()
    db.close()
    return render_template('production_form.html', order=None, products=products, 
                         molds=molds, machines=machines, t=get_translation)

@app.route('/production/start/<int:id>', methods=['POST'])
@login_required
def start_production(id):
    db = get_db()
    db.execute('''
        UPDATE production_orders 
        SET status = 'in_progress', actual_start_date = ?
        WHERE id = ?
    ''', (datetime.now(), id))
    db.commit()
    db.close()
    return redirect(url_for('production'))

@app.route('/production/complete/<int:id>', methods=['GET', 'POST'])
@login_required
def complete_production(id):
    db = get_db()
    
    if request.method == 'POST':
        produced = int(request.form['produced_quantity'])
        scrap = int(request.form['scrap_quantity'])
        material_used = float(request.form.get('raw_material_used', 0))
        
        db.execute('''
            UPDATE production_orders 
            SET status = 'completed', 
                actual_end_date = ?,
                produced_quantity = ?,
                scrap_quantity = ?,
                raw_material_used = ?,
                quality_status = 'pending'
            WHERE id = ?
        ''', (datetime.now(), produced, scrap, material_used, id))
        
        # Update mold shots
        order = db.execute('SELECT mold_id FROM production_orders WHERE id = ?', (id,)).fetchone()
        db.execute('''
            UPDATE molds 
            SET total_shots = total_shots + ?,
                shots_since_maintenance = shots_since_maintenance + ?
            WHERE id = ?
        ''', (produced + scrap, produced + scrap, order['mold_id']))
        
        db.commit()
        db.close()
        return redirect(url_for('production'))
    
    order = db.execute('''
        SELECT po.*, p.name as product_name, m.mold_code
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        JOIN molds m ON po.mold_id = m.id
        WHERE po.id = ?
    ''', (id,)).fetchone()
    db.close()
    return render_template('production_complete.html', order=order, t=get_translation)

@app.route('/production/quality/<int:id>', methods=['GET', 'POST'])
@login_required
def production_quality(id):
    db = get_db()
    
    if request.method == 'POST':
        quality_result = request.form['quality_status']
        
        db.execute('''
            UPDATE production_orders 
            SET quality_status = ?,
                quality_inspector = ?,
                quality_date = ?,
                quality_notes = ?
            WHERE id = ?
        ''', (
            quality_result,
            request.form.get('quality_inspector', ''),
            datetime.now(),
            request.form.get('quality_notes', ''),
            id
        ))
        
        # If quality passed, update product stock
        if quality_result == 'passed':
            order = db.execute('SELECT product_id, produced_quantity FROM production_orders WHERE id = ?', (id,)).fetchone()
            db.execute('''
                UPDATE products 
                SET quantity = quantity + ?
                WHERE id = ?
            ''', (order['produced_quantity'], order['product_id']))
        
        db.commit()
        db.close()
        return redirect(url_for('production'))
    
    order = db.execute('''
        SELECT po.*, p.name as product_name
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        WHERE po.id = ?
    ''', (id,)).fetchone()
    db.close()
    return render_template('production_quality.html', order=order, t=get_translation)

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
    return render_template('sales.html', orders=orders, t=get_translation)

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
    return render_template('sales_form.html', customers=customers, t=get_translation, products=products)

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
    return render_template('reports.html', data=reports_data, t=get_translation)

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
