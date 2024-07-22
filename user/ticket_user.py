from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

ticket_user_bp = Blueprint('ticket_user_bp', __name__)

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tiger',
    'database': 'airline'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@ticket_user_bp.route('/user/ticket_user', methods=['GET', 'POST'])
def ticket_user():
    if request.method == 'POST':
        try:
            # Get form data
            origin = request.form['origin']
            dest = request.form['dest']
            tycl = request.form['tycl']
            tyt = request.form['tyt']
            tm=request.form['tm']
            jd2=request.form['jd']
            rd2 = request.form.get('rd', '').strip()

            input_format = "%Y-%m-%d"
            output_format = "%d/%b/%Y"
            jd = datetime.strptime(jd2, input_format).strftime(output_format)
            rd = datetime.strptime(rd2, input_format).strftime(output_format) if rd2 else None

            # Database operations
            con = get_db_connection()
            cursor = con.cursor()

            # Check for flights
            flight_query = """
                SELECT * FROM flights 
                WHERE FIND_IN_SET(%s, airports) AND FIND_IN_SET(%s, airports) 
                AND FIND_IN_SET(%s, class) AND FIND_IN_SET(%s, ticket_type)
            """
            cursor.execute(flight_query, (origin, dest, tycl, tyt))
            flights = cursor.fetchall()

            if flights:
                # Check for fares
                fare_query = """
                    SELECT fare, km FROM airplane_fare 
                    WHERE FIND_IN_SET(%s, airport) AND FIND_IN_SET(%s, airport) > 0 
                    LIMIT 1
                """
                cursor.execute(fare_query, (origin, dest))
                fare_result = cursor.fetchone()

                cursor.close()
                con.close()

                if fare_result:
                    base_fare = fare_result[0]
                    km = fare_result[1]
                    class_charge = 0
                    quuota_discount = 0

                    # Calculate additional charges based on class
                    if tycl == "FIRST CLASS":
                        class_charge = 1500
                    elif tycl == "BUSINESS CLASS":
                        class_charge = 2500
                    elif tycl == "PREMIUM ECONOMY":
                        class_charge = 1600
                    elif tycl == "ECONOMY":
                        class_charge = 800
                    bs=base_fare
                    base_fare += class_charge #with adding class charges 

                    # Calculate additional charges based on ticket type
                    if tyt == "GENERAL":
                        quuota_discount = 0
                    elif tyt == "DEFENCE":
                        
                        quuota_discount = -1000
                    elif tyt == "GOVT EMPLOYEE":
                       
                        quuota_discount = -500
                    elif tyt == "SENIOR CITIZEN":
                       
                        quuota_discount = -600
                    elif tyt == "STUDENT":
                        quuota_discount = -600
                    tf = base_fare + quuota_discount # with subtraction of quota   
                    
                       # Calculating the trip mode, if one way total fare = total fare, if round trip total fare = total fare * 2
                    tmf = tf
                    tmf1 = 0
                    if tm == "ROUND TRIP":
                        tmf = tf * 2
                        tmf1 = tmf * 0.01
                        tmf -= tmf1

                    return render_template(
                        'user/ticket_user1.html', 
                        flights=flights, 
                        base_fare=base_fare,
                        bs=bs,
                        class_charge=class_charge,
                        tf=tf,
                        quuota_discount=quuota_discount,
                        km=km,
                        tm=tm,
                        jd=jd,
                        rd=rd,
                        tmf1=tmf1,
                        tmf=tmf
                    )
                else:
                    error_message = 'No fares found for the selected route.'
                    flash(error_message)
                    return redirect(url_for('user.ticket_user_bp.ticket_user'))
            else:
                cursor.close()
                con.close()
                error_message = 'No flights found for the selected route.'
                flash(error_message)
                return redirect(url_for('user.ticket_user_bp.ticket_user'))

        except Exception as ex:
            print(ex)
            error_message = 'An error occurred while processing your request. Please try again.'
            flash(error_message)
            return redirect(url_for('user.ticket_user_bp.ticket_user'))
    
    return render_template('user/ticket_user.html')
