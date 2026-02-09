# Quick Start Guide - Simple ERP

## Getting Started in 5 Minutes

### 1. Installation (2 minutes)

```bash
# Navigate to the project folder
cd simple-erp

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 2. First Login (30 seconds)

Open your browser and go to: `http://localhost:5000`

Login with:
- Username: `admin`
- Password: `admin123`

### 3. Add Your First Supplier (1 minute)

1. Click "Suppliers" in the sidebar
2. Click "+ Add Supplier"
3. Fill in the form:
   - Name: "ABC Wholesale"
   - Contact Person: "John Smith"
   - Email: "john@abcwholesale.com"
   - Phone: "555-1234"
4. Click "Add Supplier"

### 4. Add Your First Product (1 minute)

1. Click "Inventory" in the sidebar
2. Click "+ Add Product"
3. Fill in the form:
   - Product Name: "Office Chair"
   - SKU: "CHAIR-001"
   - Category: "Furniture"
   - Quantity: "50"
   - Unit Price: "149.99"
   - Reorder Level: "10"
   - Supplier: Select "ABC Wholesale"
4. Click "Add Product"

### 5. Add Your First Customer (1 minute)

1. Click "Customers" in the sidebar
2. Click "+ Add Customer"
3. Fill in:
   - Full Name: "Sarah Johnson"
   - Company: "Tech Startup Inc"
   - Email: "sarah@techstartup.com"
   - Phone: "555-5678"
4. Click "Add Customer"

### 6. Create Your First Sale (1.5 minutes)

1. Click "Sales" in the sidebar
2. Click "+ New Order"
3. Select Customer: "Sarah Johnson"
4. Add Items:
   - Select Product: "Office Chair"
   - Quantity: "5"
   - Price will auto-fill
5. Status: "Completed"
6. Click "Create Order"

### 7. View Your Dashboard

Click "Dashboard" to see:
- Total Products: 1
- Total Customers: 1
- Recent Orders: Your first sale
- Total Sales: $749.95

## Common Tasks

### Check Low Stock Items
1. Go to Dashboard
2. Look at "Low Stock Items" card
3. Or go to Reports → Low Stock Items

### View Sales Reports
1. Click "Reports" in sidebar
2. Review:
   - Inventory value
   - Top selling products
   - Monthly sales trends
   - Top customers

### Update Product Quantity
1. Go to Inventory
2. Click "Edit" on the product
3. Update quantity
4. Click "Update Product"

### Change Order Status
Currently orders are created with a status. In future versions, you'll be able to update order status.

## Tips for Best Results

✅ **DO:**
- Use unique SKU codes for each product
- Set realistic reorder levels
- Mark orders as "Completed" to update inventory
- Review reports weekly
- Keep customer information up to date

❌ **DON'T:**
- Delete products that have order history
- Set reorder level to 0 (unless intentional)
- Leave required fields empty
- Use special characters in SKU codes

## Keyboard Shortcuts

- **Tab**: Navigate between form fields
- **Enter**: Submit forms
- **Esc**: Cancel/go back (in some browsers)

## Understanding the Interface

### Color Coding
- 🔵 **Blue**: Primary actions (Add, Save, Create)
- ⚪ **Gray**: Secondary actions (Cancel, Back)
- 🟢 **Green**: Success states (Completed orders)
- 🟡 **Yellow**: Warning states (Low stock, Pending)
- 🔴 **Red**: Delete/danger actions

### Status Badges
- **Pending** (Yellow): Order is waiting to be processed
- **Completed** (Green): Order is finished, inventory updated
- **Cancelled** (Red): Order is cancelled

### Icons Guide
- 📊 Dashboard
- 📦 Inventory
- 💰 Sales
- 👥 Customers
- 🏭 Suppliers
- 📈 Reports

## Next Steps

Once you're comfortable with the basics:

1. **Add More Products**: Build your complete inventory
2. **Import Customer Data**: Add all your customers
3. **Process Daily Orders**: Make sales order entry part of your routine
4. **Review Weekly Reports**: Check performance and stock levels
5. **Plan Reorders**: Use low stock alerts to place supplier orders

## Need Help?

- Check the main README.md for detailed documentation
- Review the database schema for data structure
- Look at the code comments in app.py for logic explanations

---

**You're ready to go! Start managing your business with Simple ERP** 🎉
