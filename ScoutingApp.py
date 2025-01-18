import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import os
import csv
import qrcode
from PIL import ImageTk, Image

# Setup environment to suppress Tkinter warning
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Database Setup
def initialize_db():
    """Initialize the SQLite database and create the required table."""
    try:
        conn = sqlite3.connect("scouting.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scouting_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_number INTEGER NOT NULL,
                match_number INTEGER NOT NULL,
                match_level TEXT,
                auto_points INTEGER DEFAULT 0,
                teleop_points INTEGER DEFAULT 0,
                endgame_points INTEGER DEFAULT 0,
                team_station TEXT,
                comments TEXT,
                scouter_name TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error initializing the database: {e}")

# Insert Data into Database
def save_data():
    """Save the input data into the SQLite database."""
    team_number = team_entry.get()
    match_number = match_entry.get()
    match_level = match_level_entry.get()
    auto_points = auto_points_entry.get() or 0
    teleop_points = teleop_points_entry.get() or 0
    endgame_points = endgame_points_entry.get() or 0
    team_station = team_station_var.get()  # Retrieve the selected team station
    comments = comments_entry.get("1.0", tk.END).strip()
    scouter_name = scouter_name_entry.get()  # Retrieve the scouter's name

    # Validate required fields
    if not team_number.isdigit() or not match_number.isdigit():
        messagebox.showerror("Input Error", "Team number and match number must be integers!")
        return

    if team_station == "Select Team Station":
        messagebox.showerror("Input Error", "Please select a team station!")
        return

    try:
        conn = sqlite3.connect("scouting.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scouting_data (
                team_number, match_number, match_level, auto_points, teleop_points, 
                endgame_points, team_station, comments, scouter_name, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(team_number), int(match_number), match_level, int(auto_points),
            int(teleop_points), int(endgame_points), team_station,
            comments, scouter_name
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Data saved successfully!")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to save data: {e}")

# Clear Input Fields
def clear_fields():
    """Clear all input fields in the form."""
    team_entry.delete(0, tk.END)
    match_entry.delete(0, tk.END)
    match_level_entry.set("Select Match Level")
    auto_points_entry.delete(0, tk.END)
    teleop_points_entry.delete(0, tk.END)
    endgame_points_entry.delete(0, tk.END)
    team_station_var.set("Select Team Station")
    comments_entry.delete("1.0", tk.END)
    scouter_name_entry.delete(0, tk.END)

# Export to CSV
def export_to_csv():
    """Export data to a CSV file."""
    filename = f"scouting_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        conn = sqlite3.connect("scouting.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scouting_data")
        rows = cursor.fetchall()
        conn.close()

        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Team Number", "Match Number", "Match Level", "Auto Points", "Teleop Points", "Endgame Points", "Team Station", "Comments", "Scouter Name", "Timestamp"])
            writer.writerows(rows)

        messagebox.showinfo("Success", f"Data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {e}")

# Generate QR Code
def generate_qr_code():
    """Generate a QR code that links to the spreadsheet of the data."""
    scouter_name = scouter_name_entry.get()
    match_number = match_entry.get()
    team_number = team_entry.get()
    match_level = match_level_entry.get()
    auto_points = auto_points_entry.get()
    teleop_points = teleop_points_entry.get()
    endgame_points = endgame_points_entry.get()
    team_station = team_station_var.get()
    comments = comments_entry.get("1.0", tk.END).strip()

    # Format the data to display in the QR code
    data = f"{scouter_name}\t{team_number}\t{match_number}\t{match_level}\t{auto_points}\t{teleop_points}\t{endgame_points}\t{team_station}\t{comments}\n"

    # Generate the QR code
    qr = qrcode.make(data)

    # Convert QR code to an image and display it
    qr_image = ImageTk.PhotoImage(qr)
    qr_window = tk.Toplevel()
    qr_window.title("QR Code")
    qr_label = tk.Label(qr_window, image=qr_image)
    qr_label.image = qr_image  # Keep a reference to the image
    qr_label.pack()

# Create Main App Window
def create_app():
    """Create and display the main application window."""
    root = tk.Tk()
    root.title("FRC Scouting App")
    root.geometry("500x800")  # Adjusted window size for better layout
    root.resizable(False, False)
    root.config(bg="black")  # Set background color to black

    # Load Reefscape Logo
    try:
        logo_path = "Reefscape-Banner.png"  # Update this if the image is in a different path
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((250, 100))  # Resize logo to fit
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Add logo at the top
        logo_label = tk.Label(root, image=logo_photo, bg="black")
        logo_label.image = logo_photo  # Keep reference to avoid garbage collection
        logo_label.pack(pady=10)  # Adds space around the logo
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load logo: {e}")

    # Title
    title_label = tk.Label(root, text="FRC Scouting App", font=("Arial", 20), bg="black", fg="white")
    title_label.pack(pady=15)

    # Input Fields
    fields_frame = tk.Frame(root, bg="black")
    fields_frame.pack(pady=10, padx=10)

    # Labels
    tk.Label(fields_frame, text="Scouter Name:", fg="white", bg="black").grid(row=0, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Team Number:", fg="white", bg="black").grid(row=1, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Match Number:", fg="white", bg="black").grid(row=2, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Match Level:", fg="white", bg="black").grid(row=3, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Auto Points:", fg="white", bg="black").grid(row=4, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Teleop Points:", fg="white", bg="black").grid(row=5, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Endgame Points:", fg="white", bg="black").grid(row=6, column=0, sticky="w", pady=5)
    tk.Label(fields_frame, text="Team Station:", fg="white", bg="black").grid(row=7, column=0, sticky="nw", pady=5)
    tk.Label(fields_frame, text="Comments:", fg="white", bg="black").grid(row=15, column=0, sticky="nw", pady=15)

    # Inputs
    global scouter_name_entry, team_entry, match_entry, match_level_entry, auto_points_entry, teleop_points_entry, endgame_points_entry, team_station_var, comments_entry
    scouter_name_entry = tk.Entry(fields_frame, width=21)
    team_entry = tk.Entry(fields_frame, width=21)
    match_entry = tk.Spinbox(fields_frame, from_=1, to=999, width=20)
    match_level_entry = ttk.Combobox(fields_frame, values=["Quals", "Semi-finals", "Finals"], state="readonly", width=20)
    match_level_entry.set("Select Match Level")
    auto_points_entry = tk.Spinbox(fields_frame, from_=0, to=100, width=20)
    teleop_points_entry = tk.Spinbox(fields_frame, from_=0, to=100, width=20)
    endgame_points_entry = tk.Spinbox(fields_frame, from_=0, to=100, width=20)
    

    team_station_var = tk.StringVar(value="Select Team Station")
    stations = [("Red 1", 0, 0), ("Red 2", 0, 1), ("Red 3", 0, 2),
                ("Blue 1", 1, 0), ("Blue 2", 1, 1), ("Blue 3", 1, 2)]

    # Adjust row positions for the radio buttons
    for station, col, row in stations:
        tk.Radiobutton(fields_frame, text=station, variable=team_station_var, value=station, bg="black", fg="white", selectcolor="gray").grid(row=row + 7, column=col + 1, padx=1, pady=1, sticky="w")

    comments_entry = tk.Text(fields_frame, height=5, width=30)

    # Arrange inputs in grid
    scouter_name_entry.grid(row=0, column=1, pady=5)
    team_entry.grid(row=1, column=1, pady=5)
    match_entry.grid(row=2, column=1, pady=5)
    match_level_entry.grid(row=3, column=1, pady=5)
    auto_points_entry.grid(row=4, column=1, pady=5)
    teleop_points_entry.grid(row=5, column=1, pady=5)
    endgame_points_entry.grid(row=6, column=1, pady=5)
    comments_entry.grid(row=15, column=1, pady=5)

    # Buttons Frame
    buttons_frame = tk.Frame(root, bg="black")
    buttons_frame.pack(pady=30)

    save_button = tk.Button(buttons_frame, text="Save Data", command=save_data, width=15, bg="gray", fg="black")
    clear_button = tk.Button(buttons_frame, text="Clear Fields", command=clear_fields, width=15, bg="gray", fg="black")
    qr_button = tk.Button(buttons_frame, text="QR Code", command=generate_qr_code, width=15, bg="gray", fg="black")
    export_button = tk.Button(buttons_frame, text="Export to CSV", command=export_to_csv, width=15, bg="gray", fg="black")

    save_button.grid(row=0, column=0, padx=10)
    clear_button.grid(row=0, column=1, padx=10)
    qr_button.grid(row=1, column=0, padx=10, pady=10)
    export_button.grid(row=1, column=1, padx=10)

    root.mainloop()

# Initialize DB
initialize_db()

# Start the application
create_app()
