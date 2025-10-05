import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from datetime import datetime
from tkcalendar import DateEntry
import csv



conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

conn.commit()



root = Tk()
root.title("Personal Expense Tracker")
root.geometry("600x500")

title_label = Label(root, text="My Finance Tracker", font=("Arial", 24, "bold"), fg="#4CAF50")
title_label.pack(pady=10)


frame = Frame(root)
frame.pack(pady=20)

# Labels and Entries with bigger size
label_font = ("Arial", 12, "bold")  # bigger and bold labels
entry_width = 25  # wider input boxes

# Amount
Label(frame, text="Amount:", font=label_font).grid(row=0, column=0, padx=10, pady=10, sticky=E)
amount_entry = Entry(frame, width=entry_width, font=("Arial", 12))
amount_entry.grid(row=0, column=1, padx=10, pady=10)

# Description
Label(frame, text="Description:", font=label_font).grid(row=0, column=2, padx=10, pady=10, sticky=E)
description_entry = Entry(frame, width=entry_width+5, font=("Arial", 12))
description_entry.grid(row=0, column=3, padx=10, pady=10)

# Category
Label(frame, text="Category:", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky=E)
category_entry = Entry(frame, width=entry_width, font=("Arial", 12))
category_entry.grid(row=1, column=1, padx=10, pady=10)

# Date
Label(frame, text="Date:", font=label_font).grid(row=1, column=2, padx=10, pady=10, sticky=E)
date_entry = DateEntry(
    frame,
    width=entry_width-5,
    font=("Arial", 12),
    background='darkblue',
    foreground='white',
    borderwidth=2,
    date_pattern='yyyy-mm-dd'
)
date_entry.grid(row=1, column=3, padx=10, pady=10)



def add_expense():
    amount = float(amount_entry.get())
    description = description_entry.get()
    category = category_entry.get()
    date = date_entry.get()

    if not amount or not category or not date:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return
    
    try:
        float(amount)
    except:
        messagebox.showerror("Input Error", "Amount must be a number.")
        return
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except:
        messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
        return

    cursor.execute("INSERT INTO expenses (amount, description, category, date) VALUES (?, ?, ?, ?)",
                   (amount, description, category, date))
    conn.commit()
    messagebox.showinfo("Success", "Expense added successfully.")
    view_expenses()


table_frame = Frame(root)
columns = ('ID', 'Amount', 'Description', 'Category', 'Date')
tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

scrollbar = Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180, anchor=CENTER)

def tag_rows():
    for i, item in enumerate(tree.get_children()):
        if i % 2 == 0:
            tree.item(item, tags=('evenrow',))
        else:
            tree.item(item, tags=('oddrow',))

tree.tag_configure('evenrow', background='lightblue')
tree.tag_configure('oddrow', background='white')


def view_expenses():

    if table_frame.winfo_ismapped():  
        table_frame.pack_forget()     
        return
    else:
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', END, values=row)

        table_frame.pack(pady=10)
        tree.pack()


for i in range(6):
    frame.columnconfigure(i, weight=1)

Button(frame, text="Add Expense", command=add_expense).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
Button(frame, text="View Expenses", command=view_expenses).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
Button(frame, text="Update Selected", command=lambda: update_expense()).grid(row=3, column=2, padx=5, pady=5, sticky="ew")
Button(frame, text="Delete Selected", command=lambda: delete_expense()).grid(row=3, column=3, padx=5, pady=5, sticky="ew")
Button(frame, text="Show Summary", command=lambda: show_summary()).grid(row=3, column=4, padx=5, pady=5, sticky="ew")
Button(frame, text="Export CSV", command=lambda: export_csv()).grid(row=3, column=5, padx=5, pady=5, sticky="ew")


def update_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Selection Error", "Please select an expense to update.")
        return
    
    item = tree.item(selected[0])
    expense_id = item['values'][0]


    amount = amount_entry.get()
    date = date_entry.get()
    description = description_entry.get()
    category = category_entry.get()

    if not amount or not category or not date:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return
    
    try:
        float(amount)
    except:
        messagebox.showerror("Input Error", "Amount must be a number.")
        return
    
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except:
        messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
        return

    cursor.execute("UPDATE expenses SET amount=?, description=?, category=?, date=? WHERE id=?",
                   (amount, description, category, date, expense_id))
    conn.commit()
    messagebox.showinfo("Success", "Expense updated successfully.")
    view_expenses()


def delete_expense():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select an expense to delete.")
            return
        
        item = tree.item(selected[0])
        expense_id = item['values'][0]

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            messagebox.showinfo("Success", "Expense deleted successfully.")
            view_expenses()


def export_csv():
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    with open("expenses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['ID','Amount','Description','Category','Date'])
        writer.writerows(rows)
    messagebox.showinfo("Exported", "Expenses exported to expenses.csv")




def show_summary():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_data = cursor.fetchall()

    cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
    date_data = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0


    summary_window = Toplevel(root)
    summary_window.title("Expense Summary")
    Label(summary_window, text=f"Total Expenses: ${total:.2f}", font=("Arial", 16)).pack(pady=10)

    if category_data:
        categories, amounts = zip(*category_data)
        plt.figure(figsize=(6,4))
        plt.bar(categories, amounts, color='skyblue')
        plt.title("Expenses by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount")
        plt.show()

    if date_data:
        dates, amounts = zip(*date_data)
        plt.figure(figsize=(6,4))
        plt.plot(dates, amounts, marker='o',color='orange')
        plt.title("Expenses Over Time")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

root.mainloop()