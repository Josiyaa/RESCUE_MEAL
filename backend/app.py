from flask import Flask, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# FRONTEND CONFIGURATION
# ============================================================

FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "frontend"
)


# ============================================================
# SERVE FRONTEND FILES
# ============================================================

@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)


@app.route("/dashboard")
def dashboard():
    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


# ============================================================
# MYSQL DATABASE CONNECTION
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="josu2003",
        database="rescuemeal"
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return """
    <h1>RescueMeal Backend is Running!</h1>

    <p>
        Open
        <a href="/dashboard">
            RescueMeal Website
        </a>
    </p>
    """


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

@app.route("/api/test-db", methods=["GET"])
def test_database():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()

        return {
            "success": True,
            "message": "Database connected successfully!",
            "tables": [table[0] for table in tables]
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database connection failed.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# USER REGISTRATION
# ============================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Request body is required."
        }, 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    phone = data.get("phone")
    address = data.get("address")

    if not name or not email or not password or not role:

        return {
            "success": False,
            "message": "Name, email, password and role are required."
        }, 400

    if role not in ["donor", "ngo", "admin"]:

        return {
            "success": False,
            "message": "Invalid role. Use donor, ngo or admin."
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check whether email already exists
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return {
                "success": False,
                "message": "Email already exists."
            }, 409

        hashed_password = generate_password_hash(password)

        query = """
            INSERT INTO users
            (
                name,
                email,
                password,
                role,
                phone,
                address
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            hashed_password,
            role,
            phone,
            address
        )

        cursor.execute(query, values)

        connection.commit()

        user_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Registration successful!",
            "user_id": user_id
        }, 201

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# USER LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Request body is required."
        }, 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return {
            "success": False,
            "message": "Email and password are required."
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user is None:

            return {
                "success": False,
                "message": "Invalid email or password."
            }, 401

        if not check_password_hash(
            user["password"],
            password
        ):

            return {
                "success": False,
                "message": "Invalid email or password."
            }, 401

        return {
            "success": True,
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CREATE FOOD DONATION
# ============================================================

@app.route("/api/donations", methods=["POST"])
def create_donation():

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Request body is required."
        }, 400

    donor_id = data.get("donor_id")
    food_name = data.get("food_name")
    quantity = data.get("quantity")
    food_type = data.get("food_type")
    description = data.get("description")
    preparation_time = data.get("preparation_time")
    expiry_time = data.get("expiry_time")
    pickup_address = data.get("pickup_address")

    if (
        not donor_id
        or not food_name
        or quantity is None
        or not pickup_address
    ):

        return {
            "success": False,
            "message": "Donor ID, food name, quantity and pickup address are required."
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # CHECK DONOR
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
            AND role = 'donor'
            """,
            (donor_id,)
        )

        donor = cursor.fetchone()

        if donor is None:

            return {
                "success": False,
                "message": "Donor not found."
            }, 404

        # ----------------------------------------------------
        # INSERT DONATION
        # ----------------------------------------------------

        query = """
            INSERT INTO food_donations
            (
                donor_id,
                food_name,
                quantity,
                food_type,
                description,
                preparation_time,
                expiry_time,
                pickup_address,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'available'
            )
        """

        values = (
            donor_id,
            food_name,
            quantity,
            food_type,
            description,
            preparation_time,
            expiry_time,
            pickup_address
        )

        cursor.execute(
            query,
            values
        )

        connection.commit()

        donation_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Food donation created successfully!",
            "donation_id": donation_id
        }, 201

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# VIEW AVAILABLE FOOD DONATIONS
# ============================================================

