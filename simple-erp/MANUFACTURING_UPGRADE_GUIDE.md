# Manufacturing ERP Upgrade Guide
## Plastik Kalıp ve Ürün Üreticisi için ERP Geliştirme Rehberi

This guide explains how to add manufacturing-specific features and Turkish language support to your ERP system.

## 🎯 New Features for Plastic Mold Manufacturing

### 1. **Kalıp Yönetimi (Mold Management)**
Track and manage plastic injection molds:
- Mold code and name
- Cavity count (kaç gözlü)
- Material type compatibility
- Cycle time tracking
- Maintenance scheduling
- Shot counter
- Status tracking (Active/Maintenance/Inactive)

### 2. **Hammadde Yönetimi (Raw Materials Management)**
Manage plastic resins and materials:
- Material code and specifications
- Grade and type (PP, PE, ABS, etc.)
- Stock levels in kg
- Supplier linkage
- Reorder levels
- Storage location tracking

### 3. **Üretim Emirleri (Production Orders)**
Complete production tracking:
- Link products to molds
- Plan production quantities
- Track actual production vs planned
- Scrap/fire tracking
- Operator assignment
- Machine assignment
- Raw material consumption
- Cycle time monitoring

### 4. **Kalite Kontrol (Quality Control)**
Quality inspection system:
- Sample-based inspections
- Pass/fail tracking
- Defect type recording
- Corrective actions
- Inspector assignment

### 5. **İki Dilli Sistem (Bilingual System)**
Complete Turkish and English support:
- Turkish as default language
- Language switcher
- All interface elements translated
- User preference saving

## 📋 Database Changes Required

### New Tables to Add:

```sql
-- Molds Table
CREATE TABLE molds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mold_code TEXT UNIQUE NOT NULL,
    mold_name TEXT NOT NULL,
    cavity_count INTEGER NOT NULL,
    material_type TEXT,
    tonnage REAL,
    cycle_time INTEGER,
    status TEXT DEFAULT 'active',
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    total_shots INTEGER DEFAULT 0,
    location TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Materials Table
CREATE TABLE raw_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_code TEXT UNIQUE NOT NULL,
    material_name TEXT NOT NULL,
    material_type TEXT,
    grade TEXT,
    supplier_id INTEGER,
    stock_quantity REAL DEFAULT 0,
    unit TEXT DEFAULT 'kg',
    unit_price REAL,
    reorder_level REAL DEFAULT 100,
    storage_location TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Production Orders Table
CREATE TABLE production_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    product_id INTEGER NOT NULL,
    mold_id INTEGER NOT NULL,
    planned_quantity INTEGER NOT NULL,
    produced_quantity INTEGER DEFAULT 0,
    scrap_quantity INTEGER DEFAULT 0,
    production_date DATE,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    operator_name TEXT,
    machine_number TEXT,
    raw_material_id INTEGER,
    material_used REAL,
    cycle_time_actual INTEGER,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (mold_id) REFERENCES molds(id),
    FOREIGN KEY (raw_material_id) REFERENCES raw_materials(id)
);

-- Quality Inspections Table
CREATE TABLE quality_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    production_order_id INTEGER NOT NULL,
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inspector_name TEXT,
    sample_size INTEGER,
    passed_count INTEGER,
    failed_count INTEGER,
    defect_types TEXT,
    result TEXT DEFAULT 'pending',
    corrective_action TEXT,
    notes TEXT,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(id)
);
```

### Enhanced Products Table:

Add these columns to existing products table:
```sql
ALTER TABLE products ADD COLUMN product_type TEXT DEFAULT 'finished_good';
ALTER TABLE products ADD COLUMN material_grade TEXT;
ALTER TABLE products ADD COLUMN color TEXT;
ALTER TABLE products ADD COLUMN weight REAL;
ALTER TABLE products ADD COLUMN dimensions TEXT;
ALTER TABLE products ADD COLUMN cost_price REAL;
ALTER TABLE products ADD COLUMN mold_id INTEGER;
ALTER TABLE products ADD COLUMN drawing_number TEXT;
ALTER TABLE products ADD COLUMN technical_specs TEXT;
ALTER TABLE products ADD COLUMN packaging_info TEXT;
```

### Enhanced Users Table:

Add language preference:
```sql
ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'tr';
```

## 🌐 Turkish Translation System

### Implementation Steps:

1. **Add Translation Dictionary** to app.py:

```python
TRANSLATIONS = {
    'tr': {
        'dashboard': 'Kontrol Paneli',
        'inventory': 'Envanter',
        'molds': 'Kalıplar',
        'production': 'Üretim',
        'raw_materials': 'Hammaddeler',
        'quality_control': 'Kalite Kontrol',
        # ... add all translations
    },
    'en': {
        'dashboard': 'Dashboard',
        'inventory': 'Inventory',
        'molds': 'Molds',
        'production': 'Production',
        'raw_materials': 'Raw Materials',
        'quality_control': 'Quality Control',
        # ... add all translations
    }
}

def get_translation(key, lang=None):
    if lang is None:
        lang = session.get('language', 'tr')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
```

