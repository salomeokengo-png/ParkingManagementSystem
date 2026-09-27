import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime


# ==============================
# DATABASE CONNECTION
# ==============================

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="parking_system"
    )


# ==============================
# REFRESH PARKING SLOTS
# ==============================

def refresh_slots():

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT slot_number, status "
            "FROM parking_slots "
            "ORDER BY slot_id"
        )

        slots = cursor.fetchall()

        for item in slots_table.get_children():
            slots_table.delete(item)

        available = 0
        occupied = 0

        for slot in slots:
            slots_table.insert(
                "",
                "end",
                values=(slot[0], slot[1])
            )

            if slot[1] == "Available":
                available += 1
            else:
                occupied += 1

        available_label.config(
            text="Available: " + str(available)
        )

        occupied_label.config(
            text="Occupied: " + str(occupied)
        )

        cursor.close()
        connection.close()

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ==============================
# PARK VEHICLE
# ==============================

def park_vehicle():

    registration = registration_entry.get().strip().upper()

    if registration == "":
        messagebox.showwarning(
            "Missing Information",
            "Please enter a vehicle registration number."
        )
        return

    try:
        connection = connect_database()
        cursor = connection.cursor()

        # Check vehicle
        cursor.execute(
            "SELECT vehicle_id FROM vehicles "
            "WHERE plate_number = %s",
            (registration,)
        )

        existing = cursor.fetchone()

        if existing:

            vehicle_id = existing[0]

            cursor.execute(
                "SELECT record_id FROM parking_records "
                "WHERE vehicle_id = %s "
                "AND status = 'Parked'",
                (vehicle_id,)
            )

            if cursor.fetchone():
                messagebox.showwarning(
                    "Already Parked",
                    "This vehicle is already parked."
                )

                cursor.close()
                connection.close()
                return

        # Find available slot
        cursor.execute(
            "SELECT slot_id, slot_number "
            "FROM parking_slots "
            "WHERE status = 'Available' "
            "ORDER BY slot_id "
            "LIMIT 1"
        )

        slot = cursor.fetchone()

        if slot is None:
            messagebox.showwarning(
                "Parking Full",
                "There are no available parking slots."
            )

            cursor.close()
            connection.close()
            return

        slot_id = slot[0]
        slot_number = slot[1]

        # Register vehicle
        if existing is None:

            cursor.execute(
                "INSERT INTO vehicles "
                "(plate_number, vehicle_type) "
                "VALUES (%s, %s)",
                (registration, "Car")
            )

            vehicle_id = cursor.lastrowid

        # Occupy slot
        cursor.execute(
            "UPDATE parking_slots "
            "SET status = 'Occupied' "
            "WHERE slot_id = %s",
            (slot_id,)
        )

        # Create parking record
        cursor.execute(
            "INSERT INTO parking_records "
            "(vehicle_id, slot_id, entry_time, status) "
            "VALUES (%s, %s, NOW(), 'Parked')",
            (vehicle_id, slot_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Success",
            "Vehicle parked successfully!\n\n"
            "Vehicle: " + registration +
            "\nParking Slot: " + slot_number
        )

        registration_entry.delete(0, tk.END)

        refresh_slots()
        refresh_parked_vehicles()

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )


# ==============================
# VEHICLE EXIT
# ==============================

def vehicle_exit():

    registration = registration_entry.get().strip().upper()

    if registration == "":
        messagebox.showwarning(
            "Missing Information",
            "Please enter a vehicle registration number."
        )
        return

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT "
            "v.vehicle_id, "
            "p.record_id, "
            "p.slot_id, "
            "p.entry_time "
            "FROM vehicles v "
            "JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "WHERE v.plate_number = %s "
            "AND p.status = 'Parked'",
            (registration,)
        )

        record = cursor.fetchone()

        if record is None:

            messagebox.showwarning(
                "Not Found",
                "This vehicle is not currently parked."
            )

            cursor.close()
            connection.close()
            return

        record_id = record[1]
        slot_id = record[2]
        entry_time = record[3]

        exit_time = datetime.now()

        duration = exit_time - entry_time

        duration_hours = duration.total_seconds() / 3600

        chargeable_hours = max(
            1,
            int(duration_hours) + (
                1 if duration_hours % 1 > 0 else 0
            )
        )

        amount = chargeable_hours * 100

        # Update parking record
        cursor.execute(
            "UPDATE parking_records "
            "SET exit_time = %s, "
            "duration_hours = %s, "
            "amount = %s, "
            "status = 'Exited' "
            "WHERE record_id = %s",
            (
                exit_time,
                duration_hours,
                amount,
                record_id
            )
        )

        # Free the slot
        cursor.execute(
            "UPDATE parking_slots "
            "SET status = 'Available' "
            "WHERE slot_id = %s",
            (slot_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        messagebox.showinfo(
            "Vehicle Exit",
            "Vehicle exited successfully!\n\n"
            "Vehicle: " + registration +
            "\nDuration: %.2f hours" % duration_hours +
            "\nParking Fee: KSh %.2f" % amount
        )

        registration_entry.delete(0, tk.END)

        refresh_slots()
        refresh_parked_vehicles()

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )


# ==============================
# PARKED VEHICLES
# ==============================

def refresh_parked_vehicles():

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT "
            "v.plate_number, "
            "v.vehicle_type, "
            "ps.slot_number, "
            "p.entry_time "
            "FROM vehicles v "
            "JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "JOIN parking_slots ps "
            "ON p.slot_id = ps.slot_id "
            "WHERE p.status = 'Parked' "
            "ORDER BY p.entry_time"
        )

        vehicles = cursor.fetchall()

        for item in parked_table.get_children():
            parked_table.delete(item)

        for vehicle in vehicles:

            parked_table.insert(
                "",
                "end",
                values=(
                    vehicle[0],
                    vehicle[1],
                    vehicle[2],
                    vehicle[3]
                )
            )

        cursor.close()
        connection.close()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ==============================
