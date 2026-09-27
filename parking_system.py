import mysql.connector
from datetime import datetime


# =========================================================
# DATABASE CONNECTION
# =========================================================

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="parking_system"
    )


# =========================================================
# 1. VIEW AVAILABLE PARKING SLOTS
# =========================================================

def show_available_slots():

    connection = None
    cursor = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT slot_number "
            "FROM parking_slots "
            "WHERE status = 'Available' "
            "ORDER BY slot_id"
        )

        slots = cursor.fetchall()

        print("\n")
        print("========================================")
        print("          AVAILABLE PARKING SLOTS")
        print("========================================")

        if len(slots) == 0:
            print("No parking slots are currently available.")
        else:
            for slot in slots:
                print("Slot:", slot[0])

        print("========================================")

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 2. PARK VEHICLE
# =========================================================

def park_vehicle():

    connection = None
    cursor = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        registration = input(
            "\nEnter vehicle registration number: "
        ).strip().upper()

        if registration == "":
            print("\nVehicle registration cannot be empty.")
            return

        # Check whether vehicle already exists
        cursor.execute(
            "SELECT vehicle_id "
            "FROM vehicles "
            "WHERE plate_number = %s",
            (registration,)
        )

        existing_vehicle = cursor.fetchone()

        # If vehicle exists, get its ID
        if existing_vehicle:
            vehicle_id = existing_vehicle[0]

            # Check whether it is already parked
            cursor.execute(
                "SELECT record_id "
                "FROM parking_records "
                "WHERE vehicle_id = %s "
                "AND status = 'Parked'",
                (vehicle_id,)
            )

            already_parked = cursor.fetchone()

            if already_parked:
                print("\nThis vehicle is already parked.")
                return

        # Find first available slot
        cursor.execute(
            "SELECT slot_id, slot_number "
            "FROM parking_slots "
            "WHERE status = 'Available' "
            "ORDER BY slot_id "
            "LIMIT 1"
        )

        available_slot = cursor.fetchone()

        if available_slot is None:
            print("\nSorry, the parking lot is FULL.")
            return

        slot_id = available_slot[0]
        slot_number = available_slot[1]

        # Register vehicle if it does not already exist
        if existing_vehicle is None:

            cursor.execute(
                "INSERT INTO vehicles "
                "(plate_number, vehicle_type) "
                "VALUES (%s, %s)",
                (registration, "Car")
            )

            vehicle_id = cursor.lastrowid

        # Mark slot as occupied
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

        print("\n========================================")
        print("        VEHICLE PARKED SUCCESSFULLY")
        print("========================================")
        print("Vehicle registration:", registration)
        print("Assigned parking slot:", slot_number)
        print("Entry time:", datetime.now())
        print("========================================")

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()

        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 3. VEHICLE EXIT
# =========================================================

def exit_vehicle():

    connection = None
    cursor = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        registration = input(
            "\nEnter vehicle registration number: "
        ).strip().upper()

        if registration == "":
            print("\nVehicle registration cannot be empty.")
            return

        # Find the vehicle's active parking record
        cursor.execute(
            "SELECT "
            "v.vehicle_id, "
            "p.record_id, "
            "p.slot_id, "
            "p.entry_time "
            "FROM vehicles v "
            "INNER JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "WHERE v.plate_number = %s "
            "AND p.status = 'Parked'",
            (registration,)
        )

        record = cursor.fetchone()

        if record is None:
            print("\nVehicle is not currently parked.")
            return

        vehicle_id = record[0]
        record_id = record[1]
        slot_id = record[2]
        entry_time = record[3]

        # Current time
        exit_time = datetime.now()

        # Calculate duration
        duration = exit_time - entry_time
        duration_hours = duration.total_seconds() / 3600

        # Charge at least one hour
        chargeable_hours = max(
            1,
            int(duration_hours) if duration_hours.is_integer()
            else int(duration_hours) + 1
        )

        # Rate = KSh 100 per hour
        rate_per_hour = 100

        amount = chargeable_hours * rate_per_hour

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

        # Make slot available again
        cursor.execute(
            "UPDATE parking_slots "
            "SET status = 'Available' "
            "WHERE slot_id = %s",
            (slot_id,)
        )

        connection.commit()

        print("\n========================================")
        print("         VEHICLE EXIT SUCCESSFUL")
        print("========================================")
        print("Vehicle:", registration)
        print("Entry time:", entry_time)
        print("Exit time:", exit_time)
        print("Duration: %.2f hours" % duration_hours)
        print("Chargeable hours:", chargeable_hours)
        print("Parking fee: KSh %.2f" % amount)
        print("========================================")

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()

        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 4. VIEW CURRENTLY PARKED VEHICLES
# =========================================================

