import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class InventoryDatabase:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Suppliers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                category_id INTEGER,
                supplier_id INTEGER,
                description TEXT,
                unit_price REAL NOT NULL DEFAULT 0,
                cost_price REAL NOT NULL DEFAULT 0,
                current_stock INTEGER NOT NULL DEFAULT 0,
                minimum_stock INTEGER NOT NULL DEFAULT 10,
                maximum_stock INTEGER NOT NULL DEFAULT 1000,
                reorder_point INTEGER NOT NULL DEFAULT 20,
                location TEXT,
                barcode TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # Stock movements table (for tracking all inventory changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT', 'RETURN'
                quantity INTEGER NOT NULL,
                unit_price REAL,
                reference_number TEXT,
                notes TEXT,
                created_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                customer_phone TEXT,
                total_amount REAL NOT NULL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                final_amount REAL NOT NULL DEFAULT 0,
                payment_method TEXT DEFAULT 'CASH',
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Sale items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Purchase orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT UNIQUE NOT NULL,
                supplier_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_date DATE,
                status TEXT DEFAULT 'PENDING', -- PENDING, RECEIVED, CANCELLED
                total_amount REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # Purchase order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity_ordered INTEGER NOT NULL,
                quantity_received INTEGER DEFAULT 0,
                unit_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                FOREIGN KEY (po_id) REFERENCES purchase_orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL, -- 'LOW_STOCK', 'OUT_OF_STOCK', 'OVERSTOCK'
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert sample data if tables are empty
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data for demonstration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample categories
        categories = [
            ("Electronics", "Electronic devices and components"),
            ("Clothing", "Apparel and accessories"),
            ("Books", "Books and educational materials"),
            ("Home & Garden", "Home improvement and gardening supplies"),
            ("Sports", "Sports equipment and accessories")
        ]
        
        cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories)
        
        # Sample suppliers
        suppliers = [
            ("TechCorp Ltd", "John Smith", "john@techcorp.com", "+1-555-0101", "123 Tech Street, Silicon Valley"),
            ("Fashion Hub", "Sarah Johnson", "sarah@fashionhub.com", "+1-555-0102", "456 Fashion Ave, New York"),
            ("BookWorld", "Mike Wilson", "mike@bookworld.com", "+1-555-0103", "789 Library Lane, Boston"),
            ("GreenThumb Supplies", "Lisa Brown", "lisa@greenthumb.com", "+1-555-0104", "321 Garden Road, Portland"),
            ("SportZone", "David Lee", "david@sportzone.com", "+1-555-0105", "654 Athletic Blvd, Denver")
        ]
        
        cursor.executemany("""
            INSERT INTO suppliers (name, contact_person, email, phone, address) 
            VALUES (?, ?, ?, ?, ?)
        """, suppliers)
        
        # Sample products
        products = [
            ("Wireless Headphones", "WH-001", 1, 1, "High-quality wireless headphones", 99.99, 45.00, 50, 10, 200, 15, "A1-B2", "123456789012"),
            ("Bluetooth Speaker", "BS-002", 1, 1, "Portable Bluetooth speaker", 79.99, 35.00, 30, 5, 150, 10, "A1-B3", "123456789013"),
            ("Men's T-Shirt", "MT-003", 2, 2, "Cotton t-shirt for men", 24.99, 12.00, 100, 20, 500, 30, "B2-C1", "123456789014"),
            ("Women's Jeans", "WJ-004", 2, 2, "Denim jeans for women", 59.99, 28.00, 75, 15, 300, 25, "B2-C2", "123456789015"),
            ("Python Programming Book", "PB-005", 3, 3, "Learn Python programming", 39.99, 20.00, 25, 5, 100, 10, "C3-D1", "123456789016"),
            ("Garden Hose", "GH-006", 4, 4, "50ft garden hose", 34.99, 18.00, 40, 8, 120, 12, "D4-E1", "123456789017"),
            ("Tennis Racket", "TR-007", 5, 5, "Professional tennis racket", 129.99, 65.00, 20, 5, 80, 8, "E5-F1", "123456789018"),
            ("Yoga Mat", "YM-008", 5, 5, "Non-slip yoga mat", 29.99, 15.00, 60, 10, 200, 15, "E5-F2", "123456789019")
        ]
        
        cursor.executemany("""
            INSERT INTO products (name, sku, category_id, supplier_id, description, unit_price, cost_price, 
                                current_stock, minimum_stock, maximum_stock, reorder_point, location, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
        
        conn.commit()
        conn.close()
    
    # Product operations
    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO products (name, sku, category_id, supplier_id, description, unit_price, cost_price,
                                current_stock, minimum_stock, maximum_stock, reorder_point, location, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_data['name'], product_data['sku'], product_data['category_id'],
            product_data['supplier_id'], product_data['description'], product_data['unit_price'],
            product_data['cost_price'], product_data['current_stock'], product_data['minimum_stock'],
            product_data['maximum_stock'], product_data['reorder_point'], product_data['location'],
            product_data['barcode']
        ))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def get_all_products(self) -> List[Dict]:
        """Get all products with category and supplier info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.is_active = 1
            ORDER BY p.name
        """)
        
        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return products
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            product = dict(zip(columns, row))
        else:
            product = None
        
        conn.close()
        return product
    
    def update_product_stock(self, product_id: int, new_stock: int, movement_type: str = 'ADJUSTMENT', notes: str = ''):
        """Update product stock and record movement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current stock
        cursor.execute("SELECT current_stock FROM products WHERE id = ?", (product_id,))
        current_stock = cursor.fetchone()[0]
        
        # Calculate quantity change
        quantity_change = new_stock - current_stock
        
        # Update product stock
        cursor.execute("""
            UPDATE products 
            SET current_stock = ?, updated_date = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (new_stock, product_id))
        
        # Record stock movement
        cursor.execute("""
            INSERT INTO stock_movements (product_id, movement_type, quantity, notes, created_date)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (product_id, movement_type, quantity_change, notes))
        
        conn.commit()
        conn.close()
        
        # Check for alerts
        self.check_stock_alerts(product_id)
    
    def get_low_stock_products(self) -> List[Dict]:
        """Get products with stock below reorder point"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.current_stock <= p.reorder_point AND p.is_active = 1
            ORDER BY (p.current_stock - p.reorder_point) ASC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return products
    
    def check_stock_alerts(self, product_id: int):
        """Check and create stock alerts for a product"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get product info
        cursor.execute("""
            SELECT name, current_stock, minimum_stock, reorder_point, maximum_stock
            FROM products WHERE id = ?
        """, (product_id,))
        
        product = cursor.fetchone()
        if not product:
            conn.close()
            return
        
        name, current_stock, minimum_stock, reorder_point, maximum_stock = product
        
        # Clear existing unread alerts for this product
        cursor.execute("DELETE FROM alerts WHERE product_id = ? AND is_read = 0", (product_id,))
        
        # Check for different alert conditions
        if current_stock == 0:
            message = f"Product '{name}' is OUT OF STOCK!"
            cursor.execute("""
                INSERT INTO alerts (product_id, alert_type, message)
                VALUES (?, 'OUT_OF_STOCK', ?)
            """, (product_id, message))
        elif current_stock <= minimum_stock:
            message = f"Product '{name}' is critically low (Stock: {current_stock}, Min: {minimum_stock})"
            cursor.execute("""
                INSERT INTO alerts (product_id, alert_type, message)
                VALUES (?, 'LOW_STOCK', ?)
            """, (product_id, message))
        elif current_stock <= reorder_point:
            message = f"Product '{name}' needs reordering (Stock: {current_stock}, Reorder at: {reorder_point})"
            cursor.execute("""
                INSERT INTO alerts (product_id, alert_type, message)
                VALUES (?, 'LOW_STOCK', ?)
            """, (product_id, message))
        elif current_stock > maximum_stock:
            message = f"Product '{name}' is overstocked (Stock: {current_stock}, Max: {maximum_stock})"
            cursor.execute("""
                INSERT INTO alerts (product_id, alert_type, message)
                VALUES (?, 'OVERSTOCK', ?)
            """, (product_id, message))
        
        conn.commit()
        conn.close()
    
    # Sales operations
    def create_sale(self, sale_data: Dict, items: List[Dict]) -> int:
        """Create a new sale with items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create sale record
            cursor.execute("""
                INSERT INTO sales (sale_number, customer_name, customer_email, customer_phone,
                                 total_amount, discount_amount, tax_amount, final_amount, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_data['sale_number'], sale_data['customer_name'], sale_data['customer_email'],
                sale_data['customer_phone'], sale_data['total_amount'], sale_data['discount_amount'],
                sale_data['tax_amount'], sale_data['final_amount'], sale_data['payment_method'],
                sale_data['notes']
            ))
            
            sale_id = cursor.lastrowid
            
            # Add sale items and update stock
            for item in items:
                # Add sale item
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['product_id'], item['quantity'], item['unit_price'], item['total_price']))
                
                # Update product stock
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = current_stock - ?, updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (item['quantity'], item['product_id']))
                
                # Record stock movement
                cursor.execute("""
                    INSERT INTO stock_movements (product_id, movement_type, quantity, reference_number, notes)
                    VALUES (?, 'OUT', ?, ?, ?)
                """, (item['product_id'], -item['quantity'], sale_data['sale_number'], f"Sale to {sale_data['customer_name']}"))
                
                # Check for alerts
                self.check_stock_alerts(item['product_id'])
            
            conn.commit()
            return sale_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_sales_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get sales report for a date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build date filter
        date_filter = ""
        params = []
        if start_date and end_date:
            date_filter = "WHERE DATE(sale_date) BETWEEN ? AND ?"
            params = [start_date, end_date]
        elif start_date:
            date_filter = "WHERE DATE(sale_date) >= ?"
            params = [start_date]
        elif end_date:
            date_filter = "WHERE DATE(sale_date) <= ?"
            params = [end_date]
        
        # Get summary statistics
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_sales,
                SUM(final_amount) as total_revenue,
                AVG(final_amount) as avg_sale_amount,
                SUM(discount_amount) as total_discounts
            FROM sales {date_filter}
        """, params)
        
        summary = cursor.fetchone()
        
        # Get top selling products
        cursor.execute(f"""
            SELECT 
                p.name,
                SUM(si.quantity) as total_sold,
                SUM(si.total_price) as total_revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            {date_filter.replace('sale_date', 's.sale_date') if date_filter else ''}
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT 10
        """, params)
        
        top_products = cursor.fetchall()
        
        # Get daily sales
        cursor.execute(f"""
            SELECT 
                DATE(sale_date) as sale_date,
                COUNT(*) as sales_count,
                SUM(final_amount) as daily_revenue
            FROM sales {date_filter}
            GROUP BY DATE(sale_date)
            ORDER BY sale_date DESC
            LIMIT 30
        """, params)
        
        daily_sales = cursor.fetchall()
        
        conn.close()
        
        return {
            'summary': {
                'total_sales': summary[0] or 0,
                'total_revenue': summary[1] or 0,
                'avg_sale_amount': summary[2] or 0,
                'total_discounts': summary[3] or 0
            },
            'top_products': top_products,
            'daily_sales': daily_sales
        }
    
    # Category and Supplier operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        
        columns = [desc[0] for desc in cursor.description]
        categories = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_all_suppliers(self) -> List[Dict]:
        """Get all suppliers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        
        columns = [desc[0] for desc in cursor.description]
        suppliers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return suppliers
    
    def add_category(self, name: str, description: str = '') -> int:
        """Add a new category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        category_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return category_id
    
    def add_supplier(self, supplier_data: Dict) -> int:
        """Add a new supplier"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, (
            supplier_data['name'], supplier_data['contact_person'],
            supplier_data['email'], supplier_data['phone'], supplier_data['address']
        ))
        
        supplier_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return supplier_id
    
    # Alert operations
    def get_unread_alerts(self) -> List[Dict]:
        """Get all unread alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, p.name as product_name, p.sku
            FROM alerts a
            JOIN products p ON a.product_id = p.id
            WHERE a.is_read = 0
            ORDER BY a.created_date DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return alerts
    
    def mark_alert_read(self, alert_id: int):
        """Mark an alert as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
        
        conn.commit()
        conn.close()
    
    # Dashboard statistics
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total products
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        total_products = cursor.fetchone()[0]
        
        # Low stock products
        cursor.execute("SELECT COUNT(*) FROM products WHERE current_stock <= reorder_point AND is_active = 1")
        low_stock_count = cursor.fetchone()[0]
        
        # Out of stock products
        cursor.execute("SELECT COUNT(*) FROM products WHERE current_stock = 0 AND is_active = 1")
        out_of_stock_count = cursor.fetchone()[0]
        
        # Total inventory value
        cursor.execute("SELECT SUM(current_stock * cost_price) FROM products WHERE is_active = 1")
        inventory_value = cursor.fetchone()[0] or 0
        
        # Today's sales
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(final_amount), 0)
            FROM sales 
            WHERE DATE(sale_date) = DATE('now')
        """)
        today_sales = cursor.fetchone()
        
        # This month's sales
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(final_amount), 0)
            FROM sales 
            WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')
        """)
        month_sales = cursor.fetchone()
        
        # Unread alerts
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        unread_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'inventory_value': round(inventory_value, 2),
            'today_sales_count': today_sales[0],
            'today_sales_amount': round(today_sales[1], 2),
            'month_sales_count': month_sales[0],
            'month_sales_amount': round(month_sales[1], 2),
            'unread_alerts': unread_alerts
        }