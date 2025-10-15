import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
import csv

class AdvancedTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Task Manager Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize database
        self.init_database()
        
        # Start notification thread
        self.notification_thread = threading.Thread(target=self.check_notifications, daemon=True)
        self.notification_thread.start()
        
        self.create_widgets()
        self.load_tasks()
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('tasks_advanced.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'Medium',
                due_date TEXT,
                category TEXT DEFAULT 'General',
                status TEXT DEFAULT 'Pending',
                created_date TEXT,
                completed_date TEXT,
                estimated_time INTEGER DEFAULT 0,
                actual_time INTEGER DEFAULT 0,
                tags TEXT,
                reminder_sent BOOLEAN DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 Advanced Task Manager Pro", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="✏️ Add New Task", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_entry = ttk.Entry(input_frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.priority_combo = ttk.Combobox(input_frame, values=["High", "Medium", "Low"], width=12)
        self.priority_combo.set("Medium")
        self.priority_combo.grid(row=0, column=3, padx=(0, 15))
        
        # Row 2
        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.category_combo = ttk.Combobox(input_frame, values=["Work", "Personal", "Study", "Health", "Shopping"], width=22)
        self.category_combo.set("General")
        self.category_combo.grid(row=1, column=1, padx=(0, 15))
        
        ttk.Label(input_frame, text="Due Date:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        self.due_date_entry = ttk.Entry(input_frame, width=15)
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        self.due_date_entry.grid(row=1, column=3)
        
        # Row 3
        ttk.Label(input_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=2, column=1, columnspan=2, padx=(0, 15))
        
        ttk.Label(input_frame, text="Est. Hours:").grid(row=2, column=3, sticky=tk.W, padx=(0, 5))
        self.time_entry = ttk.Entry(input_frame, width=8)
        self.time_entry.grid(row=2, column=4)
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=5, pady=15)
        
        ttk.Button(button_frame, text="➕ Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.update_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ Complete", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="🔍 Filters & Actions", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_combo = ttk.Combobox(filter_frame, values=["All", "High Priority", "Medium Priority", "Low Priority", "Pending", "Completed", "Overdue"], width=15)
        self.filter_combo.set("All")
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Apply", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="📊 Analytics", command=self.show_analytics).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_frame, text="📤 Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="📥 Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)
        
        # Task list frame
        list_frame = ttk.LabelFrame(main_frame, text="📋 Task List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for task display
        columns = ("ID", "Title", "Priority", "Category", "Due Date", "Status", "Progress")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define column headings and widths
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="📝 Title")
        self.tree.heading("Priority", text="🔥 Priority")
        self.tree.heading("Category", text="📂 Category")
        self.tree.heading("Due Date", text="📅 Due Date")
        self.tree.heading("Status", text="✅ Status")
        self.tree.heading("Progress", text="⏳ Progress")
        
        for col in columns:
            self.tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_task(self):
        """Add new task to database"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Task title is required!")
            return
        
        description = self.desc_entry.get().strip()
        priority = self.priority_combo.get()
        category = self.category_combo.get()
        due_date = self.due_date_entry.get().strip()
        estimated_time = self.time_entry.get().strip() or "0"
        
        if due_date != "YYYY-MM-DD":
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
        else:
            due_date = ""
        
        try:
            estimated_time = int(estimated_time)
        except ValueError:
            estimated_time = 0
        
        self.cursor.execute('''
            INSERT INTO tasks (title, description, priority, due_date, category, 
                             created_date, estimated_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, priority, due_date, category, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"), estimated_time, "Pending"))
        
        self.conn.commit()
        self.clear_inputs()
        self.load_tasks()
        messagebox.showinfo("Success", f"Task '{title}' added successfully!")
    
    def load_tasks(self):
        """Load and display tasks"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.cursor.execute("SELECT * FROM tasks ORDER BY created_date DESC")
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            task_id, title, desc, priority, due_date, category, status, created, completed, est_time, actual_time, tags, reminder = task
            
            # Calculate progress
            if status == "Completed":
                progress = "✅ Done"
            elif due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    today = datetime.now()
                    if due < today:
                        progress = "⚠️ Overdue"
                    else:
                        days_left = (due - today).days
                        progress = f"⏳ {days_left} days"
                except:
                    progress = "❓ Unknown"
            else:
                progress = "🔄 Ongoing"
            
            # Priority emoji
            priority_display = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}[priority]
            status_display = {"Completed": "✅ Done", "Pending": "⏳ Pending"}[status]
            
            self.tree.insert("", tk.END, values=(
                task_id, title, priority_display, category, 
                due_date or "No deadline", status_display, progress
            ))
    
    def on_select(self, event):
        """Handle task selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            if values:
                task_id = values[0]
                self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = self.cursor.fetchone()
                if task:
                    self.title_entry.delete(0, tk.END)
                    self.title_entry.insert(0, task[1])
                    self.desc_entry.delete(0, tk.END)
                    self.desc_entry.insert(0, task[2] or "")
                    self.priority_combo.set(task[3])
                    self.category_combo.set(task[5])
                    self.due_date_entry.delete(0, tk.END)
                    self.due_date_entry.insert(0, task[4] or "YYYY-MM-DD")
                    self.time_entry.delete(0, tk.END)
                    self.time_entry.insert(0, str(task[9] or 0))
    
    def update_task(self):
        """Update selected task"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a task to update!")
            return
        
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        priority = self.priority_combo.get()
        category = self.category_combo.get()
        due_date = self.due_date_entry.get().strip()
        estimated_time = self.time_entry.get().strip() or "0"
        
        if due_date == "YYYY-MM-DD":
            due_date = ""
        
        self.cursor.execute('''
            UPDATE tasks SET title=?, description=?, priority=?, due_date=?, 
                           category=?, estimated_time=?
            WHERE id=?
        ''', (title, description, priority, due_date, category, int(estimated_time), task_id))
        
        self.conn.commit()
        self.load_tasks()
        messagebox.showinfo("Success", "Task updated successfully!")
    
    def delete_task(self):
        """Delete selected task"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a task to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            item = self.tree.item(selection[0])
            task_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            self.load_tasks()
            self.clear_inputs()
            messagebox.showinfo("Success", "Task deleted successfully!")
    
    def mark_complete(self):
        """Mark selected task as complete"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a task to mark complete!")
            return
        
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        
        self.cursor.execute('''
            UPDATE tasks SET status='Completed', completed_date=?
            WHERE id=?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
        
        self.conn.commit()
        self.load_tasks()
        messagebox.showinfo("Success", "Task marked as complete! 🎉")
    
    def apply_filter(self):
        """Apply selected filter"""
        filter_type = self.filter_combo.get()
        
        if filter_type == "All":
            self.load_tasks()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if filter_type == "High Priority":
            query = "SELECT * FROM tasks WHERE priority='High' ORDER BY created_date DESC"
        elif filter_type == "Medium Priority":
            query = "SELECT * FROM tasks WHERE priority='Medium' ORDER BY created_date DESC"
        elif filter_type == "Low Priority":
            query = "SELECT * FROM tasks WHERE priority='Low' ORDER BY created_date DESC"
        elif filter_type == "Pending":
            query = "SELECT * FROM tasks WHERE status='Pending' ORDER BY created_date DESC"
        elif filter_type == "Completed":
            query = "SELECT * FROM tasks WHERE status='Completed' ORDER BY created_date DESC"
        elif filter_type == "Overdue":
            today = datetime.now().strftime("%Y-%m-%d")
            query = f"SELECT * FROM tasks WHERE due_date < '{today}' AND status != 'Completed' ORDER BY due_date"
        
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
        
        for task in tasks:
            task_id, title, desc, priority, due_date, category, status, created, completed, est_time, actual_time, tags, reminder = task
            
            if status == "Completed":
                progress = "✅ Done"
            elif due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    today = datetime.now()
                    if due < today:
                        progress = "⚠️ Overdue"
                    else:
                        days_left = (due - today).days
                        progress = f"⏳ {days_left} days"
                except:
                    progress = "❓ Unknown"
            else:
                progress = "🔄 Ongoing"
            
            priority_display = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}[priority]
            status_display = {"Completed": "✅ Done", "Pending": "⏳ Pending"}[status]
            
            self.tree.insert("", tk.END, values=(
                task_id, title, priority_display, category, 
                due_date or "No deadline", status_display, progress
            ))
    
    def export_csv(self):
        """Export tasks to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filename:
            self.cursor.execute("SELECT * FROM tasks")
            tasks = self.cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Title', 'Description', 'Priority', 'Due Date', 
                               'Category', 'Status', 'Created Date', 'Completed Date', 
                               'Estimated Time', 'Actual Time'])
                writer.writerows(tasks)
            
            messagebox.showinfo("Success", f"📤 Tasks exported to {filename}")
    
    def import_csv(self):
        """Import tasks from CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    
                    imported = 0
                    for row in reader:
                        if len(row) >= 7:
                            self.cursor.execute('''
                                INSERT INTO tasks (title, description, priority, due_date, 
                                                 category, status, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (row[1], row[2], row[3], row[4], row[5], row[6], 
                                 row[7] if len(row) > 7 else datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            imported += 1
                
                self.conn.commit()
                self.load_tasks()
                messagebox.showinfo("Success", f"📥 {imported} tasks imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {str(e)}")
    
    def show_analytics(self):
        """Show task analytics dashboard"""
        # Get analytics data
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Completed'")
        completed_tasks = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='Pending'")
        pending_tasks = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date < date('now') AND status != 'Completed'")
        overdue_tasks = self.cursor.fetchone()[0]
        
        # Priority breakdown
        self.cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
        priority_data = dict(self.cursor.fetchall())
        
        # Category breakdown
        self.cursor.execute("SELECT category, COUNT(*) FROM tasks GROUP BY category")
        category_data = dict(self.cursor.fetchall())
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Show analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("📊 Task Analytics Dashboard")
        analytics_window.geometry("500x600")
        analytics_window.configure(bg="#f0f0f0")
        
        # Title
        ttk.Label(analytics_window, text="📊 Task Analytics Dashboard", 
                 font=("Arial", 16, "bold")).pack(pady=15)
        
        # Main stats frame
        stats_frame = ttk.LabelFrame(analytics_window, text="📈 Overview", padding=15)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(stats_frame, text=f"📋 Total Tasks: {total_tasks}", font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        ttk.Label(stats_frame, text=f"✅ Completed: {completed_tasks}", font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        ttk.Label(stats_frame, text=f"⏳ Pending: {pending_tasks}", font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        ttk.Label(stats_frame, text=f"⚠️ Overdue: {overdue_tasks}", font=("Arial", 12)).pack(anchor=tk.W, pady=3)
        ttk.Label(stats_frame, text=f"🎯 Completion Rate: {completion_rate:.1f}%", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=3)
        
        # Progress bar
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        ttk.Label(progress_frame, text="Progress:").pack(anchor=tk.W)
        progress_bar = ttk.Progressbar(progress_frame, length=400, value=completion_rate)
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Priority breakdown
        priority_frame = ttk.LabelFrame(analytics_window, text="🔥 Priority Breakdown", padding=15)
        priority_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for priority, count in priority_data.items():
            emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
            ttk.Label(priority_frame, text=f"{emoji} {priority}: {count} tasks", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
        
        # Category breakdown
        category_frame = ttk.LabelFrame(analytics_window, text="📂 Category Breakdown", padding=15)
        category_frame.pack(fill=tk.X, padx=20, pady=10)
        
        for category, count in category_data.items():
            ttk.Label(category_frame, text=f"📁 {category}: {count} tasks", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
        
        # Productivity tips
        tips_frame = ttk.LabelFrame(analytics_window, text="💡 Productivity Tips", padding=15)
        tips_frame.pack(fill=tk.X, padx=20, pady=10)
        
        if overdue_tasks > 0:
            ttk.Label(tips_frame, text="⚠️ Focus on overdue tasks first!", foreground="red").pack(anchor=tk.W)
        if completion_rate < 50:
            ttk.Label(tips_frame, text="💪 Break large tasks into smaller ones").pack(anchor=tk.W)
        if completion_rate > 80:
            ttk.Label(tips_frame, text="🎉 Great job! Keep up the momentum").pack(anchor=tk.W)
    
    def check_notifications(self):
        """Background notifications (simplified)"""
        while True:
            try:
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                
                self.cursor.execute('''
                    SELECT title FROM tasks 
                    WHERE due_date = ? AND status = 'Pending' AND reminder_sent = 0
                ''', (tomorrow,))
                
                due_tomorrow = self.cursor.fetchall()
                
                for task in due_tomorrow:
                    print(f"🔔 Reminder: '{task[0]}' is due tomorrow!")
                
                time.sleep(3600)  # Check every hour
            except Exception as e:
                time.sleep(3600)
    
    def clear_inputs(self):
        """Clear input fields"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.priority_combo.set("Medium")
        self.category_combo.set("General")
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        self.time_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = AdvancedTodoApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.conn.close(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
