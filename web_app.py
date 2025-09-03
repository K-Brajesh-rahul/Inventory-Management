from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import json
import os
from database import InventoryDatabase
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize database
db = InventoryDatabase()

# Helper functions
def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_stock_status(current_stock, minimum_stock, reorder_point):
    """Get stock status and color"""
    if current_stock == 0:
        return {'status': 'Out of Stock', 'class': 'danger', 'icon': '❌'}
    elif current_stock <= minimum_stock:
        return {'status': 'Critical', 'class': 'danger', 'icon': '🔴'}
    elif current_stock <= reorder_point:
        return {'status': 'Low Stock', 'class': 'warning', 'icon': '🟡'}
    else:
        return {'status': 'In Stock', 'class': 'success', 'icon': '✅'}

# Template filters
app.jinja_env.filters['currency'] = format_currency

# Routes
@app.route('/')
def index():
    """Dashboard page"""
    try:
        stats = db.get_dashboard_stats()
        recent_alerts = db.get_unread_alerts()[:5]  # Show only 5 recent alerts
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             alerts=recent_alerts,
                             page_title="Dashboard")
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             stats={}, 
                             alerts=[],
                             page_title="Dashboard")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login (for demo purposes)"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple demo authentication
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Use admin/admin for demo.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/products')
def products():
    """Products management page"""
    try:
        products = db.get_all_products()
        
        # Add stock status to each product
        for product in products:
            status_info = get_stock_status(
                product['current_stock'], 
                product['minimum_stock'], 
                product['reorder_point']
            )
            product.update(status_info)
        
        return render_template('products.html', 
                             products=products,
                             page_title="Products")
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'error')
        return render_template('products.html', 
                             products=[],
                             page_title="Products")

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            product_data = {
                'name': request.form.get('name'),
                'sku': request.form.get('sku'),
                'description': request.form.get('description', ''),
                'unit_price': float(request.form.get('unit_price', 0)),
                'cost_price': float(request.form.get('cost_price', 0)),
                'current_stock': int(request.form.get('current_stock', 0)),
                'minimum_stock': int(request.form.get('minimum_stock', 10)),
                'maximum_stock': int(request.form.get('maximum_stock', 1000)),
                'reorder_point': int(request.form.get('reorder_point', 20)),
                'location': request.form.get('location', ''),
                'barcode': request.form.get('barcode', ''),
                'category_id': int(request.form.get('category_id')) if request.form.get('category_id') else None,
                'supplier_id': int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None
            }
            
            product_id = db.add_product(product_data)
            flash(f'Product "{product_data["name"]}" added successfully!', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
    
    # Load categories and suppliers for form
    categories = db.get_all_categories()
    suppliers = db.get_all_suppliers()
    
    return render_template('add_product.html', 
                         categories=categories,
                         suppliers=suppliers,
                         page_title="Add Product")

@app.route('/products/<int:product_id>/update_stock', methods=['POST'])
def update_stock(product_id):
    """Update product stock via AJAX"""
    try:
        new_stock = int(request.json.get('stock', 0))
        movement_type = request.json.get('movement_type', 'ADJUSTMENT')
        notes = request.json.get('notes', '')
        
        db.update_product_stock(product_id, new_stock, movement_type, notes)
        
        return jsonify({
            'success': True,
            'message': 'Stock updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/sales')
def sales():
    """Sales management page"""
    try:
        # Get recent sales (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        report = db.get_sales_report(start_date.isoformat(), end_date.isoformat())
        
        return render_template('sales.html', 
                             report=report,
                             page_title="Sales")
    except Exception as e:
        flash(f'Error loading sales: {str(e)}', 'error')
        return render_template('sales.html', 
                             report={'summary': {}, 'daily_sales': [], 'top_products': []},
                             page_title="Sales")

@app.route('/sales/new', methods=['GET', 'POST'])
def new_sale():
    """Create new sale"""
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.form.get('customer_name', 'Walk-in Customer')
            customer_email = request.form.get('customer_email', '')
            customer_phone = request.form.get('customer_phone', '')
            payment_method = request.form.get('payment_method', 'CASH')
            notes = request.form.get('notes', '')
            
            # Get sale items from JSON
            items_json = request.form.get('items', '[]')
            items = json.loads(items_json)
            
            if not items:
                flash('Please add at least one item to the sale', 'error')
                return redirect(url_for('new_sale'))
            
            # Calculate totals
            total_amount = sum(item['total_price'] for item in items)
            discount_amount = float(request.form.get('discount_amount', 0))
            tax_amount = float(request.form.get('tax_amount', 0))
            final_amount = total_amount - discount_amount + tax_amount
            
            # Generate sale number
            sale_number = f"SALE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create sale data
            sale_data = {
                'sale_number': sale_number,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'total_amount': total_amount,
                'discount_amount': discount_amount,
                'tax_amount': tax_amount,
                'final_amount': final_amount,
                'payment_method': payment_method,
                'notes': notes
            }
            
            # Create sale
            sale_id = db.create_sale(sale_data, items)
            
            flash(f'Sale completed successfully! Sale Number: {sale_number}', 'success')
            return redirect(url_for('sales'))
            
        except Exception as e:
            flash(f'Error creating sale: {str(e)}', 'error')
    
    # Load products for sale
    products = db.get_all_products()
    # Only show products with stock
    available_products = [p for p in products if p['current_stock'] > 0]
    
    return render_template('new_sale.html', 
                         products=available_products,
                         page_title="New Sale")

@app.route('/reports')
def reports():
    """Reports and analytics page"""
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get sales report
        report = db.get_sales_report(start_date.isoformat(), end_date.isoformat())
        
        # Get low stock products
        low_stock_products = db.get_low_stock_products()
        
        return render_template('reports.html', 
                             report=report,
                             low_stock_products=low_stock_products,
                             start_date=start_date,
                             end_date=end_date,
                             page_title="Reports")
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('reports.html', 
                             report={'summary': {}, 'daily_sales': [], 'top_products': []},
                             low_stock_products=[],
                             start_date=datetime.now().date() - timedelta(days=30),
                             end_date=datetime.now().date(),
                             page_title="Reports")

@app.route('/categories')
def categories():
    """Categories management page"""
    try:
        categories = db.get_all_categories()
        return render_template('categories.html', 
                             categories=categories,
                             page_title="Categories")
    except Exception as e:
        flash(f'Error loading categories: {str(e)}', 'error')
        return render_template('categories.html', 
                             categories=[],
                             page_title="Categories")

@app.route('/categories/add', methods=['POST'])
def add_category():
    """Add new category"""
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Category name is required', 'error')
        else:
            category_id = db.add_category(name, description)
            flash(f'Category "{name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))

@app.route('/suppliers')
def suppliers():
    """Suppliers management page"""
    try:
        suppliers = db.get_all_suppliers()
        return render_template('suppliers.html', 
                             suppliers=suppliers,
                             page_title="Suppliers")
    except Exception as e:
        flash(f'Error loading suppliers: {str(e)}', 'error')
        return render_template('suppliers.html', 
                             suppliers=[],
                             page_title="Suppliers")

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    """Add new supplier"""
    try:
        supplier_data = {
            'name': request.form.get('name'),
            'contact_person': request.form.get('contact_person', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'address': request.form.get('address', '')
        }
        
        if not supplier_data['name']:
            flash('Supplier name is required', 'error')
        else:
            supplier_id = db.add_supplier(supplier_data)
            flash(f'Supplier "{supplier_data["name"]}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding supplier: {str(e)}', 'error')
    
    return redirect(url_for('suppliers'))

@app.route('/alerts')
def alerts():
    """Alerts page"""
    try:
        alerts = db.get_unread_alerts()
        return render_template('alerts.html', 
                             alerts=alerts,
                             page_title="Alerts")
    except Exception as e:
        flash(f'Error loading alerts: {str(e)}', 'error')
        return render_template('alerts.html', 
                             alerts=[],
                             page_title="Alerts")

@app.route('/alerts/<int:alert_id>/mark_read', methods=['POST'])
def mark_alert_read(alert_id):
    """Mark alert as read"""
    try:
        db.mark_alert_read(alert_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# API Routes for AJAX calls
@app.route('/api/products')
def api_products():
    """API endpoint for products"""
    try:
        products = db.get_all_products()
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product/<int:product_id>')
def api_product(product_id):
    """API endpoint for single product"""
    try:
        product = db.get_product_by_id(product_id)
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard_stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts_count')
def api_alerts_count():
    """API endpoint for alerts count"""
    try:
        alerts = db.get_unread_alerts()
        return jsonify({'count': len(alerts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)