from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_from_directory
)
from decimal import Decimal, InvalidOperation
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
import mysql.connector
import re
import smtplib
import secrets
import time
from email.message import EmailMessage

app = Flask(__name__)
app.config["RESUME_UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "uploads",
    "resumes"
)

os.makedirs(app.config["RESUME_UPLOAD_FOLDER"], exist_ok=True)
# =========================================================
# FLASK SECRET KEY
# =========================================================

app.secret_key = "campus_connect_secret_key"
MAIL_USERNAME = os.environ.get("CAMPUSCONNECT_MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("CAMPUSCONNECT_MAIL_PASSWORD")
MAIL_USERNAME = os.environ.get("CAMPUSCONNECT_MAIL_USERNAME" )
MAIL_PASSWORD = os.environ.get("CAMPUSCONNECT_MAIL_PASSWORD" )
password_reset_codes = {}


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_HOST = "127.0.0.1"
DB_PORT = 1234
DB_USER = "root"
DB_PASSWORD = "trisha"
DB_NAME = "campus_placement"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")


# =========================================================
# STUDENT REGISTRATION
# =========================================================

@app.route("/student_register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get(
            "confirm_password", ""
        ).strip()

        # -------------------------
        # NAME VALIDATION
        # -------------------------

        if not name:

            flash("Please enter your full name.", "danger")

            return redirect(url_for("student_register"))

        if not re.fullmatch(r"[A-Za-z ]+", name):

            flash(
                "Name should contain only letters and spaces.",
                "danger"
            )

            return redirect(url_for("student_register"))

        # -------------------------
        # EMAIL VALIDATION
        # -------------------------

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(url_for("student_register"))

        # -------------------------
        # PASSWORD VALIDATION
        # -------------------------

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )

            return redirect(url_for("student_register"))

        if not re.search(r"[A-Z]", password):

            flash(
                "Password must contain one uppercase letter.",
                "danger"
            )

            return redirect(url_for("student_register"))

        if not re.search(r"[a-z]", password):

            flash(
                "Password must contain one lowercase letter.",
                "danger"
            )

            return redirect(url_for("student_register"))

        if not re.search(r"[0-9]", password):

            flash(
                "Password must contain one number.",
                "danger"
            )

            return redirect(url_for("student_register"))

        if not re.search(r"[^A-Za-z0-9]", password):

            flash(
                "Password must contain one special character.",
                "danger"
            )

            return redirect(url_for("student_register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("student_register"))

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            # Check duplicate email

            cursor.execute(
                "SELECT user_id FROM users WHERE email=%s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "Email is already registered.",
                    "danger"
                )

                return redirect(
                    url_for("student_register")
                )

            # Insert student

            sql = """
                INSERT INTO users
                (full_name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                name,
                email,
                password,
                "Student"
            )

            cursor.execute(sql, values)

            connection.commit()

            flash(
                "Student registration successful!",
                "success"
            )

            return redirect(url_for("login"))

        except mysql.connector.Error as error:

            if connection:
                connection.rollback()

            print("Student Registration Error:", error)

            flash(
                "Database error. Please check MySQL connection.",
                "danger"
            )

            return redirect(
                url_for("student_register")
            )

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("student_register.html")


# =========================================================
# RECRUITER REGISTRATION
# =========================================================

@app.route("/recruiter_register", methods=["GET", "POST"])
def recruiter_register():

    if request.method == "POST":

        name = (
    request.form.get("hr_name", "").strip()
    or request.form.get("name", "").strip()
)
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get(
            "confirm_password", ""
        ).strip()

        if not name:

            flash(
                "Please enter your full name.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if not re.fullmatch(r"[A-Za-z ]+", name):

            flash(
                "Name should contain only letters and spaces.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if not re.search(r"[A-Z]", password):

            flash(
                "Password needs one uppercase letter.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if not re.search(r"[a-z]", password):

            flash(
                "Password needs one lowercase letter.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if not re.search(r"[0-9]", password):

            flash(
                "Password needs one number.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if not re.search(r"[^A-Za-z0-9]", password):

            flash(
                "Password needs one special character.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT user_id FROM users WHERE email=%s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "Email is already registered.",
                    "danger"
                )

                return redirect(
                    url_for("recruiter_register")
                )

            sql = """
                INSERT INTO users
                (full_name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """

            values = (
                name,
                email,
                password,
                "Recruiter"
            )

            cursor.execute(sql, values)

            connection.commit()

            flash(
                "Recruiter registration successful!",
                "success"
            )

            return redirect(url_for("login"))

        except mysql.connector.Error as error:

            if connection:
                connection.rollback()

            print("Recruiter Registration Error:", error)

            flash(
                "Database error. Please check MySQL connection.",
                "danger"
            )

            return redirect(
                url_for("recruiter_register")
            )

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("recruiter_register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip()

        password = request.form.get(
            "password", ""
        ).strip()

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            sql = """
                SELECT user_id,
                       full_name,
                       email,
                       password,
                       role,
                       is_active
                FROM users
                WHERE email=%s
                AND password=%s
            """

            cursor.execute(
                sql,
                (email, password)
            )

            user = cursor.fetchone()

            if user is None:

                flash(
                    "Invalid email or password.",
                    "danger"
                )

                return redirect(url_for("login"))
            if not user["is_active"]:
                 flash("This account has been deactivated. Contact the administrator.", "danger")
                 return redirect(url_for("login"))
            # Store login session

            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["name"] = user["full_name"]
            session["role"] = user["role"]
            session["email"] = user["email"]

            # Redirect according to role

            if user["role"].lower() == "student":

                return redirect(
                    url_for("dashboard")
                )

            elif user["role"].lower() == "recruiter":

                return redirect(
                    url_for("recruiter_dashboard")
                )
            elif user["role"].lower() == "admin":
                return redirect(url_for("admin_dashboard"))
            else:

                flash(
                    "Unknown user role.",
                    "danger"
                )

                return redirect(
                    url_for("login")
                )

        except mysql.connector.Error as error:

            print("Login Database Error:", error)

            flash(
                "Database connection error.",
                "danger"
            )

            return redirect(url_for("login"))

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template("login.html")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Student":
        return redirect(url_for("login"))

    return render_template("dashboard.html", name=session["full_name"])


# =========================================================
# STUDENT PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
            SELECT
                u.user_id,
                u.full_name,
                u.email,
                sp.phone,
                sp.course,
                sp.college,
                sp.graduation_year,
                sp.cgpa,
                sp.skills,
                sp.bio,
                sp.resume_filename
            FROM users u
            LEFT JOIN student_profiles sp
                ON u.user_id = sp.user_id
            WHERE u.user_id = %s
        """

        cursor.execute(sql, (session["user_id"],))
        student = cursor.fetchone()

        if not student:
            flash("Profile not found.", "danger")
            return redirect(url_for("dashboard"))

        return render_template("profile.html", student=student)

    except mysql.connector.Error as error:
        print("Profile Error:", error)
        flash("Unable to load profile.", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# EDIT STUDENT PROFILE
# =========================================================

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None
    new_resume_path = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == "POST":
            phone = request.form.get("phone", "").strip()
            course = request.form.get("course", "").strip()
            college = request.form.get("college", "").strip()
            graduation_year = request.form.get(
                "graduation_year", ""
            ).strip()
            cgpa_input = request.form.get("cgpa", "").strip()
            skills = request.form.get("skills", "").strip()
            bio = request.form.get("bio", "").strip()

            # CGPA validate karo
            cgpa = None

            if cgpa_input:
                try:
                    cgpa = Decimal(cgpa_input)
                except InvalidOperation:
                    flash("Enter a valid CGPA.", "danger")
                    return redirect(url_for("edit_profile"))

                if cgpa < 0 or cgpa > 10:
                    flash("CGPA must be between 0 and 10.", "danger")
                    return redirect(url_for("edit_profile"))

            # Existing profile aur resume check karo
            cursor.execute(
                """
                SELECT profile_id, resume_filename
                FROM student_profiles
                WHERE user_id = %s
                """,
                (session["user_id"],)
            )

            profile_exists = cursor.fetchone()

            if profile_exists:
                old_resume_filename = profile_exists["resume_filename"]
            else:
                old_resume_filename = None

            resume_filename = old_resume_filename
            resume_file = request.files.get("resume")

            # Naya resume mila ho toh validate karke save karo
            if resume_file and resume_file.filename:
                safe_name = secure_filename(resume_file.filename)

                if not safe_name.lower().endswith(".pdf"):
                    flash("Resume must be a PDF file.", "danger")
                    return redirect(url_for("edit_profile"))

                resume_file.stream.seek(0, os.SEEK_END)
                file_size = resume_file.stream.tell()
                resume_file.stream.seek(0)

                if file_size > 5 * 1024 * 1024:
                    flash("Resume must be smaller than 5 MB.", "danger")
                    return redirect(url_for("edit_profile"))

                file_header = resume_file.stream.read(5)
                resume_file.stream.seek(0)

                if file_header != b"%PDF-":
                    flash("The selected file is not a valid PDF.", "danger")
                    return redirect(url_for("edit_profile"))

                resume_filename = (
                    f"student_{session['user_id']}_{uuid.uuid4().hex}.pdf"
                )

                new_resume_path = os.path.join(
                    app.config["RESUME_UPLOAD_FOLDER"],
                    resume_filename
                )

                resume_file.save(new_resume_path)

            # Existing profile update karo
            if profile_exists:
                cursor.execute(
                    """
                    UPDATE student_profiles
                    SET phone = %s,
                        course = %s,
                        college = %s,
                        graduation_year = %s,
                        cgpa = %s,
                        skills = %s,
                        bio = %s,
                        resume_filename = %s
                    WHERE user_id = %s
                    """,
                    (
                        phone,
                        course,
                        college,
                        graduation_year or None,
                        cgpa,
                        skills,
                        bio,
                        resume_filename,
                        session["user_id"]
                    )
                )

            # Profile nahi hai toh naya row banao
            else:
                cursor.execute(
                    """
                    INSERT INTO student_profiles
                    (
                        user_id,
                        phone,
                        course,
                        college,
                        graduation_year,
                        cgpa,
                        skills,
                        bio,
                        resume_filename
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session["user_id"],
                        phone,
                        course,
                        college,
                        graduation_year or None,
                        cgpa,
                        skills,
                        bio,
                        resume_filename
                    )
                )

            connection.commit()

            # Naya resume save hone ke baad purani file delete karo
            if old_resume_filename and resume_filename != old_resume_filename:
                old_resume_path = os.path.join(
                    app.config["RESUME_UPLOAD_FOLDER"],
                    old_resume_filename
                )

                if os.path.isfile(old_resume_path):
                    try:
                        os.remove(old_resume_path)
                    except OSError as file_error:
                        print("Old resume cleanup error:", file_error)

            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))

        # Edit form ke liye current profile load karo
        cursor.execute(
            """
            SELECT
                u.full_name,
                u.email,
                sp.phone,
                sp.course,
                sp.college,
                sp.graduation_year,
                sp.cgpa,
                sp.skills,
                sp.bio,
                sp.resume_filename
            FROM users u
            LEFT JOIN student_profiles sp
                ON u.user_id = sp.user_id
            WHERE u.user_id = %s
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()

        return render_template(
            "edit_profile.html",
            student=student,
            current_year=datetime.now().year
        )

    except (mysql.connector.Error, OSError) as error:
        if connection:
            connection.rollback()

        if new_resume_path and os.path.isfile(new_resume_path):
            try:
                os.remove(new_resume_path)
            except OSError:
                pass

        print("Edit Profile Error:", error)
        flash("Unable to update profile.", "danger")
        return redirect(url_for("profile"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# RECRUITER DASHBOARD
# =========================================================

@app.route("/recruiter_dashboard")
def recruiter_dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template(
        "recruiter_dashboard.html",
        name=session.get("full_name")
    )


# =========================================================
# MODULE 3
# COMPANY REGISTRATION
# =========================================================

@app.route("/company_register", methods=["GET", "POST"])
def company_register():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if request.method == "POST":

        company_name = request.form.get(
            "company_name", ""
        ).strip()

        hr_name = request.form.get(
            "hr_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        phone = request.form.get(
            "phone", ""
        ).strip()

        website = request.form.get(
            "website", ""
        ).strip()

        # -------------------------
        # BASIC VALIDATION
        # -------------------------

        if not company_name:

            flash(
                "Company name is required.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        if not hr_name:

            flash(
                "HR name is required.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        if not email:

            flash(
                "Email is required.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        if not phone:

            flash(
                "Phone number is required.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_pattern, email):

            flash(
                "Please enter a valid HR email.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        connection = None
        cursor = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            sql = """
                INSERT INTO companies
                (
                    company_name,
                    hr_name,
                    email,
                    phone,
                    website
                )
                VALUES (%s,%s,%s,%s,%s)
            """

            values = (
                company_name,
                hr_name,
                email,
                phone,
                website
            )

            cursor.execute(sql, values)

            connection.commit()

            flash(
                "Company registered successfully!",
                "success"
            )

            return redirect(
                url_for("company_list")
            )

        except mysql.connector.Error as error:

            if connection:
                connection.rollback()

            print(
                "Company Registration Error:",
                error
            )

            flash(
                "Unable to register company.",
                "danger"
            )

            return redirect(
                url_for("company_register")
            )

        finally:

            if cursor:
                cursor.close()

            if connection and connection.is_connected():
                connection.close()

    return render_template(
        "company_register.html"
    )


# =========================================================
# MODULE 3
# COMPANY LIST
# =========================================================

@app.route("/company_list")
def company_list():

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                company_id,
                company_name,
                hr_name,
                email,
                phone,
                website
            FROM companies
            ORDER BY company_id DESC
            """
        )

        companies = cursor.fetchall()

        return render_template(
            "company_list.html",
            companies=companies
        )

    except mysql.connector.Error as error:

        print(
            "Company List Error:",
            error
        )

        flash(
            "Unable to load companies.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# MODULE 3
# EDIT COMPANY
# =========================================================

@app.route(
    "/company_edit/<int:company_id>",
    methods=["GET", "POST"]
)
def company_edit(company_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        if request.method == "POST":

            company_name = request.form.get(
                "company_name", ""
            ).strip()

            hr_name = request.form.get(
                "hr_name", ""
            ).strip()

            email = request.form.get(
                "email", ""
            ).strip()

            phone = request.form.get(
                "phone", ""
            ).strip()

            website = request.form.get(
                "website", ""
            ).strip()

            sql = """
                UPDATE companies
                SET company_name=%s,
                    hr_name=%s,
                    email=%s,
                    phone=%s,
                    website=%s
                WHERE company_id=%s
            """

            values = (
                company_name,
                hr_name,
                email,
                phone,
                website,
                company_id
            )

            cursor.execute(sql, values)

            connection.commit()

            flash(
                "Company updated successfully!",
                "success"
            )

            return redirect(
                url_for("company_list")
            )

        cursor.execute(
            """
            SELECT
                company_id,
                company_name,
                hr_name,
                email,
                phone,
                website
            FROM companies
            WHERE company_id=%s
            """,
            (company_id,)
        )

        company = cursor.fetchone()

        if company is None:

            flash(
                "Company not found.",
                "danger"
            )

            return redirect(
                url_for("company_list")
            )

        return render_template(
            "company_edit.html",
            company=company
        )

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print(
            "Company Edit Error:",
            error
        )

        flash(
            "Unable to update company.",
            "danger"
        )

        return redirect(
            url_for("company_list")
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# MODULE 3
# DELETE COMPANY
# =========================================================

@app.route(
    "/company_delete/<int:company_id>",
    methods=["POST"]
)
def company_delete(company_id):

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM companies
            WHERE company_id=%s
            """,
            (company_id,)
        )

        connection.commit()

        flash(
            "Company deleted successfully!",
            "success"
        )

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print(
            "Company Delete Error:",
            error
        )

        flash(
            "Unable to delete company.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    return redirect(
        url_for("company_list")
    )

@app.route("/download_resume")
def download_resume():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT resume_filename
            FROM student_profiles
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )

        profile = cursor.fetchone()

        if not profile or not profile["resume_filename"]:
            flash("No resume has been uploaded.", "warning")
            return redirect(url_for("profile"))

        return send_from_directory(
            app.config["RESUME_UPLOAD_FOLDER"],
            profile["resume_filename"],
            as_attachment=True
        )

    except mysql.connector.Error as error:
        print("Resume Download Error:", error)
        flash("Unable to download resume.", "danger")
        return redirect(url_for("profile"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# RUN APPLICATION
# =========================================================
@app.route("/job_create", methods=["GET", "POST"])
def job_create():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can create jobs or internships.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        if request.method == "POST":
            company_name = request.form.get("company_name", "").strip()
            job_title = request.form.get("job_title", "").strip()
            job_type = request.form.get("job_type", "").strip()
            location = request.form.get("location", "").strip()
            salary = request.form.get("salary", "").strip()
            eligibility = request.form.get("eligibility", "").strip()
            description = request.form.get("description", "").strip()
            application_deadline = request.form.get(
                "application_deadline", ""
            ).strip()

            if not all([
                company_name,
                job_title,
                job_type,
                location,
                description
            ]):
                flash("Please fill in all required fields.", "danger")
                return redirect(url_for("job_create"))

            if job_type not in ("Job", "Internship"):
                flash("Select Job or Internship.", "danger")
                return redirect(url_for("job_create"))

            cursor.execute(
                """
                INSERT INTO jobs
                (
                    company_name,
                    job_title,
                    location,
                    salary,
                    eligibility,
                    job_type,
                    description,
                    application_deadline,
                    recruiter_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    company_name,
                    job_title,
                    location,
                    salary,
                    eligibility,
                    job_type,
                    description,
                    application_deadline or None,
                    session["user_id"]
                )
            )
            cursor.execute( "SELECT user_id FROM users WHERE role = %s",("Student",))
            students = cursor.fetchall()
            for student in students:
                cursor.execute(
        """
        INSERT INTO notifications (user_id, message)
        VALUES (%s, %s)
        """,
        (
            student[0],
            f"New {job_type} posted: {job_title} at {company_name}."
        )
    )
            connection.commit()
            flash(f"{job_type} created successfully!", "success")
            return redirect(url_for("recruiter_dashboard"))

        cursor.execute(
            """
            SELECT company_name
            FROM companies
            ORDER BY company_name
            """
        )
        companies = cursor.fetchall()

        return render_template(
            "create_job.html",
            companies=companies
        )

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Job Creation Error:", error)
        flash("Unable to create the job or internship.", "danger")
        return redirect(url_for("recruiter_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/manage_jobs")
def manage_jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can manage job listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                job_id,
                company_name,
                job_title,
                job_type,
                location,
                salary,
                eligibility,
                application_deadline
            FROM jobs
            WHERE recruiter_id = %s
            ORDER BY job_id DESC
            """,
            (session["user_id"],)
        )

        jobs = cursor.fetchall()

        return render_template("manage_jobs.html", jobs=jobs)

    except mysql.connector.Error as error:
        print("Manage Jobs Error:", error)
        flash("Unable to load your job listings.", "danger")
        return redirect(url_for("recruiter_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            
@app.route("/job_edit/<int:job_id>", methods=["GET", "POST"])
def job_edit(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can edit job listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == "POST":
            company_name = request.form.get("company_name", "").strip()
            job_title = request.form.get("job_title", "").strip()
            job_type = request.form.get("job_type", "").strip()
            location = request.form.get("location", "").strip()
            salary = request.form.get("salary", "").strip()
            eligibility = request.form.get("eligibility", "").strip()
            description = request.form.get("description", "").strip()
            application_deadline = request.form.get(
                "application_deadline", ""
            ).strip()

            if not all([company_name, job_title, job_type, location, description]):
                flash("Please fill in all required fields.", "danger")
                return redirect(url_for("job_edit", job_id=job_id))

            if job_type not in ("Job", "Internship"):
                flash("Select Job or Internship.", "danger")
                return redirect(url_for("job_edit", job_id=job_id))

            cursor.execute(
                """
                UPDATE jobs
                SET company_name = %s,
                    job_title = %s,
                    job_type = %s,
                    location = %s,
                    salary = %s,
                    eligibility = %s,
                    description = %s,
                    application_deadline = %s
                WHERE job_id = %s
                  AND recruiter_id = %s
                """,
                (
                    company_name,
                    job_title,
                    job_type,
                    location,
                    salary,
                    eligibility,
                    description,
                    application_deadline or None,
                    job_id,
                    session["user_id"]
                )
            )

            if cursor.rowcount == 0:
                flash("Listing not found or you cannot edit it.", "danger")
                return redirect(url_for("manage_jobs"))

            connection.commit()
            flash("Listing updated successfully!", "success")
            return redirect(url_for("manage_jobs"))

        cursor.execute(
            """
            SELECT
                job_id,
                company_name,
                job_title,
                job_type,
                location,
                salary,
                eligibility,
                description,
                application_deadline
            FROM jobs
            WHERE job_id = %s
              AND recruiter_id = %s
            """,
            (job_id, session["user_id"])
        )

        job = cursor.fetchone()

        if not job:
            flash("Listing not found.", "danger")
            return redirect(url_for("manage_jobs"))

        return render_template("edit_job.html", job=job)

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Job Edit Error:", error)
        flash("Unable to edit this listing.", "danger")
        return redirect(url_for("manage_jobs"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/job_delete/<int:job_id>", methods=["POST"])
def job_delete(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can delete job listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM jobs
            WHERE job_id = %s
              AND recruiter_id = %s
            """,
            (job_id, session["user_id"])
        )

        if cursor.rowcount == 0:
            flash("Listing not found or you cannot delete it.", "danger")
        else:
            connection.commit()
            flash("Listing deleted successfully.", "success")

        return redirect(url_for("manage_jobs"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Job Delete Error:", error)
        flash("Unable to delete this listing.", "danger")
        return redirect(url_for("manage_jobs"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/jobs")
def job_search():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "student":
        flash("Only students can search for jobs.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        keyword = request.args.get("q", "").strip()
        company = request.args.get("company", "").strip()
        job_type = request.args.get("job_type", "").strip()
        location = request.args.get("location", "").strip()

        conditions = []
        values = []

        if keyword:
            conditions.append(
                "(job_title LIKE %s OR description LIKE %s OR company_name LIKE %s)"
            )
            search_value = f"%{keyword}%"
            values.extend([search_value, search_value, search_value])

        if company:
            conditions.append("company_name = %s")
            values.append(company)

        if job_type in ("Job", "Internship"):
            conditions.append("job_type = %s")
            values.append(job_type)

        if location:
            conditions.append("location LIKE %s")
            values.append(f"%{location}%")

        sql = """
            SELECT
                job_id,
                company_name,
                job_title,
                job_type,
                location,
                salary,
                eligibility,
                description,
                application_deadline
            FROM jobs
        """

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY job_id DESC"

        cursor.execute(sql, values)
        jobs = cursor.fetchall()

        cursor.execute(
            """
            SELECT DISTINCT company_name
            FROM jobs
            WHERE company_name IS NOT NULL
            ORDER BY company_name
            """
        )
        companies = cursor.fetchall()

        return render_template(
            "job_search.html",
            jobs=jobs,
            companies=companies,
            keyword=keyword,
            selected_company=company,
            selected_type=job_type,
            selected_location=location
        )

    except mysql.connector.Error as error:
        print("Job Search Error:", error)
        flash("Unable to load job listings.", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()      
@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def job_apply(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "student":
        flash("Only students can apply for listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                job_id,
                company_name,
                job_title,
                job_type,
                location,
                salary,
                eligibility,
                description,
                application_deadline
            FROM jobs
            WHERE job_id = %s
            """,
            (job_id,)
        )

        job = cursor.fetchone()

        if not job:
            flash("Job or internship not found.", "danger")
            return redirect(url_for("job_search"))

        if request.method == "POST":
            cover_letter = request.form.get("cover_letter", "").strip()

            cursor.execute(
                """
                SELECT application_id
                FROM applications
                WHERE job_id = %s
                  AND student_id = %s
                """,
                (job_id, session["user_id"])
            )

            existing_application = cursor.fetchone()

            if existing_application:
                flash("You have already applied for this listing.", "warning")
                return redirect(url_for("job_search"))

            cursor.execute(
                """
                INSERT INTO applications
                    (job_id, student_id, cover_letter)
                VALUES (%s, %s, %s)
                """,
                (job_id, session["user_id"], cover_letter)
            )

            connection.commit()
            flash("Your application was submitted successfully!", "success")
            return redirect(url_for("job_search"))

        return render_template("apply_job.html", job=job)

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Job Application Error:", error)
        flash("Unable to submit your application.", "danger")
        return redirect(url_for("job_search"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/recruiter_applications")
def recruiter_applications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can view applications.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.application_id,
                a.status,
                a.applied_at,
                a.cover_letter,
                a.offer_details,
                a.joining_date,
                j.job_title,
                j.job_type,
                j.company_name,
                u.full_name AS student_name,
                u.email AS student_email
            FROM applications a
            JOIN jobs j
                ON a.job_id = j.job_id
            JOIN users u
                ON a.student_id = u.user_id
            WHERE j.recruiter_id = %s
            ORDER BY a.applied_at DESC
            """,
            (session["user_id"],)
        )

        applications = cursor.fetchall()

        return render_template(
            "recruiter_applications.html",
            applications=applications
        )

    except mysql.connector.Error as error:
        print("Recruiter Applications Error:", error)
        flash("Unable to load applications.", "danger")
        return redirect(url_for("recruiter_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route(
    "/application_status/<int:application_id>",
    methods=["POST"]
)
def update_application_status(application_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can update application status.", "danger")
        return redirect(url_for("dashboard"))

    new_status = request.form.get("status", "").strip()

    if new_status not in ("Shortlisted", "Rejected"):
        flash("Invalid application status.", "danger")
        return redirect(url_for("recruiter_applications"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE applications a
            JOIN jobs j ON a.job_id = j.job_id
            SET a.status = %s
            WHERE a.application_id = %s
              AND j.recruiter_id = %s
            """,
            (new_status, application_id, session["user_id"])
        )

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Application not found or you cannot update it.", "danger")
            return redirect(url_for("recruiter_applications"))

        cursor.execute(
            """
            SELECT a.student_id, j.job_title, j.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.application_id = %s
            """,
            (application_id,)
        )

        student = cursor.fetchone()

        message = (
            f"Your application for {student[1]} at {student[2]} "
            f"was {new_status.lower()}."
        )

        cursor.execute(
            """
            INSERT INTO notifications (user_id, message)
            VALUES (%s, %s)
            """,
            (student[0], message)
        )

        connection.commit()
        flash(f"Application marked {new_status}.", "success")
        return redirect(url_for("recruiter_applications"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Application Status Error:", error)
        flash("Unable to update application status.", "danger")
        return redirect(url_for("recruiter_applications"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/select_candidate/<int:application_id>", methods=["POST"])
def select_candidate(application_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can select applicants.", "danger")
        return redirect(url_for("dashboard"))

    offer_details = request.form.get("offer_details", "").strip()
    joining_date = request.form.get("joining_date", "").strip()

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE applications a
            JOIN jobs j ON a.job_id = j.job_id
            SET a.status = 'Selected',
                a.offer_details = %s,
                a.joining_date = %s
            WHERE a.application_id = %s
              AND j.recruiter_id = %s
            """,
            (
                offer_details or None,
                joining_date or None,
                application_id,
                session["user_id"]
            )
        )

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Application not found or you cannot update it.", "danger")
            return redirect(url_for("recruiter_applications"))

        cursor.execute(
            """
            SELECT a.student_id, j.job_title, j.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.application_id = %s
            """,
            (application_id,)
        )

        student = cursor.fetchone()

        message = (
            f"Congratulations! You were selected for {student[1]} "
            f"at {student[2]}."
        )

        cursor.execute(
            """
            INSERT INTO notifications (user_id, message)
            VALUES (%s, %s)
            """,
            (student[0], message)
        )

        connection.commit()
        flash("Applicant selected; placement details saved.", "success")
        return redirect(url_for("recruiter_applications"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Candidate Selection Error:", error)
        flash("Unable to save placement details.", "danger")
        return redirect(url_for("recruiter_applications"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/notifications")
def student_notifications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "student":
        flash("This page is for students.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT notification_id, message, is_read, created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        )

        notifications = cursor.fetchall()

        return render_template(
            "student_notifications.html",
            notifications=notifications
        )

    except mysql.connector.Error as error:
        print("Notifications Error:", error)
        flash("Unable to load notifications.", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()  
@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can open this page.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM users WHERE role = 'Student')
                    AS student_count,
                (SELECT COUNT(*) FROM users WHERE role = 'Recruiter')
                    AS recruiter_count,
                (SELECT COUNT(*) FROM companies)
                    AS company_count,
                (SELECT COUNT(*) FROM jobs)
                    AS job_count,
                (SELECT COUNT(*) FROM applications)
                    AS application_count
            """
        )

        counts = cursor.fetchone()

        return render_template(
            "admin_dashboard.html",
            counts=counts
        )

    except mysql.connector.Error as error:
        print("Admin Dashboard Error:", error)
        flash("Unable to load admin dashboard.", "danger")
        return redirect(url_for("login"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/admin_users")
def admin_users():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can view user accounts.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
           SELECT user_id, full_name, email, role, is_active
            FROM users
            WHERE role IN ('Student', 'Recruiter')
            ORDER BY role, full_name
            """
        )

        users = cursor.fetchall()

        return render_template("admin_users.html", users=users)

    except mysql.connector.Error as error:
        print("Admin Users Error:", error)
        flash("Unable to load users.", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()     
@app.route("/admin_jobs")
def admin_jobs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can view all job listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                job_id,
                company_name,
                job_title,
                job_type,
                location,
                salary,
                eligibility,
                application_deadline,
                recruiter_id
            FROM jobs
            ORDER BY job_id DESC
            """
        )

        jobs = cursor.fetchall()
        return render_template("admin_jobs.html", jobs=jobs)

    except mysql.connector.Error as error:
        print("Admin Jobs Error:", error)
        flash("Unable to load job listings.", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()     
@app.route("/admin_applications")
def admin_applications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can view all applications.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.application_id,
                a.status,
                a.applied_at,
                a.cover_letter,
                a.offer_details,
                a.joining_date,
                u.full_name AS student_name,
                u.email AS student_email,
                j.job_title,
                j.job_type,
                j.company_name
            FROM applications a
            JOIN users u
                ON a.student_id = u.user_id
            JOIN jobs j
                ON a.job_id = j.job_id
            ORDER BY a.applied_at DESC
            """
        )

        applications = cursor.fetchall()

        return render_template(
            "admin_applications.html",
            applications=applications
        )

    except mysql.connector.Error as error:
        print("Admin Applications Error:", error)
        flash("Unable to load applications.", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/admin_reports")
def admin_reports():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can view reports.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM applications
            GROUP BY status
            ORDER BY status
            """
        )
        application_summary = cursor.fetchall()

        cursor.execute(
            """
            SELECT company_name, COUNT(*) AS totalck
            FROM jobs
            GROUP BY company_name
            ORDER BY total DESC
            """
        )
        jobs_by_company = cursor.fetchall()

        cursor.execute(
            """
            SELECT j.company_name, COUNT(*) AS total
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            GROUP BY j.company_name
            ORDER BY total DESC
            """
        )
        applications_by_company = cursor.fetchall()

        return render_template(
            "admin_reports.html",
            application_summary=application_summary,
            jobs_by_company=jobs_by_company,
            applications_by_company=applications_by_company
        )

    except mysql.connector.Error as error:
        print("Admin Reports Error:", error)
        flash("Unable to load reports.", "danger")
        return redirect(url_for("admin_dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close() 
@app.route("/my_applications")
@app.route("/my_applications")
def my_applications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "student":
        flash("Only students can view their applications.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.application_id,
                a.status,
                a.applied_at,
                a.cover_letter,
                a.offer_details,
                a.joining_date,
                j.job_title,
                j.job_type,
                j.company_name,
                j.location,
                i.interview_datetime,
                i.interview_mode,
                i.location_or_link,
                i.notes,
                i.status AS interview_status
            FROM applications a
            JOIN jobs j
                ON a.job_id = j.job_id
            LEFT JOIN interviews i
                ON i.interview_id = (
                    SELECT MAX(i2.interview_id)
                    FROM interviews i2
                    WHERE i2.application_id = a.application_id
                )
            WHERE a.student_id = %s
            ORDER BY a.applied_at DESC
            """,
            (session["user_id"],)
        )

        applications = cursor.fetchall()

        return render_template(
            "my_applications.html",
            applications=applications
        )

    except mysql.connector.Error as error:
        print("My Applications Error:", error)
        flash("Unable to load your applications.", "danger")
        return redirect(url_for("dashboard"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route(
    "/notification_read/<int:notification_id>",
    methods=["POST"]
)
def mark_notification_read(notification_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "student":
        flash("Only students can update notifications.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = %s
              AND user_id = %s
            """,
            (notification_id, session["user_id"])
        )

        connection.commit()
        return redirect(url_for("student_notifications"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Mark Notification Read Error:", error)
        flash("Unable to update notification.", "danger")
        return redirect(url_for("student_notifications"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()     
@app.route("/admin_user_toggle/<int:user_id>", methods=["POST"])
def admin_toggle_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can change account status.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET is_active = IF(is_active = 1, 0, 1)
            WHERE user_id = %s
              AND role IN ('Student', 'Recruiter')
            """,
            (user_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Student or recruiter account not found.", "danger")
        else:
            connection.commit()
            flash("Account status changed successfully.", "success")

        return redirect(url_for("admin_users"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Admin Account Status Error:", error)
        flash("Unable to change account status.", "danger")
        return redirect(url_for("admin_users"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/admin_job_delete/<int:job_id>", methods=["POST"])
def admin_delete_job(job_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can delete job listings.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Delete this job's applications first.
        cursor.execute(
            "DELETE FROM applications WHERE job_id = %s",
            (job_id,)
        )

        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Job listing not found.", "danger")
        else:
            connection.commit()
            flash("Job listing and its applications deleted.", "success")

        return redirect(url_for("admin_jobs"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Admin Job Delete Error:", error)
        flash("Unable to delete the job listing.", "danger")
        return redirect(url_for("admin_jobs"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route("/admin_application_update/<int:application_id>", methods=["POST"])
def admin_update_application(application_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "admin":
        flash("Only admins can update applications.", "danger")
        return redirect(url_for("dashboard"))

    status = request.form.get("status", "").strip()
    offer_details = request.form.get("offer_details", "").strip()
    joining_date = request.form.get("joining_date", "").strip()

    if status not in ("Pending", "Shortlisted", "Rejected", "Selected"):
        flash("Invalid application status.", "danger")
        return redirect(url_for("admin_applications"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE applications
            SET status = %s,
                offer_details = %s,
                joining_date = %s
            WHERE application_id = %s
            """,
            (
                status,
                offer_details or None,
                joining_date or None,
                application_id
            )
        )

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Application not found or no changes were made.", "warning")
            return redirect(url_for("admin_applications"))

        cursor.execute(
            """
            SELECT a.student_id, j.job_title, j.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.application_id = %s
            """,
            (application_id,)
        )

        application = cursor.fetchone()

        if application:
            message = (
                f"Your application for {application[1]} at {application[2]} "
                f"was updated to {status} by the administrator."
            )

            cursor.execute(
                """
                INSERT INTO notifications (user_id, message)
                VALUES (%s, %s)
                """,
                (application[0], message)
            )

        connection.commit()
        flash("Application updated successfully.", "success")
        return redirect(url_for("admin_applications"))

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Admin Application Update Error:", error)
        flash("Unable to update the application.", "danger")
        return redirect(url_for("admin_applications"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@app.route(
    "/schedule_interview/<int:application_id>",
    methods=["GET", "POST"]
)
def schedule_interview(application_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role", "").lower() != "recruiter":
        flash("Only recruiters can schedule interviews.", "danger")
        return redirect(url_for("dashboard"))

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.application_id,
                a.status,
                a.student_id,
                u.full_name AS student_name,
                j.job_title,
                j.company_name
            FROM applications a
            JOIN users u ON a.student_id = u.user_id
            JOIN jobs j ON a.job_id = j.job_id
            WHERE a.application_id = %s
              AND j.recruiter_id = %s
            """,
            (application_id, session["user_id"])
        )

        application = cursor.fetchone()

        if not application:
            flash("Application not found.", "danger")
            return redirect(url_for("recruiter_applications"))

        if application["status"] not in ("Shortlisted", "Selected"):
            flash("Only shortlisted or selected applicants can be scheduled.", "warning")
            return redirect(url_for("recruiter_applications"))

        if request.method == "POST":
            datetime_input = request.form.get(
                "interview_datetime", ""
            ).strip()
            interview_mode = request.form.get(
                "interview_mode", ""
            ).strip()
            location_or_link = request.form.get(
                "location_or_link", ""
            ).strip()
            notes = request.form.get("notes", "").strip()

            if interview_mode not in ("Online", "In-person"):
                flash("Select Online or In-person.", "danger")
                return redirect(
                    url_for("schedule_interview", application_id=application_id)
                )

            try:
                interview_datetime = datetime.strptime(
                    datetime_input,
                    "%Y-%m-%dT%H:%M"
                )
            except ValueError:
                flash("Enter a valid interview date and time.", "danger")
                return redirect(
                    url_for("schedule_interview", application_id=application_id)
                )

            cursor.execute(
                """
                INSERT INTO interviews
                (
                    application_id,
                    scheduled_by,
                    interview_datetime,
                    interview_mode,
                    location_or_link,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    application_id,
                    session["user_id"],
                    interview_datetime,
                    interview_mode,
                    location_or_link,
                    notes or None
                )
            )

            message = (
                f"An interview for {application['job_title']} at "
                f"{application['company_name']} has been scheduled for "
                f"{interview_datetime.strftime('%d %b %Y, %I:%M %p')}."
            )

            cursor.execute(
                """
                INSERT INTO notifications (user_id, message)
                VALUES (%s, %s)
                """,
                (application["student_id"], message)
            )

            connection.commit()
            flash("Interview scheduled and student notified.", "success")
            return redirect(url_for("recruiter_applications"))

        return render_template(
            "schedule_interview.html",
            application=application
        )

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("Schedule Interview Error:", error)
        flash("Unable to schedule the interview.", "danger")
        return redirect(url_for("recruiter_applications"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
