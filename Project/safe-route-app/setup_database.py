#!/usr/bin/env python3
"""
Setup script for My Safety Admin Dashboard
This script helps you set up the database and run the application
"""

import mysql.connector
from mysql.connector import Error
import os

def create_database():
    """Create the mysafety database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=input("Enter your MySQL root password: ")
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS mysafety")
            print("Database 'mysafety' created successfully")
            
            # Use the database
            cursor.execute("USE mysafety")
            
            # Create tables based on your schema
            create_tables(cursor)
            
            cursor.close()
            connection.close()
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables(cursor):
    """Create all necessary tables"""
    
    # District table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS district (
            district_id INT AUTO_INCREMENT PRIMARY KEY,
            district_name VARCHAR(100) NOT NULL,
            state VARCHAR(50) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Location table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location (
            location_id INT AUTO_INCREMENT PRIMARY KEY,
            area_name VARCHAR(100) NOT NULL,
            city VARCHAR(50) NOT NULL,
            district_id INT,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (district_id) REFERENCES district(district_id)
        )
    """)
    
    # Police Station table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policestation (
            station_id INT AUTO_INCREMENT PRIMARY KEY,
            station_name VARCHAR(100) NOT NULL,
            address VARCHAR(255),
            location_id INT,
            established_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES location(location_id)
        )
    """)
    
    # App User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appuser (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role_id INT,
            station_id INT,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (station_id) REFERENCES policestation(station_id)
        )
    """)
    
    # Station Staff table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS station_staff (
            staff_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            station_id INT,
            position VARCHAR(50),
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (user_id) REFERENCES appuser(user_id),
            FOREIGN KEY (station_id) REFERENCES policestation(station_id)
        )
    """)
    
    # Complaint table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint (
            complaint_id INT AUTO_INCREMENT PRIMARY KEY,
            reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reporter_contact VARCHAR(100),
            description TEXT,
            channel VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pending'
        )
    """)
    
    # Crime table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime (
            crime_id INT AUTO_INCREMENT PRIMARY KEY,
            crime_type VARCHAR(50) NOT NULL,
            description TEXT,
            date_time DATETIME NOT NULL,
            location_id INT,
            status VARCHAR(20) DEFAULT 'reported',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES location(location_id)
        )
    """)
    
    # Victim table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS victim (
            victim_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            dob DATE,
            gender CHAR(1),
            address VARCHAR(255),
            phone_number VARCHAR(20),
            email VARCHAR(100),
            injury_details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Criminal table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS criminal (
            criminal_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            alias_name VARCHAR(100),
            dob DATE,
            gender CHAR(1),
            address VARCHAR(255),
            marital_status VARCHAR(20),
            crime_record TEXT,
            previous_crimes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Weapon table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weapon (
            weapon_id INT AUTO_INCREMENT PRIMARY KEY,
            weapon_name VARCHAR(100) NOT NULL,
            weapon_type VARCHAR(50),
            description TEXT,
            serial_number VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Witness table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS witness (
            witness_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(20),
            protection_flag BOOLEAN DEFAULT FALSE
        )
    """)
    
    # Crime-Victim junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_victim (
            crime_id INT,
            victim_id INT,
            injury_level VARCHAR(20),
            PRIMARY KEY (crime_id, victim_id),
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (victim_id) REFERENCES victim(victim_id)
        )
    """)
    
    # Crime-Criminal junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_criminal (
            crime_id INT,
            criminal_id INT,
            notes TEXT,
            PRIMARY KEY (crime_id, criminal_id),
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (criminal_id) REFERENCES criminal(criminal_id)
        )
    """)
    
    # Crime-Weapon junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_weapon (
            crime_id INT,
            weapon_id INT,
            usage_detail TEXT,
            PRIMARY KEY (crime_id, weapon_id),
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (weapon_id) REFERENCES weapon(weapon_id)
        )
    """)
    
    # Crime-Witness junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_witness (
            crime_id INT,
            witness_id INT,
            statement_status VARCHAR(20),
            PRIMARY KEY (crime_id, witness_id),
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (witness_id) REFERENCES witness(witness_id)
        )
    """)
    
    # Case Assignment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_assignment (
            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            crime_id INT,
            duty_role VARCHAR(50),
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            released_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES appuser(user_id),
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id)
        )
    """)
    
    # Case Status History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_status_history (
            status_id INT AUTO_INCREMENT PRIMARY KEY,
            crime_id INT,
            status VARCHAR(20),
            notes TEXT,
            changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            changed_by INT,
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (changed_by) REFERENCES appuser(user_id)
        )
    """)
    
    # Evidence table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id INT AUTO_INCREMENT PRIMARY KEY,
            crime_id INT,
            evidence_type VARCHAR(50),
            storage_ref VARCHAR(100),
            notes TEXT,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            collected_by INT,
            FOREIGN KEY (crime_id) REFERENCES crime(crime_id),
            FOREIGN KEY (collected_by) REFERENCES appuser(user_id)
        )
    """)
    
    # Arrest table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arrest (
            arrest_id INT AUTO_INCREMENT PRIMARY KEY,
            criminal_id INT,
            arrest_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            officer_id INT,
            location_detail VARCHAR(255),
            FOREIGN KEY (criminal_id) REFERENCES criminal(criminal_id),
            FOREIGN KEY (officer_id) REFERENCES appuser(user_id)
        )
    """)
    
    # Charge table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS charge (
            charge_id INT AUTO_INCREMENT PRIMARY KEY,
            arrest_id INT,
            legal_code VARCHAR(20),
            description TEXT,
            disposition VARCHAR(20),
            FOREIGN KEY (arrest_id) REFERENCES arrest(arrest_id)
        )
    """)
    
    # Known Associates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS known_associates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            criminal_id_FK INT,
            associate_id_FK INT,
            relation_type VARCHAR(50),
            notes TEXT,
            FOREIGN KEY (criminal_id_FK) REFERENCES criminal(criminal_id),
            FOREIGN KEY (associate_id_FK) REFERENCES criminal(criminal_id)
        )
    """)
    
    # Contact table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact (
            contact_id INT AUTO_INCREMENT PRIMARY KEY,
            creator_id INT,
            phone_number VARCHAR(20),
            email VARCHAR(100),
            contact_type VARCHAR(50),
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES appuser(user_id)
        )
    """)
    
    # Panic Event table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS panic_event (
            panic_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            location_id INT,
            triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES appuser(user_id),
            FOREIGN KEY (location_id) REFERENCES location(location_id)
        )
    """)
    
    # Panic Notification table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS panic_notification (
            notification_id INT AUTO_INCREMENT PRIMARY KEY,
            panic_id INT,
            sender_id INT,
            receiver_id INT,
            message TEXT,
            delivered BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (panic_id) REFERENCES panic_event(panic_id),
            FOREIGN KEY (sender_id) REFERENCES appuser(user_id),
            FOREIGN KEY (receiver_id) REFERENCES appuser(user_id)
        )
    """)
    
    print("All tables created successfully!")

def insert_sample_data(cursor):
    """Insert sample data for testing"""
    
    # Insert sample districts
    districts = [
        (1, 'Dhaka', 'Dhaka'),
        (2, 'Chittagong', 'Chittagong'),
        (3, 'Sylhet', 'Sylhet'),
        (4, 'Rajshahi', 'Rajshahi'),
        (5, 'Khulna', 'Khulna'),
        (6, 'Barisal', 'Barisal'),
        (7, 'Rangpur', 'Rangpur'),
        (8, 'Mymensingh', 'Mymensingh')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO district (district_id, district_name, state) 
        VALUES (%s, %s, %s)
    """, districts)
    
    # Insert sample admin user
    cursor.execute("""
        INSERT IGNORE INTO appuser (user_id, username, password_hash, full_name, role_id, status)
        VALUES (1, 'admin', 'admin123', 'System Administrator', 1, 'active')
    """)
    
    print("Sample data inserted successfully!")

def main():
    """Main setup function"""
    print("=== My Safety Admin Dashboard Setup ===")
    print("This script will:")
    print("1. Create the 'mysafety' database")
    print("2. Create all necessary tables")
    print("3. Insert sample data")
    print()
    
    response = input("Do you want to proceed? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    create_database()
    
    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. Update the database password in app.py")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000")

if __name__ == "__main__":
    main()