# PARKING HISTORY
# ==============================

def show_history():

    try:

        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT "
            "v.plate_number, "
            "ps.slot_number, "
            "p.entry_time, "
            "p.exit_time, "
            "p.duration_hours, "
            "p.amount, "
            "p.status "
            "FROM vehicles v "
            "JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "JOIN parking_slots ps "
            "ON p.slot_id = ps.slot_id "
            "ORDER BY p.entry_time DESC"
        )

        records = cursor.fetchall()

        for item in history_table.get_children():
            history_table.delete(item)

        for record in records:

            history_table.insert(
                "",
                "end",
                values=record
            )

        cursor.close()
        connection.close()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error)
        )


# ==============================
# MAIN WINDOW
# ==============================

root = tk.Tk()

root.title("Modern Parking Management System")

root.geometry("1000x700")

root.minsize(900, 600)


# ==============================
# TITLE
# ==============================

title = tk.Label(
    root,
    text="MODERN PARKING MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold")
)

title.pack(pady=15)


subtitle = tk.Label(
    root,
    text="Smart Parking • Vehicle Management • Parking Records",
    font=("Arial", 11)
)

subtitle.pack()


# ==============================
# STATUS FRAME
# ==============================

status_frame = tk.Frame(root)

status_frame.pack(pady=15)


available_label = tk.Label(
    status_frame,
    text="Available: 0",
    font=("Arial", 14, "bold")
)

available_label.grid(row=0, column=0, padx=30)


occupied_label = tk.Label(
    status_frame,
    text="Occupied: 0",
    font=("Arial", 14, "bold")
)

occupied_label.grid(row=0, column=1, padx=30)


# ==============================
# VEHICLE INPUT
# ==============================

input_frame = tk.Frame(root)

input_frame.pack(pady=10)


tk.Label(
    input_frame,
    text="Vehicle Registration:",
    font=("Arial", 12)
).grid(row=0, column=0, padx=5)


registration_entry = tk.Entry(
    input_frame,
    width=25,
    font=("Arial", 12)
)

registration_entry.grid(row=0, column=1, padx=5)


park_button = tk.Button(
    input_frame,
    text="PARK VEHICLE",
    command=park_vehicle,
    font=("Arial", 11, "bold"),
    width=16
)

park_button.grid(row=0, column=2, padx=5)


exit_button = tk.Button(
    input_frame,
    text="VEHICLE EXIT",
    command=vehicle_exit,
    font=("Arial", 11, "bold"),
    width=16
)

exit_button.grid(row=0, column=3, padx=5)


# ==============================
# NOTEBOOK
# ==============================

notebook = ttk.Notebook(root)

notebook.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)


# ==============================
# SLOTS TAB
# ==============================

slots_frame = tk.Frame(notebook)

notebook.add(
    slots_frame,
    text="Parking Slots"
)


slots_table = ttk.Treeview(
    slots_frame,
    columns=("slot", "status"),
    show="headings"
)

slots_table.heading(
    "slot",
    text="Parking Slot"
)

slots_table.heading(
    "status",
    text="Status"
)

slots_table.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


refresh_slots_button = tk.Button(
    slots_frame,
    text="REFRESH SLOTS",
    command=refresh_slots,
    font=("Arial", 11, "bold")
)

refresh_slots_button.pack(pady=10)


# ==============================
# PARKED VEHICLES TAB
# ==============================

parked_frame = tk.Frame(notebook)

notebook.add(
    parked_frame,
    text="Parked Vehicles"
)


parked_table = ttk.Treeview(
    parked_frame,
    columns=(
        "vehicle",
        "type",
        "slot",
        "entry"
    ),
    show="headings"
)

parked_table.heading(
    "vehicle",
    text="Registration"
)

parked_table.heading(
    "type",
    text="Vehicle Type"
)

parked_table.heading(
    "slot",
    text="Parking Slot"
)

parked_table.heading(
    "entry",
    text="Entry Time"
)

parked_table.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


refresh_parked_button = tk.Button(
    parked_frame,
    text="REFRESH PARKED VEHICLES",
    command=refresh_parked_vehicles,
    font=("Arial", 11, "bold")
)

refresh_parked_button.pack(pady=10)


# ==============================
# HISTORY TAB
# ==============================

history_frame = tk.Frame(notebook)

notebook.add(
    history_frame,
    text="Parking History"
)


history_table = ttk.Treeview(
    history_frame,
    columns=(
        "vehicle",
        "slot",
        "entry",
        "exit",
        "hours",
        "amount",
        "status"
    ),
    show="headings"
)

history_table.heading(
    "vehicle",
    text="Vehicle"
)

history_table.heading(
    "slot",
    text="Slot"
)

history_table.heading(
    "entry",
    text="Entry"
)

history_table.heading(
    "exit",
    text="Exit"
)

history_table.heading(
    "hours",
    text="Hours"
)

history_table.heading(
    "amount",
    text="Amount"
)

history_table.heading(
    "status",
    text="Status"
)

history_table.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=20
)


history_button = tk.Button(
    history_frame,
    text="REFRESH HISTORY",
    command=show_history,
    font=("Arial", 11, "bold")
)

history_button.pack(pady=10)


# ==============================
# INITIAL DATA LOAD
# ==============================

refresh_slots()

refresh_parked_vehicles()

show_history()


# ==============================
# START FRONTEND
# ==============================

root.mainloop()