# FitTrack — Gym Management System

A first-year BCA mini project using Python, Flask and SQLite DBMS.

## Important
This project intentionally does NOT have an Attendance page or a Members Management page.

## Main modules
1. Dashboard
2. Membership Plans
3. Trainers
4. Classes/Schedule
5. Equipment/Inventory
6. Payments

## Database
Five tables:
- plans
- trainers
- classes
- equipment
- payments

The `classes` and `payments` tables use foreign keys.

## Run
Install Python 3.10+.

Open Terminal in this folder:

pip install -r requirements.txt

Then:

python app.py

Open:
http://127.0.0.1:5000

## Technology used
Python with Flask is used for the backend, and SQLite is used as the DBMS. CSV export demonstrates Python file handling.

## DBMS syllabus/viva
Be ready to explain:
- What is a database?
- What is a table?
- Primary key
- Foreign key
- CRUD
- SQL SELECT/INSERT/UPDATE/DELETE
- JOIN
- Why separate tables are used
- Relationship between trainers and classes
- Relationship between plans and payments
