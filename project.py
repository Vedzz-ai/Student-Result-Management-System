import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

# Database setup - saved in same folder as the script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll TEXT PRIMARY KEY,
    name TEXT,
    appliedmath INTEGER,
    python INTEGER,
    english INTEGER,
    computer INTEGER,
    datastructure INTEGER,
    total INTEGER,
    percentage REAL,
    grade TEXT
)
""")
conn.commit()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 75:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    else:
        return "Fail"

def clear_fields():
    entry_roll.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_appliedmaths.delete(0, tk.END)
    entry_python.delete(0, tk.END)
    entry_english.delete(0, tk.END)
    entry_computer.delete(0, tk.END)
    entry_datastructure.delete(0, tk.END)

def get_inputs():
    """Validate and return all input fields. Returns None on error."""
    roll          = entry_roll.get().strip()
    name          = entry_name.get().strip()
    appliedmaths  = entry_appliedmaths.get().strip()
    python        = entry_python.get().strip()
    english       = entry_english.get().strip()
    computer      = entry_computer.get().strip()
    datastructure = entry_datastructure.get().strip()

    if not all([roll, name, appliedmaths, python, english, computer, datastructure]):
        messagebox.showerror("Error", "All fields are required!")
        return None

    if not roll.isdigit():
        messagebox.showerror("Error", "Roll number must be numeric!")
        return None

    if not name.replace(" ", "").isalpha():
        messagebox.showerror("Error", "Name must contain only alphabets!")
        return None

    try:
        am = int(appliedmaths)
        py = int(python)
        en = int(english)
        co = int(computer)
        ds = int(datastructure)
        for mark in [am, py, en, co, ds]:
            if mark < 0 or mark > 100:
                raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Marks must be whole numbers between 0 and 100!")
        return None

    return roll, name, am, py, en, co, ds

def refresh_table():
    """Clear and reload all rows from DB into the Treeview."""
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("""
        SELECT roll, name, appliedmath, python, english, computer, datastructure, total, percentage, grade
        FROM students ORDER BY CAST(roll AS INTEGER)
    """)
    rows = cursor.fetchall()
    for i, row in enumerate(rows):
        formatted = list(row)
        formatted[8] = f"{row[8]:.2f}%"
        tag = "oddrow" if i % 2 == 0 else "evenrow"
        tree.insert("", tk.END, values=formatted, tags=(tag,))

def fill_fields(record):
    """Populate input boxes from a DB record tuple."""
    clear_fields()
    entry_roll.insert(0, record[0])
    entry_name.insert(0, record[1])
    entry_appliedmaths.insert(0, record[2])
    entry_python.insert(0, record[3])
    entry_english.insert(0, record[4])
    entry_computer.insert(0, record[5])
    entry_datastructure.insert(0, record[6])

# ─────────────────────────────────────────────
# CRUD OPERATIONS
# ─────────────────────────────────────────────

def add_student():
    data = get_inputs()
    if data is None:
        return
    roll, name, am, py, en, co, ds = data

    total      = am + py + en + co + ds
    percentage = total / 5
    grade      = calculate_grade(percentage)

    try:
        cursor.execute(
            """INSERT INTO students
               (roll, name, appliedmath, python, english, computer, datastructure, total, percentage, grade)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (roll, name, am, py, en, co, ds, total, round(percentage, 2), grade)
        )
        conn.commit()
        messagebox.showinfo(
            "Student Added ✅",
            f"Name       : {name}\n"
            f"Total Marks: {total} / 500\n"
            f"Percentage : {percentage:.2f}%\n"
            f"Grade      : {grade}"
        )
        clear_fields()
        refresh_table()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Roll number {roll} already exists!")

def search_student():
    roll = entry_roll.get().strip()
    if not roll:
        messagebox.showerror("Error", "Enter a Roll Number to search!")
        return

    cursor.execute("""
        SELECT roll, name, appliedmath, python, english, computer, datastructure, total, percentage, grade
        FROM students WHERE roll=?
    """, (roll,))
    result = cursor.fetchone()

    if result:
        for row in tree.get_children():
            tree.delete(row)
        formatted = list(result)
        formatted[8] = f"{result[8]:.2f}%"
        tree.insert("", tk.END, values=formatted, tags=("found",))
        fill_fields(result)
        messagebox.showinfo(
            "Student Found 🔍",
            f"Name       : {result[1]}\n"
            f"Total Marks: {result[7]} / 500\n"
            f"Percentage : {result[8]:.2f}%\n"
            f"Grade      : {result[9]}"
        )
    else:
        messagebox.showerror("Not Found", f"No student found with Roll No: {roll}")

