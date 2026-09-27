CREATE DATABASE parking_system;

USE parking_system;

CREATE TABLE parking_slots (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    slot_number VARCHAR(10) NOT NULL UNIQUE,
    status ENUM('Available', 'Occupied') DEFAULT 'Available'
);

CREATE TABLE vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(30) NOT NULL,
    owner_name VARCHAR(100)
);

CREATE TABLE parking_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    slot_id INT NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    duration_hours DECIMAL(10,2),
    amount DECIMAL(10,2),
    status ENUM('Parked', 'Exited') DEFAULT 'Parked',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(30),
    FOREIGN KEY (record_id) REFERENCES parking_records(record_id)
);