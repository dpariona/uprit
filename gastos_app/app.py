import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"

# Credenciales fijas (admin / 123)
USERS = {"admin": "123"}

DB_PATH = os.path.join(os.path.dirname(__file__), "gastos.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Debes iniciar sesión primero.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        fecha = request.form.get("fecha")
        descripcion = request.form.get("descripcion", "").strip()
        monto_raw = request.form.get("monto", "").strip()

        if not fecha or not descripcion or not monto_raw:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for("index"))

        try:
            monto = float(monto_raw)
            if monto <= 0:
                raise ValueError
        except ValueError:
            flash("El monto debe ser un número positivo.")
            return redirect(url_for("index"))

        conn = get_db()
        conn.execute(
            "INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)",
            (fecha, descripcion, monto),
        )
        conn.commit()
        conn.close()
        flash("Gasto registrado correctamente.")
        return redirect(url_for("index"))

    conn = get_db()
    gastos = conn.execute(
        "SELECT * FROM gastos ORDER BY fecha DESC, id DESC"
    ).fetchall()
    total = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM gastos").fetchone()[0]
    conn.close()

    return render_template("index.html", gastos=gastos, total=total)


@app.route("/reporte")
@login_required
def reporte():
    conn = get_db()
    gastos = conn.execute(
        "SELECT * FROM gastos ORDER BY fecha ASC, id ASC"
    ).fetchall()
    total = conn.execute("SELECT COALESCE(SUM(monto), 0) FROM gastos").fetchone()[0]
    conn.close()

    # Resumen por mes (YYYY-MM)
    resumen_mensual = {}
    for g in gastos:
        mes = g["fecha"][:7]
        resumen_mensual[mes] = resumen_mensual.get(mes, 0) + g["monto"]

    return render_template(
        "reporte.html",
        gastos=gastos,
        total=total,
        resumen_mensual=resumen_mensual,
        fecha_generacion=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )


if __name__ == "__main__":
    app.run(debug=True)