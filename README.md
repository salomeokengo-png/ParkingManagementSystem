# Modern Parking Management System

## Project Description

The Modern Parking Management System is a computerized system designed to manage parking operations efficiently. It allows users to check available parking spaces, register vehicles, assign parking slots, process vehicle exits, and view parking information.

The system consists of a Python backend, a Tkinter graphical user interface (frontend), and a MySQL database.

## Technologies Used

* Python
* Tkinter
* MySQL
* MySQL Connector/Python
* Git
* GitHub

## System Modules

The system contains the following 8 modules:

### 1. Parking Slot Availability Module

Displays parking slots and shows whether each slot is available or occupied.

### 2. Vehicle Parking Module

Registers a vehicle and automatically assigns an available parking slot.

### 3. Vehicle Exit Module

Records the vehicle exit time, calculates the parking duration and parking fee, and makes the parking slot available again.

### 4. Parked Vehicles Module

Displays vehicles that are currently parked in the parking facility.

### 5. Parking History Module

Displays previous parking records, including entry time, exit time, duration, amount, and status.

### 6. Revenue Module

Displays parking revenue generated from completed parking transactions.

### 7. Vehicle Search Module

Allows the user to search for a vehicle using its registration/plate number.

### 8. Database Management Module

Stores and manages vehicle, parking slot, parking record, and payment information using MySQL.

## Database Tables

The system uses the following MySQL tables:

* `vehicles`
* `parking_slots`
* `parking_records`
* `payments`

## Main Features

* Check available parking slots
* Register and park vehicles
* Automatically assign parking slots
* Process vehicle exits
* Calculate parking fees
* View currently parked vehicles
* View parking history
* Search for vehicles
* View parking revenue
* Store data permanently in MySQL

## How to Run the System

### 1. Start MySQL

Make sure the MySQL server is running.

### 2. Set up the database

Run the SQL commands in `database.sql` to create the `parking_system` database and its tables.

### 3. Install Python dependencies

Open the terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

### 4. Run the backend

```bash
python parking_system.py
```

### 5. Run the frontend

```bash
python frontend.py
```

## Project Structure

```text
ParkingManagementSystem/
│
├── parking_system.py
├── frontend.py
├── database.sql
├── requirements.txt
├── README.md
└── .gitignore
```

## Author

Salome Kemunto

## Repository

Parking Management System developed as a university programming/database project.