def update_student():
    data = get_inputs()
    if data is None:
        return
    roll, name, am, py, en, co, ds = data

    cursor.execute("SELECT roll FROM students WHERE roll=?", (roll,))
    if not cursor.fetchone():
        messagebox.showerror("Error", f"No student found with Roll No: {roll}\nAdd the student first.")
        return

    total      = am + py + en + co + ds
    percentage = total / 5
    grade      = calculate_grade(percentage)

    cursor.execute("""
        UPDATE students
        SET name=?, appliedmath=?, python=?, english=?, computer=?, datastructure=?, total=?, percentage=?, grade=?
        WHERE roll=?
    """, (name, am, py, en, co, ds, total, round(percentage, 2), grade, roll))
    conn.commit()
    messagebox.showinfo(
        "Student Updated ✏️",
        f"Name       : {name}\n"
        f"Total Marks: {total} / 500\n"
        f"Percentage : {percentage:.2f}%\n"
        f"Grade      : {grade}"
    )
    clear_fields()
    refresh_table()

def delete_student():
    roll = entry_roll.get().strip()
    if not roll:
        messagebox.showerror("Error", "Enter a Roll Number to delete!")
        return

    cursor.execute("SELECT name FROM students WHERE roll=?", (roll,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("Error", f"No student found with Roll No: {roll}")
        return

    confirm = messagebox.askyesno("Confirm Delete", f"Delete student '{result[0]}' (Roll: {roll})?")
    if confirm:
        cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
        conn.commit()
        messagebox.showinfo("Deleted 🗑️", f"Student '{result[0]}' deleted successfully!")
        clear_fields()
        refresh_table()

# ─────────────────────────────────────────────
# GUI SETUP
# ─────────────────────────────────────────────

root = tk.Tk()
root.title("🎓 Student Result Management System")
root.geometry("980x600")
root.config(bg="#b0d8e8")
root.resizable(True, True)

# ── Title ──
tk.Label(root, text="🎓 Student Result Management System",
         font=("Arial", 14, "bold"), bg="#1565C0", fg="white",
         pady=8).pack(fill=tk.X)

# ── Input Frame ──
frame_input = tk.Frame(root, bg="#c8f0c8", bd=2, relief=tk.GROOVE)
frame_input.pack(side=tk.TOP, pady=10, padx=15)

label_texts = ["Roll No:", "Name:", "AppliedMaths (0-100):", "Python (0-100):",
               "English (0-100):", "Computer Networking (0-100):", "Data Structure (0-100):"]

for i, text in enumerate(label_texts):
    tk.Label(frame_input, text=text, bg="#c8f0c8",
             font=("Arial", 10, "bold"), anchor="e", width=26).grid(row=i, column=0, padx=8, pady=4, sticky="e")

entry_roll          = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_name          = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_appliedmaths  = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_python        = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_english       = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_computer      = tk.Entry(frame_input, width=28, font=("Arial", 10))
entry_datastructure = tk.Entry(frame_input, width=28, font=("Arial", 10))

all_entries = [entry_roll, entry_name, entry_appliedmaths, entry_python,
               entry_english, entry_computer, entry_datastructure]

for i, e in enumerate(all_entries):
    e.grid(row=i, column=1, padx=8, pady=4)

# ── Button Frame ──
frame_buttons = tk.Frame(root, bg="#b0d8e8")
frame_buttons.pack(side=tk.TOP, pady=6)

buttons = [
    ("➕ Add",      "#4CAF50", add_student),
    ("🔍 Search",   "#2196F3", search_student),
    ("✏️ Update",   "#FF9800", update_student),
    ("🗑️ Delete",   "#F44336", delete_student),
    ("🔄 Refresh",  "#9C27B0", refresh_table),
    ("🧹 Clear",    "#607D8B", clear_fields),
]

for col, (text, color, cmd) in enumerate(buttons):
    tk.Button(frame_buttons, text=text, bg=color, fg="white", command=cmd,
              width=12, font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2,
              cursor="hand2").grid(row=0, column=col, padx=6)

# ── Table Frame ──
frame_table = tk.Frame(root, bd=2, relief=tk.SUNKEN)
frame_table.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

columns = ("Roll", "Name", "AppliedMaths", "Python", "English", "Computer", "Datastructure", "Total", "Percentage", "Grade")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#1565C0", foreground="black")
style.configure("Treeview", font=("Arial", 10), rowheight=26)

col_widths = [60, 130, 100, 75, 75, 110, 105, 65, 90, 65]
for col, w in zip(columns, col_widths):
    tree.heading(col, text=col)
    tree.column(col, width=w, anchor="center")

tree.tag_configure("oddrow",  background="#e8f5e9")
tree.tag_configure("evenrow", background="#ffffff")
tree.tag_configure("found",   background="#fff9c4")

sy = ttk.Scrollbar(frame_table, orient=tk.VERTICAL,   command=tree.yview)
sx = ttk.Scrollbar(frame_table, orient=tk.HORIZONTAL, command=tree.xview)
tree.configure(yscroll=sy.set, xscroll=sx.set)

sy.pack(side=tk.RIGHT,  fill=tk.Y)
sx.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

# ── Initial load ──
refresh_table()

root.mainloop()
conn.close()