2. **Add Language Switcher Route**:

```python
@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['tr', 'en']:
        session['language'] = lang
        if 'user_id' in session:
            db = get_db()
            db.execute('UPDATE users SET language = ? WHERE id = ?', (lang, session['user_id']))
            db.commit()
            db.close()
    return redirect(request.referrer or url_for('dashboard'))
```

3. **Update Templates** - Add to base.html:

```html
<div class="language-switcher">
    <a href="{{ url_for('set_language', lang='tr') }}" 
       class="{% if session.get('language') == 'tr' %}active{% endif %}">TR</a>
    <a href="{{ url_for('set_language', lang='en') }}" 
       class="{% if session.get('language') == 'en' %}active{% endif %}">EN</a>
</div>
```

4. **Use Translations in Templates**:

Replace hardcoded text with:
```html
<!-- Old -->
<h1>Dashboard</h1>

<!-- New -->
<h1>{{ t('dashboard') }}</h1>
```

And pass `t=get_translation` to all render_template calls:
```python
return render_template('dashboard.html', stats=stats, t=get_translation)
```

## 📄 New Pages to Create

### 1. Molds Page (templates/molds.html)

```html
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1>{{ t('molds') }}</h1>
    <a href="{{ url_for('add_mold') }}" class="btn-primary">+ {{ t('add_mold') }}</a>
</div>

<div class="content-section">
    <table class="data-table">
        <thead>
            <tr>
                <th>{{ t('mold_code') }}</th>
                <th>{{ t('mold_name') }}</th>
                <th>{{ t('cavity_count') }}</th>
                <th>{{ t('material_type') }}</th>
                <th>{{ t('cycle_time') }}</th>
                <th>{{ t('status') }}</th>
                <th>{{ t('actions') }}</th>
            </tr>
        </thead>
        <tbody>
            {% for mold in molds %}
            <tr>
                <td>{{ mold.mold_code }}</td>
                <td>{{ mold.mold_name }}</td>
                <td>{{ mold.cavity_count }} {{ t('cavity') }}</td>
                <td>{{ mold.material_type or '-' }}</td>
                <td>{{ mold.cycle_time }} sn</td>
                <td><span class="badge badge-{{ mold.status }}">{{ t(mold.status) }}</span></td>
                <td class="actions">
                    <a href="{{ url_for('edit_mold', id=mold.id) }}" class="btn-small btn-edit">{{ t('edit') }}</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### 2. Production Orders Page (templates/production.html)

```html
{% extends "base.html" %}
{% block content %}
<div class="page-header">
    <h1>{{ t('production') }}</h1>
    <a href="{{ url_for('add_production') }}" class="btn-primary">+ {{ t('new_production') }}</a>
</div>

<div class="content-section">
    <table class="data-table">
        <thead>
            <tr>
                <th>{{ t('production_order') }}</th>
                <th>{{ t('product_name') }}</th>
                <th>{{ t('mold_code') }}</th>
                <th>{{ t('planned_quantity') }}</th>
                <th>{{ t('produced_quantity') }}</th>
                <th>{{ t('scrap_quantity') }}</th>
                <th>{{ t('status') }}</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.order_number }}</td>
                <td>{{ order.product_name }}</td>
                <td>{{ order.mold_code }}</td>
                <td>{{ order.planned_quantity }}</td>
                <td>{{ order.produced_quantity }}</td>
                <td class="{% if order.scrap_quantity > 0 %}warning-text{% endif %}">
                    {{ order.scrap_quantity }}
                </td>
                <td><span class="badge badge-{{ order.status }}">{{ t(order.status) }}</span></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### 3. Raw Materials Page (templates/raw_materials.html)

Similar structure showing material code, name, stock quantity, and reorder alerts.

## 🎨 Enhanced Dashboard

Add manufacturing-specific statistics:

```python
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    stats = {
        # Existing stats...
        'total_molds': db.execute('SELECT COUNT(*) FROM molds').fetchone()[0],
        'active_molds': db.execute('SELECT COUNT(*) FROM molds WHERE status = "active"').fetchone()[0],
        'production_today': db.execute(
            'SELECT COUNT(*) FROM production_orders WHERE DATE(production_date) = DATE("now")'
        ).fetchone()[0],
        'low_stock_materials': db.execute(
            'SELECT COUNT(*) FROM raw_materials WHERE stock_quantity <= reorder_level'
        ).fetchone()[0],
        'recent_production': db.execute('''
            SELECT po.*, p.name as product_name, m.mold_code
            FROM production_orders po
            JOIN products p ON po.product_id = p.id
            JOIN molds m ON po.mold_id = m.id
            ORDER BY po.created_at DESC LIMIT 5
        ''').fetchall()
    }
    return render_template('dashboard.html', stats=stats, t=get_translation)
```

## 📊 Enhanced Reports

Add manufacturing-specific reports:

