# Simple ERP System

A clean, easy-to-understand ERP (Enterprise Resource Planning) system designed for small businesses with up to 50 employees.

## Features

### 📊 Dashboard
- Real-time business statistics
- Quick overview of products, customers, and sales
- Low stock alerts
- Recent orders tracking

### 📦 Inventory Management
- Add, edit, and delete products
- Track stock levels
- Set reorder points for automatic low-stock alerts
- Product categories and descriptions
- Supplier linkage

### 💰 Sales Management
- Create sales orders
- Link orders to customers
- Multi-item orders with automatic subtotal calculation
- Order status tracking (Pending, Completed, Cancelled)
- Automatic inventory updates on completed orders

### 👥 Customer Management
- Store customer information
- Contact details and addresses
- Company associations
- Order history tracking

### 🏭 Supplier Management
- Maintain supplier database
- Contact information
- Link products to suppliers

### 📈 Reports & Analytics
- Inventory value reports
- Low stock items
- Top selling products
- Monthly sales trends
- Top customers by revenue
- Sales performance metrics

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (file-based, no server needed)
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom CSS with modern, clean interface

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 3: Login

Use the default credentials:
- **Username**: admin
- **Password**: admin123

## Project Structure

```
simple-erp/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── database/
│   └── erp.db             # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css      # Stylesheet
│   ├── js/
│   │   └── script.js      # JavaScript functions
│   └── images/            # Image assets
└── templates/             # HTML templates
    ├── base.html          # Base template with navigation
    ├── login.html         # Login page
    ├── dashboard.html     # Main dashboard
    ├── products.html      # Product list
    ├── product_form.html  # Add/Edit product
    ├── customers.html     # Customer list
    ├── customer_form.html # Add/Edit customer
    ├── suppliers.html     # Supplier list
    ├── supplier_form.html # Add/Edit supplier
    ├── sales.html         # Sales orders list
    ├── sales_form.html    # Create sales order
    └── reports.html       # Reports & analytics
```

## Database Schema

### Users
- User authentication and authorization
- Roles: admin, manager, user

### Products
- SKU, name, description
- Category, quantity, price
- Reorder levels
- Supplier linkage

### Customers
- Name, company
- Contact information
- Address details

### Suppliers
- Name, contact person
- Email, phone
- Address

### Sales Orders
- Order number (auto-generated)
- Customer linkage
- Order date, status
- Total amount

### Sales Order Items
- Product linkage
- Quantity, price
- Subtotal calculations

### Transactions
- Financial tracking
- Income/expense records
- Reference to source (orders, etc.)

## Key Features Explained

### Inventory Management
- **Low Stock Alerts**: Products below reorder level are highlighted
- **Real-time Updates**: Inventory automatically decreases when orders are completed
- **Supplier Tracking**: Link products to suppliers for easy reordering

### Sales Orders
- **Dynamic Item Addition**: Add multiple items to a single order
- **Automatic Calculations**: Subtotals and totals calculated in real-time
- **Inventory Integration**: Completed orders automatically reduce stock

### Reporting
- **Visual Dashboard**: Quick overview cards for key metrics
- **Trend Analysis**: Monthly sales trends
- **Performance Metrics**: Top products and customers
- **Stock Analysis**: Inventory value and low stock warnings

## User Roles & Permissions

### Admin
- Full access to all features
- User management
- System configuration

### Manager (Future Enhancement)
- View and manage inventory
- Process sales orders
- Generate reports

### User (Future Enhancement)
- View-only access to reports
- Create sales orders
- Limited inventory access

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Login required for all pages
- SQL injection protection (parameterized queries)

## Customization

### Adding New Users
Currently done through database. Future versions will include user management UI.

### Modifying Colors/Theme
Edit `/static/css/style.css` and change CSS variables:
```css
:root {
    --primary-color: #2563eb;
    --primary-dark: #1e40af;
    /* ... other variables */
}
```

### Adding New Features
The modular structure makes it easy to add new modules:
1. Create route in `app.py`
2. Create template in `templates/`
3. Add navigation link in `base.html`

## Troubleshooting

### Database Issues
If you encounter database errors, delete `database/erp.db` and restart the application. It will create a fresh database.

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Template Not Found
Ensure all templates are in the `templates/` folder and named correctly.

## Best Practices

1. **Regular Backups**: Backup `database/erp.db` regularly
2. **Update Stock**: Keep inventory levels current
3. **Complete Orders**: Mark orders as completed to update inventory
4. **Review Reports**: Check low stock items weekly
5. **Data Entry**: Use consistent naming for products and categories

## Future Enhancements

- [ ] User management interface
- [ ] Purchase order management
- [ ] Advanced reporting with charts
- [ ] Email notifications for low stock
- [ ] Barcode scanning support
- [ ] Multi-location support
- [ ] Mobile app
- [ ] Export to Excel/PDF
- [ ] Advanced search and filtering
- [ ] Audit trail

## Support

For issues or questions, please refer to the documentation or create an issue in the project repository.

## License

This project is created for educational and small business use.

---

**Simple ERP** - Business Management Made Easy 🚀
