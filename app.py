from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / "data" / "gym.db"

app = Flask(__name__)
app.secret_key = "fittrack-demo"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        duration_months INTEGER NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS trainers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        phone TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        trainer_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        time TEXT NOT NULL,
        FOREIGN KEY (trainer_id) REFERENCES trainers(id)
    );

    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        condition TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payer_name TEXT NOT NULL,
        plan_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (plan_id) REFERENCES plans(id)
    );
    """)

    if conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO plans(name,duration_months,price) VALUES(?,?,?)",
            [("Basic",1,999),("Standard",3,2499),("Premium",12,7999)]
        )

    if conn.execute("SELECT COUNT(*) FROM trainers").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO trainers(name,specialization,phone) VALUES(?,?,?)",
            [("Arjun Rao","Strength Training","9876543210"),
             ("Neha Sharma","Yoga & Mobility","9876501234"),
             ("Kabir Mehta","Cardio & Fitness","9988776655")]
        )

    if conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0] == 0:
        trainers = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM trainers")}
        conn.executemany(
            "INSERT INTO classes(class_name,trainer_id,day,time) VALUES(?,?,?,?)",
            [("Strength Basics",trainers["Arjun Rao"],"Monday","7:00 AM"),
             ("Yoga Flow",trainers["Neha Sharma"],"Wednesday","6:00 PM"),
             ("Cardio Blast",trainers["Kabir Mehta"],"Friday","7:00 AM")]
        )

    if conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO equipment(name,category,quantity,condition) VALUES(?,?,?,?)",
            [("Treadmill","Cardio",4,"Good"),
             ("Dumbbell Set","Strength",12,"Good"),
             ("Exercise Mat","Flexibility",20,"Good"),
             ("Bench Press","Strength",3,"Maintenance")]
        )

    if conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0] == 0:
        plans = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM plans")}
        conn.executemany(
            "INSERT INTO payments(payer_name,plan_id,amount,payment_date,status) VALUES(?,?,?,?,?)",
            [("Demo Customer",plans["Premium"],7999,"2026-09-20","Paid"),
             ("Sample Customer",plans["Standard"],2499,"2026-09-25","Paid")]
        )

    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    conn = get_db()
    stats = {
        "plans": conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0],
        "trainers": conn.execute("SELECT COUNT(*) FROM trainers").fetchone()[0],
        "classes": conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
        "equipment": conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0],
        "revenue": conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='Paid'").fetchone()[0]
    }
    upcoming = conn.execute("""
        SELECT classes.*, trainers.name AS trainer
        FROM classes JOIN trainers ON classes.trainer_id=trainers.id
        ORDER BY classes.id
    """).fetchall()
    conn.close()
    return render_template("dashboard.html", stats=stats, classes=upcoming)

@app.route("/plans", methods=["GET","POST"])
def plans():
    conn = get_db()
    if request.method == "POST":
        try:
            conn.execute(
                "INSERT INTO plans(name,duration_months,price) VALUES(?,?,?)",
                (request.form["name"], int(request.form["duration"]), float(request.form["price"]))
            )
            conn.commit()
            flash("Plan added successfully.", "success")
        except (ValueError, KeyError):
            flash("Please enter valid plan details.", "error")
        conn.close()
        return redirect(url_for("plans"))
    rows = conn.execute("SELECT * FROM plans ORDER BY price").fetchall()
    conn.close()
    return render_template("plans.html", plans=rows)

@app.route("/trainers", methods=["GET","POST"])
def trainers():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO trainers(name,specialization,phone) VALUES(?,?,?)",
            (request.form["name"], request.form["specialization"], request.form["phone"])
        )
        conn.commit()
        conn.close()
        flash("Trainer added.", "success")
        return redirect(url_for("trainers"))
    rows = conn.execute("SELECT * FROM trainers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("trainers.html", trainers=rows)

@app.route("/classes")
def classes():
    conn = get_db()
    rows = conn.execute("""
        SELECT classes.*, trainers.name AS trainer
        FROM classes JOIN trainers ON classes.trainer_id=trainers.id
        ORDER BY classes.id
    """).fetchall()
    conn.close()
    return render_template("classes.html", classes=rows)

@app.route("/equipment", methods=["GET","POST"])
def equipment():
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO equipment(name,category,quantity,condition) VALUES(?,?,?,?)",
            (request.form["name"], request.form["category"],
             int(request.form["quantity"]), request.form["condition"])
        )
        conn.commit()
        conn.close()
        flash("Equipment added.", "success")
        return redirect(url_for("equipment"))
    rows = conn.execute("SELECT * FROM equipment ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("equipment.html", equipment=rows)

@app.route("/payments", methods=["GET","POST"])
def payments():
    conn = get_db()
    if request.method == "POST":
        try:
            conn.execute(
                "INSERT INTO payments(payer_name,plan_id,amount,payment_date,status) VALUES(?,?,?,?,?)",
                (request.form["payer"], int(request.form["plan_id"]),
                 float(request.form["amount"]), request.form["date"], request.form["status"])
            )
            conn.commit()
            flash("Payment recorded.", "success")
        except (ValueError, KeyError):
            flash("Please enter valid payment details.", "error")
        conn.close()
        return redirect(url_for("payments"))

    rows = conn.execute("""
        SELECT payments.*, plans.name AS plan
        FROM payments JOIN plans ON payments.plan_id=plans.id
        ORDER BY payment_date DESC
    """).fetchall()
    plans = conn.execute("SELECT * FROM plans ORDER BY price").fetchall()
    conn.close()
    return render_template("payments.html", payments=rows, plans=plans)

@app.route("/export")
def export():
    conn = get_db()
    rows = conn.execute("""
        SELECT payments.id, payments.payer_name, plans.name AS plan,
               payments.amount, payments.payment_date, payments.status
        FROM payments JOIN plans ON payments.plan_id=plans.id
    """).fetchall()
    conn.close()

    path = BASE_DIR / "data" / "payments.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Payer","Plan","Amount","Date","Status"])
        writer.writerows([list(r) for r in rows])
    return __import__("flask").send_file(path, as_attachment=True, download_name="payments.csv")

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