```python
@app.route('/reports')
@login_required
def reports():
    db = get_db()
    reports_data = {
        # ... existing reports
        'production_efficiency': db.execute('''
            SELECT 
                SUM(produced_quantity) as total_produced,
                SUM(scrap_quantity) as total_scrap,
                AVG((produced_quantity - scrap_quantity) * 100.0 / produced_quantity) as efficiency
            FROM production_orders
            WHERE status = 'completed' AND produced_quantity > 0
        ''').fetchone(),
        'mold_utilization': db.execute('''
            SELECT m.mold_code, m.mold_name, COUNT(po.id) as usage_count,
                   SUM(po.produced_quantity) as total_pieces
            FROM molds m
            LEFT JOIN production_orders po ON m.id = po.mold_id
            GROUP BY m.id
            ORDER BY usage_count DESC
            LIMIT 10
        ''').fetchall(),
        'material_consumption': db.execute('''
            SELECT rm.material_name, SUM(po.material_used) as total_used
            FROM production_orders po
            JOIN raw_materials rm ON po.raw_material_id = rm.id
            WHERE po.status = 'completed'
            GROUP BY rm.id
            ORDER BY total_used DESC
            LIMIT 5
        ''').fetchall()
    }
    return render_template('reports.html', data=reports_data, t=get_translation)
```

## 🔄 Navigation Update

Update base.html navigation to include new sections:

```html
<ul class="nav-menu">
    <li><a href="{{ url_for('dashboard') }}">
        <span class="icon">📊</span> {{ t('dashboard') }}
    </a></li>
    <li><a href="{{ url_for('products') }}">
        <span class="icon">📦</span> {{ t('inventory') }}
    </a></li>
    <li><a href="{{ url_for('molds') }}">
        <span class="icon">🔧</span> {{ t('molds') }}
    </a></li>
    <li><a href="{{ url_for('production') }}">
        <span class="icon">⚙️</span> {{ t('production') }}
    </a></li>
    <li><a href="{{ url_for('raw_materials') }}">
        <span class="icon">🧱</span> {{ t('raw_materials') }}
    </a></li>
    <li><a href="{{ url_for('sales') }}">
        <span class="icon">💰</span> {{ t('sales') }}
    </a></li>
    <li><a href="{{ url_for('customers') }}">
        <span class="icon">👥</span> {{ t('customers') }}
    </a></li>
    <li><a href="{{ url_for('suppliers') }}">
        <span class="icon">🏭</span> {{ t('suppliers') }}
    </a></li>
    <li><a href="{{ url_for('reports') }}">
        <span class="icon">📈</span> {{ t('reports') }}
    </a></li>
</ul>
```

## 💡 Key Turkish Terms for Manufacturing

| English | Turkish |
|---------|---------|
| Mold | Kalıp |
| Cavity | Göz/Gözlü |
| Cycle Time | Çevrim Süresi |
| Production Order | Üretim Emri |
| Raw Material | Hammadde |
| Scrap/Waste | Fire |
| Quality Control | Kalite Kontrol |
| Operator | Operatör |
| Machine | Makine |
| Injection Molding | Enjeksiyon Kalıplama |
| Tonnage | Tonaj |
| Shot | Atış/Shot |
| Maintenance | Bakım |
| Resin | Reçine |
| Grade | Kalite/Sınıf |
| Defect | Hata/Kusur |
| Inspector | Kontrolör |
| Efficiency | Verimlilik |

## 🚀 Implementation Priority

1. **Phase 1**: Add language system (1-2 hours)
   - Add translation dictionary
   - Update all templates
   - Add language switcher

2. **Phase 2**: Add molds module (2-3 hours)
   - Create database table
   - Add routes
   - Create templates

3. **Phase 3**: Add raw materials (2-3 hours)
   - Create database table
   - Add routes
   - Create templates
   - Link to suppliers

4. **Phase 4**: Add production orders (3-4 hours)
   - Create database table
   - Add complex form
   - Link products, molds, materials
   - Track production metrics

5. **Phase 5**: Add quality control (2 hours)
   - Create database table
   - Link to production orders
   - Add inspection forms

6. **Phase 6**: Enhanced reporting (2 hours)
   - Production efficiency reports
   - Mold utilization
   - Material consumption
   - Scrap analysis

## 📦 Complete File Package

I can provide you with:
1. ✅ Updated app.py with all new features
2. ✅ All new template files
3. ✅ Enhanced CSS with Turkish language support
4. ✅ Migration SQL script
5. ✅ Complete documentation in Turkish and English

Would you like me to create the complete updated package with all these files ready to use?

## 🎯 Expected Benefits

- **Tam Türkçe Arayüz**: Complete Turkish interface for your team
- **Kalıp Takibi**: Track all molds, maintenance, and usage
- **Üretim Kontrolü**: Monitor production efficiency and waste
- **Hammadde Yönetimi**: Control raw material inventory
- **Kalite İzleme**: Track quality metrics
- **Detaylı Raporlar**: Manufacturing-specific analytics

Total estimated development time: 12-15 hours
Your manufacturing ERP will be complete and professional!
