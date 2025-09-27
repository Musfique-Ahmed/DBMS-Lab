from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import datetime
import json

app = Flask(__name__)

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

# Flask Routes
@app.route('/')
def index():
    """Serve the admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/api/crimes', methods=['POST'])
def create_crime():
    """Create a new crime via API"""
    try:
        # Get JSON data from request
        crime_data = request.get_json()
        
        # Initialize database manager
        db_manager = CrimeDatabaseManager(
            host='localhost',
            database='mysafety',
            user='root',
            password='your_password_here'  # Update with your actual password
        )
        
        if not db_manager.connection or not db_manager.connection.is_connected():
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        # Insert the crime data
        result = db_manager.insert_crime_data(crime_data)
        
        # Close connection
        db_manager.close_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Crime created successfully',
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/crimes', methods=['GET'])
def get_crimes():
    """Get all crimes"""
    try:
        db_manager = CrimeDatabaseManager(
            host='localhost',
            database='mysafety',
            user='root',
            password='your_password_here'  # Update with your actual password
        )
        
        if not db_manager.connection or not db_manager.connection.is_connected():
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        # Get all crimes using hardcoded SQL
        sql = """
        SELECT c.crime_id, c.crime_type, c.description, c.date_time, c.status, c.created_at,
               l.area_name, l.city, l.latitude, l.longitude,
               d.district_name
        FROM crime c
        JOIN location l ON c.location_id = l.location_id
        JOIN district d ON l.district_id = d.district_id
        ORDER BY c.created_at DESC
        """
        
        db_manager.cursor.execute(sql)
        crimes = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries
        crime_list = []
        for crime in crimes:
            crime_dict = {
                'crime_id': crime[0],
                'crime_type': crime[1],
                'description': crime[2],
                'date_time': crime[3].isoformat() if crime[3] else None,
                'status': crime[4],
                'created_at': crime[5].isoformat() if crime[5] else None,
                'area_name': crime[6],
                'city': crime[7],
                'latitude': crime[8],
                'longitude': crime[9],
                'district_name': crime[10]
            }
            crime_list.append(crime_dict)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'crimes': crime_list
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/complaints', methods=['GET'])
def get_complaints():
    """Get all complaints"""
    try:
        db_manager = CrimeDatabaseManager(
            host='localhost',
            database='mysafety',
            user='root',
            password='your_password_here'  # Update with your actual password
        )
        
        if not db_manager.connection or not db_manager.connection.is_connected():
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        # Get all complaints using hardcoded SQL
        sql = """
        SELECT complaint_id, reported_at, reporter_contact, description, channel, status
        FROM complaint
        ORDER BY reported_at DESC
        """
        
        db_manager.cursor.execute(sql)
        complaints = db_manager.cursor.fetchall()
        
        # Convert to list of dictionaries
        complaint_list = []
        for complaint in complaints:
            complaint_dict = {
                'complaint_id': complaint[0],
                'reported_at': complaint[1].isoformat() if complaint[1] else None,
                'reporter_contact': complaint[2],
                'description': complaint[3],
                'channel': complaint[4],
                'status': complaint[5]
            }
            complaint_list.append(complaint_dict)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'complaints': complaint_list
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/complaints/<int:complaint_id>/verify', methods=['POST'])
def verify_complaint(complaint_id):
    """Verify a complaint"""
    try:
        db_manager = CrimeDatabaseManager(
            host='localhost',
            database='mysafety',
            user='root',
            password='your_password_here'  # Update with your actual password
        )
        
        if not db_manager.connection or not db_manager.connection.is_connected():
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        # Update complaint status using hardcoded SQL
        sql = "UPDATE complaint SET status = 'verified' WHERE complaint_id = %s"
        db_manager.cursor.execute(sql, (complaint_id,))
        
        if db_manager.cursor.rowcount > 0:
            db_manager.connection.commit()
            db_manager.close_connection()
            return jsonify({'success': True, 'message': 'Complaint verified successfully'}), 200
        else:
            db_manager.close_connection()
            return jsonify({'success': False, 'error': 'Complaint not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/case-assignments', methods=['POST'])
def assign_case():
    """Assign case to officer"""
    try:
        assignment_data = request.get_json()
        
        db_manager = CrimeDatabaseManager(
            host='localhost',
            database='mysafety',
            user='root',
            password='your_password_here'  # Update with your actual password
        )
        
        if not db_manager.connection or not db_manager.connection.is_connected():
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        # Insert case assignment using hardcoded SQL
        sql = """
        INSERT INTO case_assignment (user_id, crime_id, duty_role, assigned_at)
        VALUES (%s, %s, %s, %s)
        """
        
        values = (
            assignment_data['user_id'],
            assignment_data['crime_id'],
            assignment_data['duty_role'],
            datetime.datetime.now()
        )
        
        db_manager.cursor.execute(sql, values)
        assignment_id = db_manager.cursor.lastrowid
        
        db_manager.connection.commit()
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'message': 'Case assigned successfully',
            'assignment_id': assignment_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