def view_parked_vehicles():

    connection = None
    cursor = None

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
            "INNER JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "INNER JOIN parking_slots ps "
            "ON p.slot_id = ps.slot_id "
            "WHERE p.status = 'Parked' "
            "ORDER BY p.entry_time"
        )

        vehicles = cursor.fetchall()

        print("\n")
        print("======================================================")
        print("             CURRENTLY PARKED VEHICLES")
        print("======================================================")

        if len(vehicles) == 0:

            print("No vehicles are currently parked.")

        else:

            for vehicle in vehicles:

                print(
                    "Vehicle:", vehicle[0],
                    "| Type:", vehicle[1],
                    "| Slot:", vehicle[2],
                    "| Entry:", vehicle[3]
                )

        print("======================================================")

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 5. VIEW PARKING HISTORY
# =========================================================

def view_parking_history():

    connection = None
    cursor = None

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
            "INNER JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "INNER JOIN parking_slots ps "
            "ON p.slot_id = ps.slot_id "
            "ORDER BY p.entry_time DESC"
        )

        records = cursor.fetchall()

        print("\n")
        print("==========================================================================")
        print("                       PARKING HISTORY")
        print("==========================================================================")

        if len(records) == 0:

            print("No parking history found.")

        else:

            for record in records:

                print(
                    "Vehicle:", record[0],
                    "| Slot:", record[1],
                    "| Entry:", record[2],
                    "| Exit:", record[3],
                    "| Hours:", record[4],
                    "| Amount:", record[5],
                    "| Status:", record[6]
                )

        print("==========================================================================")

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 6. VIEW TOTAL PARKING REVENUE
# =========================================================

def view_revenue():

    connection = None
    cursor = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT "
            "COUNT(*), "
            "COALESCE(SUM(amount), 0) "
            "FROM parking_records "
            "WHERE status = 'Exited'"
        )

        result = cursor.fetchone()

        number_of_payments = result[0]
        total_revenue = result[1]

        print("\n")
        print("========================================")
        print("           PARKING REVENUE")
        print("========================================")
        print("Completed parking sessions:", number_of_payments)
        print("Total revenue: KSh %.2f" % total_revenue)
        print("========================================")

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# 7. SEARCH FOR A VEHICLE
# =========================================================

def search_vehicle():

    connection = None
    cursor = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        registration = input(
            "\nEnter vehicle registration number to search: "
        ).strip().upper()

        if registration == "":
            print("\nVehicle registration cannot be empty.")
            return

        cursor.execute(
            "SELECT "
            "v.plate_number, "
            "v.vehicle_type, "
            "p.status, "
            "ps.slot_number, "
            "p.entry_time, "
            "p.exit_time, "
            "p.amount "
            "FROM vehicles v "
            "LEFT JOIN parking_records p "
            "ON v.vehicle_id = p.vehicle_id "
            "LEFT JOIN parking_slots ps "
            "ON p.slot_id = ps.slot_id "
            "WHERE v.plate_number = %s "
            "ORDER BY p.entry_time DESC "
            "LIMIT 1",
            (registration,)
        )

        vehicle = cursor.fetchone()

        print("\n========================================")
        print("             VEHICLE SEARCH")
        print("========================================")

        if vehicle is None:

            print("Vehicle not found.")

        else:

            print("Registration:", vehicle[0])
            print("Vehicle type:", vehicle[1])
            print("Status:", vehicle[2])

            if vehicle[3] is not None:
                print("Parking slot:", vehicle[3])

            if vehicle[4] is not None:
                print("Entry time:", vehicle[4])

            if vehicle[5] is not None:
                print("Exit time:", vehicle[5])

            if vehicle[6] is not None:
                print("Amount: KSh %.2f" % vehicle[6])

        print("========================================")

    except mysql.connector.Error as error:
        print("\nDatabase error:", error)

    except Exception as error:
        print("\nError:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# MAIN MENU
# =========================================================

def main():

    while True:

        print("\n")
        print("==============================================")
        print("          MODERN PARKING SYSTEM")
        print("==============================================")
        print("1. View Available Parking Slots")
        print("2. Park Vehicle")
        print("3. Vehicle Exit")
        print("4. View Currently Parked Vehicles")
        print("5. View Parking History")
        print("6. View Parking Revenue")
        print("7. Search Vehicle")
        print("8. Exit Program")
        print("==============================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":

            show_available_slots()

        elif choice == "2":

            park_vehicle()

        elif choice == "3":

            exit_vehicle()

        elif choice == "4":

            view_parked_vehicles()

        elif choice == "5":

            view_parking_history()

        elif choice == "6":

            view_revenue()

        elif choice == "7":

            search_vehicle()

        elif choice == "8":

            print("\nThank you for using the Modern Parking System.")
            break

        else:

            print("\nInvalid choice.")
            print("Please enter a number from 1 to 8.")


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    main()