@app.route("/api/donations", methods=["GET"])
def get_donations():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                food_donations.id,
                food_donations.food_name,
                food_donations.quantity,
                food_donations.food_type,
                food_donations.description,
                food_donations.preparation_time,
                food_donations.expiry_time,
                food_donations.pickup_address,
                food_donations.status,
                food_donations.created_at,
                users.name AS donor_name
            FROM food_donations

            JOIN users
                ON food_donations.donor_id = users.id

            WHERE food_donations.status = 'available'

            ORDER BY
                food_donations.created_at DESC
        """

        cursor.execute(query)

        donations = cursor.fetchall()

        return {
            "success": True,
            "donations": donations
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET DONATIONS OF A PARTICULAR DONOR
# ============================================================

@app.route(
    "/api/donations/donor/<int:donor_id>",
    methods=["GET"]
)
def get_donor_donations(donor_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # CHECK DONOR
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = %s
            AND role = 'donor'
            """,
            (donor_id,)
        )

        donor = cursor.fetchone()

        if donor is None:

            return {
                "success": False,
                "message": "Donor not found."
            }, 404

        # ----------------------------------------------------
        # GET DONATIONS
        # ----------------------------------------------------

        query = """
            SELECT
                id,
                food_name,
                quantity,
                food_type,
                description,
                preparation_time,
                expiry_time,
                pickup_address,
                status,
                created_at
            FROM food_donations
            WHERE donor_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(
            query,
            (donor_id,)
        )

        donations = cursor.fetchall()

        return {
            "success": True,
            "donations": donations
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# NGO CLAIM FOOD DONATION
# ============================================================

@app.route(
    "/api/donations/<int:donation_id>/claim",
    methods=["POST"]
)
def claim_donation(donation_id):

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Request body is required."
        }, 400

    ngo_id = data.get("ngo_id")

    if not ngo_id:

        return {
            "success": False,
            "message": "NGO ID is required."
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # CHECK DONATION
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                status
            FROM food_donations
            WHERE id = %s
            """,
            (donation_id,)
        )

        donation = cursor.fetchone()

        if donation is None:

            return {
                "success": False,
                "message": "Donation not found."
            }, 404

        if donation["status"] != "available":

            return {
                "success": False,
                "message": "This donation is no longer available."
            }, 400

        # ----------------------------------------------------
        # CHECK NGO
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM ngos
            WHERE id = %s
            """,
            (ngo_id,)
        )

        ngo = cursor.fetchone()

        if ngo is None:

            return {
                "success": False,
                "message": "NGO not found."
            }, 404

        # ----------------------------------------------------
        # CREATE CLAIM
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO donation_claims
            (
                donation_id,
                ngo_id,
                claim_status
            )
            VALUES
            (
                %s,
                %s,
                'claimed'
            )
            """,
            (
                donation_id,
                ngo_id
            )
        )

        claim_id = cursor.lastrowid

        # ----------------------------------------------------
        # UPDATE DONATION STATUS
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE food_donations
            SET status = 'claimed'
            WHERE id = %s
            """,
            (donation_id,)
        )

        connection.commit()

        return {
            "success": True,
            "message": "Food donation claimed successfully!",
            "claim_id": claim_id,
            "donation_id": donation_id,
            "ngo_id": ngo_id
        }, 201

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# MARK DONATION AS COLLECTED
# ============================================================

@app.route(
    "/api/donations/<int:donation_id>/collect",
    methods=["POST"]
)
def collect_donation(donation_id):

    data = request.get_json()

    if not data:

        return {
            "success": False,
            "message": "Request body is required."
        }, 400

    ngo_id = data.get("ngo_id")

    if not ngo_id:

        return {
            "success": False,
            "message": "NGO ID is required."
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # ----------------------------------------------------
        # FIND CLAIM
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                claim_status
            FROM donation_claims
            WHERE donation_id = %s
            AND ngo_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                donation_id,
                ngo_id
            )
        )

        claim = cursor.fetchone()

        if claim is None:

            return {
                "success": False,
                "message": "No claim found for this donation."
            }, 404

        # ----------------------------------------------------
        # CHECK CLAIM STATUS
        # ----------------------------------------------------

        if claim["claim_status"] != "claimed":

            return {
                "success": False,
                "message": "This donation cannot be marked as collected."
            }, 400

        # ----------------------------------------------------
        # UPDATE CLAIM
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE donation_claims
            SET
                claim_status = 'collected',
                collected_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (claim["id"],)
        )

        # ----------------------------------------------------
        # UPDATE DONATION
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE food_donations
            SET status = 'collected'
            WHERE id = %s
            """,
            (donation_id,)
        )

        connection.commit()

        return {
            "success": True,
            "message": "Food donation marked as collected!",
            "donation_id": donation_id,
            "ngo_id": ngo_id,
            "claim_id": claim["id"]
        }, 200

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET NGO CLAIMED DONATIONS
# ============================================================

