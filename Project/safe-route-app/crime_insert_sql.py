import mysql.connector
from mysql.connector import Error
import datetime
import json

class CrimeDatabaseManager:
    def __init__(self, host='localhost', database='mysafety', user='root', password=''):
        """Initialize database connection"""
        self.connection = None
        self.cursor = None
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def close_connection(self):
        """Close database connection"""
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")

    def insert_crime_data(self, crime_data):
        """Insert complete crime data using hardcoded SQL queries"""
        try:
            # Start transaction
            self.connection.start_transaction()
            
            # Step 1: Insert Location
            location_id = self._insert_location(crime_data['location'])
            print(f"Location inserted with ID: {location_id}")
            
            # Step 2: Insert Crime
            crime_id = self._insert_crime(crime_data['crime'], location_id)
            print(f"Crime inserted with ID: {crime_id}")
            
            # Step 3: Insert Victim (if provided)
            victim_id = None
            if crime_data.get('victim', {}).get('full_name'):
                victim_id = self._insert_victim(crime_data['victim'])
                print(f"Victim inserted with ID: {victim_id}")
                
                # Insert Crime-Victim relationship
                self._insert_crime_victim(crime_id, victim_id)
                print("Crime-Victim relationship created")
            
            # Step 4: Insert Criminal (if provided)
            criminal_id = None
            if crime_data.get('criminal', {}).get('full_name'):
                criminal_id = self._insert_criminal(crime_data['criminal'])
                print(f"Criminal inserted with ID: {criminal_id}")
                
                # Insert Crime-Criminal relationship
                self._insert_crime_criminal(crime_id, criminal_id)
                print("Crime-Criminal relationship created")
            
            # Step 5: Insert Weapon (if provided)
            weapon_id = None
            if crime_data.get('weapon', {}).get('weapon_name'):
                weapon_id = self._insert_weapon(crime_data['weapon'])
                print(f"Weapon inserted with ID: {weapon_id}")
                
                # Insert Crime-Weapon relationship
                self._insert_crime_weapon(crime_id, weapon_id)
                print("Crime-Weapon relationship created")
            
            # Step 6: Insert Witness (if provided)
            witness_id = None
            if crime_data.get('witness', {}).get('full_name'):
                witness_id = self._insert_witness(crime_data['witness'])
                print(f"Witness inserted with ID: {witness_id}")
                
                # Insert Crime-Witness relationship
                self._insert_crime_witness(crime_id, witness_id)
                print("Crime-Witness relationship created")
            
            # Commit transaction
            self.connection.commit()
            print("Transaction committed successfully")
            
            return {
                'success': True,
                'crime_id': crime_id,
                'location_id': location_id,
                'victim_id': victim_id,
                'criminal_id': criminal_id,
                'weapon_id': weapon_id,
                'witness_id': witness_id
            }
            
        except Error as e:
            # Rollback transaction on error
            self.connection.rollback()
            print(f"Error inserting crime data: {e}")
            return {'success': False, 'error': str(e)}

    def _insert_location(self, location_data):
        """Insert location data using hardcoded SQL"""
        sql = """
        INSERT INTO location (district_id, area_name, city, latitude, longitude, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = (
            location_data['district_id'],
            location_data['area_name'],
            location_data['city'],
            location_data['latitude'],
            location_data['longitude'],
            datetime.datetime.now()
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_crime(self, crime_data, location_id):
        """Insert crime data using hardcoded SQL"""
        sql = """
        INSERT INTO crime (crime_type, description, date_time, location_id, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        values = (
            crime_data['crime_type'],
            crime_data['description'],
            crime_data['date_time'],
            location_id,
            crime_data['status'],
            datetime.datetime.now()
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_victim(self, victim_data):
        """Insert victim data using hardcoded SQL"""
        sql = """
        INSERT INTO victim (full_name, dob, gender, address, phone_number, email, injury_details, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Handle date conversion
        dob = None
        if victim_data.get('dob'):
            dob = datetime.datetime.strptime(victim_data['dob'], '%Y-%m-%d').date()
        
        values = (
            victim_data['full_name'],
            dob,
            victim_data.get('gender'),
            victim_data.get('address'),
            victim_data.get('phone_number'),
            victim_data.get('email'),
            victim_data.get('injury_details'),
            datetime.datetime.now()
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_criminal(self, criminal_data):
        """Insert criminal data using hardcoded SQL"""
        sql = """
        INSERT INTO criminal (full_name, alias_name, dob, gender, address, marital_status, previous_crimes, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Handle date conversion
        dob = None
        if criminal_data.get('dob'):
            dob = datetime.datetime.strptime(criminal_data['dob'], '%Y-%m-%d').date()
        
        values = (
            criminal_data['full_name'],
            criminal_data.get('alias_name'),
            dob,
            criminal_data.get('gender'),
            criminal_data.get('address'),
            criminal_data.get('marital_status'),
            criminal_data.get('previous_crimes'),
            datetime.datetime.now()
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_weapon(self, weapon_data):
        """Insert weapon data using hardcoded SQL"""
        sql = """
        INSERT INTO weapon (weapon_name, weapon_type, description, serial_number, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            weapon_data['weapon_name'],
            weapon_data.get('weapon_type'),
            weapon_data.get('description'),
            weapon_data.get('serial_number'),
            datetime.datetime.now()
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_witness(self, witness_data):
        """Insert witness data using hardcoded SQL"""
        sql = """
        INSERT INTO witness (full_name, phone_number, protection_flag)
        VALUES (%s, %s, %s)
        """
        
        values = (
            witness_data['full_name'],
            witness_data.get('phone_number'),
            witness_data.get('protection_flag', False)
        )
        
        self.cursor.execute(sql, values)
        return self.cursor.lastrowid

    def _insert_crime_victim(self, crime_id, victim_id):
        """Insert crime-victim relationship using hardcoded SQL"""
        sql = """
        INSERT INTO crime_victim (crime_id, victim_id, injury_level)
        VALUES (%s, %s, %s)
        """
        
        values = (crime_id, victim_id, 'minor')  # Default injury level
        
        self.cursor.execute(sql, values)

    def _insert_crime_criminal(self, crime_id, criminal_id):
        """Insert crime-criminal relationship using hardcoded SQL"""
        sql = """
        INSERT INTO crime_criminal (crime_id, criminal_id, notes)
        VALUES (%s, %s, %s)
        """
        
        values = (crime_id, criminal_id, 'Initial report')
        
        self.cursor.execute(sql, values)

    def _insert_crime_weapon(self, crime_id, weapon_id):
        """Insert crime-weapon relationship using hardcoded SQL"""
        sql = """
        INSERT INTO crime_weapon (crime_id, weapon_id, usage_detail)
        VALUES (%s, %s, %s)
        """
        
        values = (crime_id, weapon_id, 'Used in crime')
        
        self.cursor.execute(sql, values)

    def _insert_crime_witness(self, crime_id, witness_id):
        """Insert crime-witness relationship using hardcoded SQL"""
        sql = """
        INSERT INTO crime_witness (crime_id, witness_id, statement_status)
        VALUES (%s, %s, %s)
        """
        
        values = (crime_id, witness_id, 'pending')
        
        self.cursor.execute(sql, values)

    def get_crime_by_id(self, crime_id):
        """Get crime details by ID using hardcoded SQL"""
        sql = """
        SELECT c.crime_id, c.crime_type, c.description, c.date_time, c.status, c.created_at,
               l.area_name, l.city, l.latitude, l.longitude,
               d.district_name
        FROM crime c
        JOIN location l ON c.location_id = l.location_id
        JOIN district d ON l.district_id = d.district_id
        WHERE c.crime_id = %s
        """
        
        self.cursor.execute(sql, (crime_id,))
        return self.cursor.fetchone()

    def get_all_crimes(self):
        """Get all crimes using hardcoded SQL"""
        sql = """
        SELECT c.crime_id, c.crime_type, c.description, c.date_time, c.status, c.created_at,
               l.area_name, l.city, l.latitude, l.longitude,
               d.district_name
        FROM crime c
        JOIN location l ON c.location_id = l.location_id
        JOIN district d ON l.district_id = d.district_id
        ORDER BY c.created_at DESC
        """
        
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_crime_status(self, crime_id, new_status, notes, changed_by):
        """Update crime status and add to history using hardcoded SQL"""
        try:
            self.connection.start_transaction()
            
            # Update crime status
            update_sql = "UPDATE crime SET status = %s WHERE crime_id = %s"
            self.cursor.execute(update_sql, (new_status, crime_id))
            
            # Add to status history
            history_sql = """
            INSERT INTO case_status_history (crime_id, status, notes, changed_at, changed_by)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            history_values = (
                crime_id, new_status, notes, datetime.datetime.now(), changed_by
            )
            
            self.cursor.execute(history_sql, history_values)
            self.connection.commit()
            
            return {'success': True, 'message': 'Status updated successfully'}
            
        except Error as e:
            self.connection.rollback()
            return {'success': False, 'error': str(e)}

    def assign_case(self, crime_id, user_id, duty_role):
        """Assign case to officer using hardcoded SQL"""
        sql = """
        INSERT INTO case_assignment (user_id, crime_id, duty_role, assigned_at)
        VALUES (%s, %s, %s, %s)
        """
        
        values = (user_id, crime_id, duty_role, datetime.datetime.now())
        
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
            return {'success': True, 'assignment_id': self.cursor.lastrowid}
        except Error as e:
            return {'success': False, 'error': str(e)}

# Example usage function
def insert_sample_crime():
    """Example function to insert sample crime data"""
    
    # Sample crime data matching the form structure
    sample_crime_data = {
        'location': {
            'district_id': 1,  # Dhaka
            'area_name': 'Dhanmondi',
            'city': 'Dhaka',
            'latitude': 23.7465,
            'longitude': 90.3760
        },
        'crime': {
            'crime_type': 'theft',
            'description': 'Mobile phone stolen from pedestrian',
            'date_time': '2025-01-15 14:30:00',
            'status': 'reported'
        },
        'victim': {
            'full_name': 'John Doe',
            'dob': '1990-05-15',
            'gender': 'M',
            'address': 'House 15, Road 5, Dhanmondi',
            'phone_number': '+880123456789',
            'email': 'john.doe@email.com',
            'injury_details': 'No physical injuries'
        },
        'criminal': {
            'full_name': 'Unknown Suspect',
            'alias_name': 'Street Thief',
            'dob': None,
            'gender': 'M',
            'address': 'Unknown',
            'marital_status': 'unknown',
            'previous_crimes': 'Multiple theft cases reported in the area'
        },
        'weapon': {
            'weapon_name': 'None',
            'weapon_type': 'other',
            'description': 'No weapon used',
            'serial_number': None
        },
        'witness': {
            'full_name': 'Jane Smith',
            'phone_number': '+880987654321',
            'protection_flag': False
        }
    }
    
    # Initialize database manager
    db_manager = CrimeDatabaseManager(
        host='localhost',
        database='mysafety',
        user='root',
        password='your_password_here'  # Update with your actual password
    )
    
    if db_manager.connection and db_manager.connection.is_connected():
        # Insert the crime data
        result = db_manager.insert_crime_data(sample_crime_data)
        
        if result['success']:
            print("Crime data inserted successfully!")
            print(f"Crime ID: {result['crime_id']}")
            print(f"Location ID: {result['location_id']}")
            if result['victim_id']:
                print(f"Victim ID: {result['victim_id']}")
            if result['criminal_id']:
                print(f"Criminal ID: {result['criminal_id']}")
            if result['weapon_id']:
                print(f"Weapon ID: {result['weapon_id']}")
            if result['witness_id']:
                print(f"Witness ID: {result['witness_id']}")
        else:
            print(f"Error inserting crime data: {result['error']}")
        
        # Close connection
        db_manager.close_connection()
    else:
        print("Failed to connect to database")

if __name__ == "__main__":
    # Run the example
    insert_sample_crime()
