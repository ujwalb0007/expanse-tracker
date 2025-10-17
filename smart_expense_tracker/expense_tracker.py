import csv
import os
from datetime import datetime
from tabulate import tabulate

FILE_NAME = "expenses.csv"

def init_file():
    """Initialize CSV file if it doesn't exist."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Description", "Amount"])
        print("✅ Expense file created.\n")

def add_expense():
    """Add a new expense."""
    date = datetime.now().strftime("%Y-%m-%d")
    category = input("Enter category (Food/Travel/Bills/etc): ").title()
    desc = input("Enter description: ")
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("❌ Invalid amount!")
        return

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, category, desc, amount])
    print("✅ Expense added successfully!\n")

def view_expenses():
    """View all expenses."""
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        data = list(reader)
    if len(data) <= 1:
        print("⚠️ No expenses recorded yet.\n")
        return
    print(tabulate(data[1:], headers=data[0], tablefmt="fancy_grid"))

def delete_expense():
    """Delete an expense by row number."""
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        data = list(reader)
    if len(data) <= 1:
        print("⚠️ No data to delete.\n")
        return

    view_expenses()
    try:
        idx = int(input("Enter row number to delete (starting from 1): "))
        if idx < 1 or idx > len(data) - 1:
            raise IndexError
        del data[idx]
        with open(FILE_NAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print("🗑️ Expense deleted successfully!\n")
    except (ValueError, IndexError):
        print("❌ Invalid row number.\n")

def summary_by_month():
    """Summarize expenses by month."""
    with open(FILE_NAME, "r") as file:
        reader = csv.DictReader(file)
        monthly = {}
        for row in reader:
            month = row["Date"][:7]
            monthly[month] = monthly.get(month, 0) + float(row["Amount"])

    if not monthly:
        print("⚠️ No expense data.\n")
        return
    print(tabulate(monthly.items(), headers=["Month", "Total Expense"], tablefmt="fancy_grid"))

def main():
    """Main CLI menu."""
    init_file()
    while True:
        print("\n==== 💰 Smart Expense Tracker ====")
        print("1️⃣  Add Expense")
        print("2️⃣  View Expenses")
        print("3️⃣  Delete Expense")
        print("4️⃣  Monthly Summary")
        print("5️⃣  Exit")

        choice = input("\nEnter choice: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            summary_by_month()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Try again.")

if __name__ == "__main__":
    main()
