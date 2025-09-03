import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import threading
from database import InventoryDatabase
from typing import Dict, List

class InventoryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.db = InventoryDatabase()
        
        # Variables
        self.current_view = tk.StringVar(value="dashboard")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Setup UI
        self.setup_styles()
        self.create_main_layout()
        self.show_dashboard()
        
        # Auto-refresh alerts every 30 seconds
        self.auto_refresh_alerts()
    
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Success.TLabel', foreground='#28a745', background='#f0f0f0')
        style.configure('Warning.TLabel', foreground='#ffc107', background='#f0f0f0')
        style.configure('Danger.TLabel', foreground='#dc3545', background='#f0f0f0')
        style.configure('Primary.TButton', background='#007bff')
        style.configure('Success.TButton', background='#28a745')
        style.configure('Warning.TButton', background='#ffc107')
        style.configure('Danger.TButton', background='#dc3545')
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create main content area
        self.create_content_area(main_container)
        
        # Create status bar
        self.create_status_bar()
    
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(sidebar, text="Inventory Manager", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", "dashboard", self.show_dashboard),
            ("📦 Products", "products", self.show_products),
            ("🛒 Sales", "sales", self.show_sales),
            ("📈 Reports", "reports", self.show_reports),
            ("🏷️ Categories", "categories", self.show_categories),
            ("🏢 Suppliers", "suppliers", self.show_suppliers),
            ("⚠️ Alerts", "alerts", self.show_alerts),
            ("⚙️ Settings", "settings", self.show_settings)
        ]
        
        self.nav_buttons = {}
        for text, view, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text, command=command, width=25)
            btn.pack(pady=2, padx=5, fill=tk.X)
            self.nav_buttons[view] = btn
        
        # Alert indicator
        self.alert_indicator = ttk.Label(sidebar, text="", foreground='red', font=('Arial', 10, 'bold'))
        self.alert_indicator.pack(pady=(10, 0))
        
        # Update alert count
        self.update_alert_indicator()
    
    def create_content_area(self, parent):
        """Create main content area"""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Current time
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        self.update_time()
    
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_alert_indicator(self):
        """Update alert indicator"""
        try:
            alerts = self.db.get_unread_alerts()
            count = len(alerts)
            if count > 0:
                self.alert_indicator.config(text=f"🔔 {count} Alert{'s' if count != 1 else ''}")
            else:
                self.alert_indicator.config(text="")
        except Exception as e:
            print(f"Error updating alerts: {e}")
    
    def auto_refresh_alerts(self):
        """Auto-refresh alerts every 30 seconds"""
        self.update_alert_indicator()
        self.root.after(30000, self.auto_refresh_alerts)
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        if hasattr(self, 'current_treeview'):
            self.filter_treeview()
    
    def filter_treeview(self):
        """Filter current treeview based on search"""
        search_term = self.search_var.get().lower()
        
        # Clear current items
        for item in self.current_treeview.get_children():
            self.current_treeview.delete(item)
        
        # Re-populate with filtered data
        if hasattr(self, 'current_data'):
            for item in self.current_data:
                # Check if search term matches any field
                match = False
                for value in item.values():
                    if search_term in str(value).lower():
                        match = True
                        break
                
                if match or not search_term:
                    self.insert_treeview_item(item)
    
    # Dashboard View
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_content()
        self.current_view.set("dashboard")
        
        # Title
        title = ttk.Label(self.content_frame, text="📊 Dashboard", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Get dashboard stats
        try:
            stats = self.db.get_dashboard_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard: {e}")
            return
        
        # Create stats cards
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Row 1: Inventory Stats
        row1 = ttk.Frame(stats_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        self.create_stat_card(row1, "Total Products", stats['total_products'], "📦", "info")
        self.create_stat_card(row1, "Low Stock", stats['low_stock_count'], "⚠️", "warning")
        self.create_stat_card(row1, "Out of Stock", stats['out_of_stock_count'], "❌", "danger")
        self.create_stat_card(row1, "Inventory Value", f"${stats['inventory_value']:,.2f}", "💰", "success")
        
        # Row 2: Sales Stats
        row2 = ttk.Frame(stats_frame)
        row2.pack(fill=tk.X)
        
        self.create_stat_card(row2, "Today's Sales", stats['today_sales_count'], "🛒", "info")
        self.create_stat_card(row2, "Today's Revenue", f"${stats['today_sales_amount']:,.2f}", "💵", "success")
        self.create_stat_card(row2, "Month Sales", stats['month_sales_count'], "📈", "info")
        self.create_stat_card(row2, "Month Revenue", f"${stats['month_sales_amount']:,.2f}", "💰", "success")
        
        # Recent alerts
        self.create_alerts_section()
        
        # Quick actions
        self.create_quick_actions()
        
        self.update_status("Dashboard loaded")
    
    def create_stat_card(self, parent, title, value, icon, style_type):
        """Create a statistics card"""
        card = ttk.Frame(parent, relief='raised', borderwidth=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Icon and title
        header = ttk.Frame(card)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        icon_label = ttk.Label(header, text=icon, font=('Arial', 16))
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(header, text=title, font=('Arial', 10))
        title_label.pack(side=tk.RIGHT)
        
        # Value
        style_map = {
            'info': 'TLabel',
            'success': 'Success.TLabel',
            'warning': 'Warning.TLabel',
            'danger': 'Danger.TLabel'
        }
        
        value_label = ttk.Label(card, text=str(value), font=('Arial', 18, 'bold'), 
                               style=style_map.get(style_type, 'TLabel'))
        value_label.pack(pady=(0, 10))
    
    def create_alerts_section(self):
        """Create recent alerts section"""
        alerts_frame = ttk.LabelFrame(self.content_frame, text="Recent Alerts", padding=10)
        alerts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Alerts listbox
        alerts_list = tk.Listbox(alerts_frame, height=6)
        alerts_list.pack(fill=tk.BOTH, expand=True)
        
        # Load recent alerts
        try:
            alerts = self.db.get_unread_alerts()[:10]  # Show only first 10
            for alert in alerts:
                alerts_list.insert(tk.END, f"{alert['alert_type']}: {alert['message']}")
            
            if not alerts:
                alerts_list.insert(tk.END, "No alerts - All good! ✅")
        except Exception as e:
            alerts_list.insert(tk.END, f"Error loading alerts: {e}")
    
    def create_quick_actions(self):
        """Create quick actions section"""
        actions_frame = ttk.LabelFrame(self.content_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X)
        
        # Action buttons
        ttk.Button(actions_frame, text="➕ Add Product", command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="🛒 New Sale", command=self.new_sale_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📊 View Reports", command=self.show_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="⚠️ Check Alerts", command=self.show_alerts).pack(side=tk.LEFT, padx=5)
    
    # Products View
    def show_products(self):
        """Show products view"""
        self.clear_content()
        self.current_view.set("products")
        
        # Title and search
        header = ttk.Frame(self.content_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header, text="📦 Products", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Search box
        search_frame = ttk.Frame(header)
        search_frame.pack(side=tk.RIGHT)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = ttk.Frame(self.content_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="➕ Add Product", command=self.add_product_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="✏️ Edit Product", command=self.edit_product_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📊 Update Stock", command=self.update_stock_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_products).pack(side=tk.LEFT, padx=(0, 5))
        
        # Products table
        self.create_products_table()
        self.refresh_products()
        
        self.update_status("Products view loaded")
    
    def create_products_table(self):
        """Create products table"""
        # Create treeview with scrollbars
        table_frame = ttk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Name', 'SKU', 'Category', 'Supplier', 'Stock', 'Min Stock', 'Price', 'Status')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        column_widths = {'ID': 50, 'Name': 200, 'SKU': 100, 'Category': 120, 'Supplier': 120, 
                        'Stock': 80, 'Min Stock': 80, 'Price': 100, 'Status': 100}
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.products_tree.bind('<Double-1>', lambda e: self.edit_product_dialog())
        
        # Set current treeview for search
        self.current_treeview = self.products_tree
    
    def refresh_products(self):
        """Refresh products table"""
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)
            
            # Load products
            products = self.db.get_all_products()
            self.current_data = products
            
            for product in products:
                # Determine status
                if product['current_stock'] == 0:
                    status = "Out of Stock"
                elif product['current_stock'] <= product['minimum_stock']:
                    status = "Critical"
                elif product['current_stock'] <= product['reorder_point']:
                    status = "Low Stock"
                else:
                    status = "In Stock"
                
                # Insert item
                item_id = self.products_tree.insert('', tk.END, values=(
                    product['id'],
                    product['name'],
                    product['sku'],
                    product['category_name'] or 'N/A',
                    product['supplier_name'] or 'N/A',
                    product['current_stock'],
                    product['minimum_stock'],
                    f"${product['unit_price']:.2f}",
                    status
                ))
                
                # Color code based on stock status
                if status == "Out of Stock":
                    self.products_tree.set(item_id, 'Status', '❌ Out of Stock')
                elif status == "Critical":
                    self.products_tree.set(item_id, 'Status', '🔴 Critical')
                elif status == "Low Stock":
                    self.products_tree.set(item_id, 'Status', '🟡 Low Stock')
                else:
                    self.products_tree.set(item_id, 'Status', '✅ In Stock')
            
            self.update_status(f"Loaded {len(products)} products")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")
    
    def insert_treeview_item(self, product):
        """Insert item into products treeview"""
        # Determine status
        if product['current_stock'] == 0:
            status = "❌ Out of Stock"
        elif product['current_stock'] <= product['minimum_stock']:
            status = "🔴 Critical"
        elif product['current_stock'] <= product['reorder_point']:
            status = "🟡 Low Stock"
        else:
            status = "✅ In Stock"
        
        self.products_tree.insert('', tk.END, values=(
            product['id'],
            product['name'],
            product['sku'],
            product['category_name'] or 'N/A',
            product['supplier_name'] or 'N/A',
            product['current_stock'],
            product['minimum_stock'],
            f"${product['unit_price']:.2f}",
            status
        ))
    
    # Dialog methods
    def add_product_dialog(self):
        """Show add product dialog"""
        dialog = ProductDialog(self.root, self.db)
        if dialog.result:
            self.refresh_products()
            self.update_status("Product added successfully")
    
    def edit_product_dialog(self):
        """Show edit product dialog"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        dialog = ProductDialog(self.root, self.db, product_id)
        if dialog.result:
            self.refresh_products()
            self.update_status("Product updated successfully")
    
    def update_stock_dialog(self):
        """Show update stock dialog"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to update stock")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        current_stock = item['values'][5]
        
        dialog = StockUpdateDialog(self.root, self.db, product_id, product_name, current_stock)
        if dialog.result:
            self.refresh_products()
            self.update_status("Stock updated successfully")
    
    def new_sale_dialog(self):
        """Show new sale dialog"""
        dialog = SaleDialog(self.root, self.db)
        if dialog.result:
            self.update_status("Sale completed successfully")
    
    # Other view methods (simplified for brevity)
    def show_sales(self):
        """Show sales view"""
        self.clear_content()
        self.current_view.set("sales")
        ttk.Label(self.content_frame, text="🛒 Sales Management", style='Title.TLabel').pack(pady=20)
        ttk.Label(self.content_frame, text="Sales management features coming soon...").pack()
    
    def show_reports(self):
        """Show reports view"""
        self.clear_content()
        self.current_view.set("reports")
        ttk.Label(self.content_frame, text="📈 Reports & Analytics", style='Title.TLabel').pack(pady=20)
        ttk.Label(self.content_frame, text="Detailed reports coming soon...").pack()
    
    def show_categories(self):
        """Show categories view"""
        self.clear_content()
        self.current_view.set("categories")
        ttk.Label(self.content_frame, text="🏷️ Categories Management", style='Title.TLabel').pack(pady=20)
        ttk.Label(self.content_frame, text="Categories management coming soon...").pack()
    
    def show_suppliers(self):
        """Show suppliers view"""
        self.clear_content()
        self.current_view.set("suppliers")
        ttk.Label(self.content_frame, text="🏢 Suppliers Management", style='Title.TLabel').pack(pady=20)
        ttk.Label(self.content_frame, text="Suppliers management coming soon...").pack()
    
    def show_alerts(self):
        """Show alerts view"""
        self.clear_content()
        self.current_view.set("alerts")
        
        ttk.Label(self.content_frame, text="⚠️ System Alerts", style='Title.TLabel').pack(pady=(0, 20))
        
        # Alerts list
        alerts_frame = ttk.Frame(self.content_frame)
        alerts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create alerts listbox
        alerts_listbox = tk.Listbox(alerts_frame, font=('Arial', 10))
        alerts_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load alerts
        try:
            alerts = self.db.get_unread_alerts()
            for alert in alerts:
                alerts_listbox.insert(tk.END, f"[{alert['alert_type']}] {alert['message']}")
            
            if not alerts:
                alerts_listbox.insert(tk.END, "✅ No alerts - Everything looks good!")
        except Exception as e:
            alerts_listbox.insert(tk.END, f"❌ Error loading alerts: {e}")
        
        self.update_status("Alerts view loaded")
    
    def show_settings(self):
        """Show settings view"""
        self.clear_content()
        self.current_view.set("settings")
        ttk.Label(self.content_frame, text="⚙️ System Settings", style='Title.TLabel').pack(pady=20)
        ttk.Label(self.content_frame, text="Settings panel coming soon...").pack()


# Dialog Classes
class ProductDialog:
    def __init__(self, parent, db, product_id=None):
        self.db = db
        self.product_id = product_id
        self.result = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Product" if product_id is None else "Edit Product")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_form()
        
        if product_id:
            self.load_product_data()
    
    def create_form(self):
        """Create product form"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        fields = [
            ("Product Name:", "name"),
            ("SKU:", "sku"),
            ("Description:", "description"),
            ("Unit Price ($):", "unit_price"),
            ("Cost Price ($):", "cost_price"),
            ("Current Stock:", "current_stock"),
            ("Minimum Stock:", "minimum_stock"),
            ("Maximum Stock:", "maximum_stock"),
            ("Reorder Point:", "reorder_point"),
            ("Location:", "location"),
            ("Barcode:", "barcode")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            ttk.Label(main_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if field_name == "description":
                entry = tk.Text(main_frame, height=3, width=40)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            else:
                entry = ttk.Entry(main_frame, width=40)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            
            self.entries[field_name] = entry
        
        # Category dropdown
        ttk.Label(main_frame, text="Category:").grid(row=len(fields), column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=37)
        self.category_combo.grid(row=len(fields), column=1, sticky=tk.W, pady=5)
        
        # Supplier dropdown
        ttk.Label(main_frame, text="Supplier:").grid(row=len(fields)+1, column=0, sticky=tk.W, pady=5)
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(main_frame, textvariable=self.supplier_var, width=37)
        self.supplier_combo.grid(row=len(fields)+1, column=1, sticky=tk.W, pady=5)
        
        # Load categories and suppliers
        self.load_categories_and_suppliers()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_categories_and_suppliers(self):
        """Load categories and suppliers for dropdowns"""
        try:
            categories = self.db.get_all_categories()
            category_names = [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            
            suppliers = self.db.get_all_suppliers()
            supplier_names = [sup['name'] for sup in suppliers]
            self.supplier_combo['values'] = supplier_names
            
            # Store ID mappings
            self.category_map = {cat['name']: cat['id'] for cat in categories}
            self.supplier_map = {sup['name']: sup['id'] for sup in suppliers}
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories/suppliers: {e}")
    
    def load_product_data(self):
        """Load existing product data for editing"""
        try:
            product = self.db.get_product_by_id(self.product_id)
            if product:
                self.entries['name'].insert(0, product['name'])
                self.entries['sku'].insert(0, product['sku'])
                self.entries['description'].insert('1.0', product['description'] or '')
                self.entries['unit_price'].insert(0, str(product['unit_price']))
                self.entries['cost_price'].insert(0, str(product['cost_price']))
                self.entries['current_stock'].insert(0, str(product['current_stock']))
                self.entries['minimum_stock'].insert(0, str(product['minimum_stock']))
                self.entries['maximum_stock'].insert(0, str(product['maximum_stock']))
                self.entries['reorder_point'].insert(0, str(product['reorder_point']))
                self.entries['location'].insert(0, product['location'] or '')
                self.entries['barcode'].insert(0, product['barcode'] or '')
                
                # Set category and supplier
                if product['category_name']:
                    self.category_var.set(product['category_name'])
                if product['supplier_name']:
                    self.supplier_var.set(product['supplier_name'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product data: {e}")
    
    def save_product(self):
        """Save product data"""
        try:
            # Validate required fields
            if not self.entries['name'].get().strip():
                messagebox.showerror("Error", "Product name is required")
                return
            
            if not self.entries['sku'].get().strip():
                messagebox.showerror("Error", "SKU is required")
                return
            
            # Get form data
            product_data = {
                'name': self.entries['name'].get().strip(),
                'sku': self.entries['sku'].get().strip(),
                'description': self.entries['description'].get('1.0', tk.END).strip(),
                'unit_price': float(self.entries['unit_price'].get() or 0),
                'cost_price': float(self.entries['cost_price'].get() or 0),
                'current_stock': int(self.entries['current_stock'].get() or 0),
                'minimum_stock': int(self.entries['minimum_stock'].get() or 10),
                'maximum_stock': int(self.entries['maximum_stock'].get() or 1000),
                'reorder_point': int(self.entries['reorder_point'].get() or 20),
                'location': self.entries['location'].get().strip(),
                'barcode': self.entries['barcode'].get().strip(),
                'category_id': self.category_map.get(self.category_var.get()),
                'supplier_id': self.supplier_map.get(self.supplier_var.get())
            }
            
            # Save product
            if self.product_id:
                # Update existing product (simplified - would need update method in database)
                messagebox.showinfo("Info", "Product update functionality needs to be implemented")
            else:
                # Add new product
                self.db.add_product(product_data)
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {e}")


class StockUpdateDialog:
    def __init__(self, parent, db, product_id, product_name, current_stock):
        self.db = db
        self.product_id = product_id
        self.result = False
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Stock")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.create_form(product_name, current_stock)
    
    def create_form(self, product_name, current_stock):
        """Create stock update form"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        ttk.Label(main_frame, text=f"Product: {product_name}", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        ttk.Label(main_frame, text=f"Current Stock: {current_stock}").pack(pady=(0, 20))
        
        # New stock entry
        ttk.Label(main_frame, text="New Stock Quantity:").pack(anchor=tk.W)
        self.stock_entry = ttk.Entry(main_frame, width=20, font=('Arial', 12))
        self.stock_entry.pack(pady=(5, 10))
        self.stock_entry.focus()
        
        # Movement type
        ttk.Label(main_frame, text="Movement Type:").pack(anchor=tk.W)
        self.movement_var = tk.StringVar(value="ADJUSTMENT")
        movement_frame = ttk.Frame(main_frame)
        movement_frame.pack(pady=(5, 10), fill=tk.X)
        
        ttk.Radiobutton(movement_frame, text="Stock Adjustment", variable=self.movement_var, value="ADJUSTMENT").pack(anchor=tk.W)
        ttk.Radiobutton(movement_frame, text="Stock In", variable=self.movement_var, value="IN").pack(anchor=tk.W)
        ttk.Radiobutton(movement_frame, text="Stock Out", variable=self.movement_var, value="OUT").pack(anchor=tk.W)
        
        # Notes
        ttk.Label(main_frame, text="Notes (optional):").pack(anchor=tk.W)
        self.notes_entry = tk.Text(main_frame, height=3, width=40)
        self.notes_entry.pack(pady=(5, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Update Stock", command=self.update_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_stock(self):
        """Update product stock"""
        try:
            new_stock = int(self.stock_entry.get())
            if new_stock < 0:
                messagebox.showerror("Error", "Stock quantity cannot be negative")
                return
            
            movement_type = self.movement_var.get()
            notes = self.notes_entry.get('1.0', tk.END).strip()
            
            # Update stock in database
            self.db.update_product_stock(self.product_id, new_stock, movement_type, notes)
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid stock quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {e}")


class SaleDialog:
    def __init__(self, parent, db):
        self.db = db
        self.result = False
        self.sale_items = []
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Sale")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_form()
    
    def create_form(self):
        """Create sale form"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer info
        customer_frame = ttk.LabelFrame(main_frame, text="Customer Information", padding=10)
        customer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.customer_name = ttk.Entry(customer_frame, width=30)
        self.customer_name.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(customer_frame, text="Email:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.customer_email = ttk.Entry(customer_frame, width=30)
        self.customer_email.grid(row=0, column=3, sticky=tk.W)
        
        # Sale items
        items_frame = ttk.LabelFrame(main_frame, text="Sale Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add item controls
        add_frame = ttk.Frame(items_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Product:").pack(side=tk.LEFT)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(add_frame, textvariable=self.product_var, width=30)
        self.product_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame, text="Qty:").pack(side=tk.LEFT, padx=(10, 0))
        self.qty_entry = ttk.Entry(add_frame, width=10)
        self.qty_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        
        # Load products
        self.load_products()
        
        # Items list
        self.items_tree = ttk.Treeview(items_frame, columns=('Product', 'Qty', 'Price', 'Total'), show='headings', height=8)
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        for col in ('Product', 'Qty', 'Price', 'Total'):
            self.items_tree.heading(col, text=col)
        
        # Total
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(total_frame, text="Total Amount:", font=('Arial', 12, 'bold')).pack(side=tk.RIGHT, padx=(0, 10))
        self.total_label = ttk.Label(total_frame, text="$0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Complete Sale", command=self.complete_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_products(self):
        """Load products for selection"""
        try:
            products = self.db.get_all_products()
            product_names = [f"{p['name']} (Stock: {p['current_stock']})" for p in products if p['current_stock'] > 0]
            self.product_combo['values'] = product_names
            
            # Store product mapping
            self.product_map = {f"{p['name']} (Stock: {p['current_stock']})": p for p in products if p['current_stock'] > 0}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")
    
    def add_item(self):
        """Add item to sale"""
        try:
            product_text = self.product_var.get()
            if not product_text:
                messagebox.showerror("Error", "Please select a product")
                return
            
            quantity = int(self.qty_entry.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            
            product = self.product_map[product_text]
            
            if quantity > product['current_stock']:
                messagebox.showerror("Error", f"Not enough stock. Available: {product['current_stock']}")
                return
            
            # Add to items list
            total_price = quantity * product['unit_price']
            self.items_tree.insert('', tk.END, values=(
                product['name'],
                quantity,
                f"${product['unit_price']:.2f}",
                f"${total_price:.2f}"
            ))
            
            # Store item data
            self.sale_items.append({
                'product_id': product['id'],
                'quantity': quantity,
                'unit_price': product['unit_price'],
                'total_price': total_price
            })
            
            # Update total
            self.update_total()
            
            # Clear inputs
            self.product_var.set('')
            self.qty_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
    
    def update_total(self):
        """Update total amount"""
        total = sum(item['total_price'] for item in self.sale_items)
        self.total_label.config(text=f"${total:.2f}")
    
    def complete_sale(self):
        """Complete the sale"""
        try:
            if not self.sale_items:
                messagebox.showerror("Error", "Please add at least one item")
                return
            
            # Generate sale number
            sale_number = f"SALE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Calculate totals
            total_amount = sum(item['total_price'] for item in self.sale_items)
            
            # Sale data
            sale_data = {
                'sale_number': sale_number,
                'customer_name': self.customer_name.get().strip() or 'Walk-in Customer',
                'customer_email': self.customer_email.get().strip(),
                'customer_phone': '',
                'total_amount': total_amount,
                'discount_amount': 0,
                'tax_amount': 0,
                'final_amount': total_amount,
                'payment_method': 'CASH',
                'notes': ''
            }
            
            # Create sale
            sale_id = self.db.create_sale(sale_data, self.sale_items)
            
            messagebox.showinfo("Success", f"Sale completed successfully!\nSale Number: {sale_number}")
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {e}")


def main():
    root = tk.Tk()
    app = InventoryManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()