@app.route(
    "/api/ngo/<int:ngo_id>/claims",
    methods=["GET"]
)
def get_ngo_claims(ngo_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                donation_claims.id AS claim_id,
                donation_claims.donation_id,
                donation_claims.ngo_id,
                donation_claims.claim_status,

                food_donations.food_name,
                food_donations.quantity,
                food_donations.food_type,
                food_donations.description,
                food_donations.pickup_address,
                food_donations.status

            FROM donation_claims

            JOIN food_donations
                ON donation_claims.donation_id =
                   food_donations.id

            WHERE donation_claims.ngo_id = %s

            ORDER BY
                donation_claims.id DESC
        """

        cursor.execute(
            query,
            (ngo_id,)
        )

        claims = cursor.fetchall()

        return {
            "success": True,
            "claims": claims
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ADMIN - STATISTICS
# ============================================================

@app.route(
    "/api/admin/stats",
    methods=["GET"]
)
def admin_stats():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        # Total users
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            """
        )

        total_users = cursor.fetchone()[0]

        # Total donors
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE role = 'donor'
            """
        )

        total_donors = cursor.fetchone()[0]

        # Total NGOs
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE role = 'ngo'
            """
        )

        total_ngos = cursor.fetchone()[0]

        # Total donations
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM food_donations
            """
        )

        total_donations = cursor.fetchone()[0]

        # Available
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM food_donations
            WHERE status = 'available'
            """
        )

        available = cursor.fetchone()[0]

        # Claimed
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM food_donations
            WHERE status = 'claimed'
            """
        )

        claimed = cursor.fetchone()[0]

        # Collected
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM food_donations
            WHERE status = 'collected'
            """
        )

        collected = cursor.fetchone()[0]

        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_donors": total_donors,
                "total_ngos": total_ngos,
                "total_donations": total_donations,
                "available": available,
                "claimed": claimed,
                "collected": collected
            }
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ADMIN - ALL USERS
# ============================================================

@app.route(
    "/api/admin/users",
    methods=["GET"]
)
def admin_users():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                phone,
                address
            FROM users
            ORDER BY id DESC
            """
        )

        users = cursor.fetchall()

        return {
            "success": True,
            "users": users
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ADMIN - ALL NGOS
# ============================================================

@app.route(
    "/api/admin/ngos",
    methods=["GET"]
)
def admin_ngos():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Try to get NGO information from ngos table
        cursor.execute(
            """
            SELECT *
            FROM ngos
            ORDER BY id DESC
            """
        )

        ngos = cursor.fetchall()

        return {
            "success": True,
            "ngos": ngos
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ADMIN - ALL FOOD DONATIONS
# ============================================================

@app.route(
    "/api/admin/donations",
    methods=["GET"]
)
def admin_donations():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
            SELECT
                food_donations.id,
                food_donations.food_name,
                food_donations.quantity,
                food_donations.food_type,
                food_donations.description,
                food_donations.preparation_time,
                food_donations.expiry_time,
                food_donations.pickup_address,
                food_donations.status,
                food_donations.created_at,

                users.name AS donor_name,
                users.email AS donor_email

            FROM food_donations

            JOIN users
                ON food_donations.donor_id =
                   users.id

            ORDER BY
                food_donations.created_at DESC
        """

        cursor.execute(query)

        donations = cursor.fetchall()

        return {
            "success": True,
            "donations": donations
        }, 200

    except mysql.connector.Error as error:

        return {
            "success": False,
            "message": "Database error.",
            "error": str(error)
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print(
        "Starting RescueMeal Flask server..."
    )

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )

