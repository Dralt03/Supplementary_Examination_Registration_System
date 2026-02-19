import os
from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "supplementary_exam_db"),
    )


def ensure_tables_exist():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student (
                roll_no INT PRIMARY KEY,
                name VARCHAR(45) NOT NULL,
                branch VARCHAR(45) NOT NULL,
                semester VARCHAR(45) NOT NULL,
                email VARCHAR(100) UNIQUE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_code VARCHAR(45) PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                department VARCHAR(45) NOT NULL,
                credits VARCHAR(45) NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS grades (
                roll_no INT NOT NULL,
                course_code VARCHAR(45) NOT NULL,
                department VARCHAR(45) NOT NULL,
                credits VARCHAR(45) NOT NULL,
                grade_id VARCHAR(45) NOT NULL,
                PRIMARY KEY (roll_no, course_code)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payment (
                transaction_no INT PRIMARY KEY,
                roll_no INT NOT NULL,
                course_code VARCHAR(45) NOT NULL,
                amount INT NOT NULL,
                payment_date DATE NOT NULL,
                payment_status VARCHAR(45) NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS supplementary (
                supplementary_id INT PRIMARY KEY,
                roll_no INT NOT NULL,
                transaction_no INT NOT NULL,
                course_code VARCHAR(45) NOT NULL,
                registration_date DATE NOT NULL
            )
            """
        )

        connection.commit()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_procedure(query, params):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        return True, "Procedure executed successfully"
    except Error as err:
        if err.errno == 1305 and query.strip().upper().startswith("CALL ADD_STUDENT"):
            try:
                if cursor:
                    cursor.close()
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO student (roll_no, name, branch, semester, email) VALUES (%s, %s, %s, %s, %s)",
                    params,
                )
                connection.commit()
                return True, "Student added successfully"
            except Error as fallback_err:
                return False, str(fallback_err)
        return False, str(err)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/api/add-student", methods=["POST"])
def add_student():
    data = request.get_json()
    success, message = execute_procedure(
        "CALL add_student(%s, %s, %s, %s, %s)",
        (
            data["roll_no"],
            data["name"],
            data["branch"],
            data["semester"],
            data["email"],
        ),
    )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@app.route("/api/add-course", methods=["POST"])
def add_course():
    data = request.get_json()
    success, message = execute_procedure(
        "CALL add_course(%s, %s, %s, %s)",
        (data["course_code"], data["course_name"], data["department"], data["credits"]),
    )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@app.route("/api/add-grade", methods=["POST"])
def add_grade():
    data = request.get_json()
    success, message = execute_procedure(
        "CALL add_grade(%s, %s, %s, %s, %s)",
        (
            data["roll_no"],
            data["course_code"],
            data["department"],
            data["credits"],
            data["grade"],
        ),
    )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@app.route("/api/add-payment", methods=["POST"])
def add_payment():
    data = request.get_json()
    success, message = execute_procedure(
        "CALL add_payment(%s, %s, %s, %s, %s, %s)",
        (
            data["transaction_no"],
            data["roll_no"],
            data["course_code"],
            data["amount"],
            data["payment_date"],
            data["payment_status"],
        ),
    )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


@app.route("/api/register-supplementary", methods=["POST"])
def register_supplementary():
    data = request.get_json()
    success, message = execute_procedure(
        "CALL register_supplementary(%s, %s, %s, %s, %s)",
        (
            data["supplementary_id"],
            data["roll_no"],
            data["transaction_no"],
            data["course_code"],
            data["registration_date"],
        ),
    )
    return jsonify({"success": success, "message": message}), (200 if success else 400)


if __name__ == "__main__":
    ensure_tables_exist()
    app.run(debug=True, port=int(os.getenv("PORT", "3000")))
