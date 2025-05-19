from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "crud"

mysql = MySQL(app)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        ciudad = request.form["ciudad"]
        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios(username, email, fecha_nacimiento, ciudad, password) VALUES(%s, %s, %s, %s, %s)",
            (username, email, fecha_nacimiento, ciudad, password),
        )
        mysql.connection.commit()
        cur.close()

        flash("Registro exitoso")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        usuario = cur.fetchone()
        cur.close()

        if usuario and check_password_hash(
            usuario[5], password
        ):  # Se verifica la contraseña correctamente
            session["username"] = usuario[1]
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales inválidas")

    return render_template("login.html")


def process_email(email):
    """Corrige el error anterior y permite procesar el email correctamente."""
    print(f"Procesando email: {email}")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios")
        usuarios = cur.fetchall()
        cur.close()
        return render_template("dashboard.html", usuarios=usuarios)

    return redirect(url_for("login"))


@app.route("/delete/<int:id>")
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash("Usuario eliminado correctamente")
    return redirect(url_for("dashboard"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    cur = mysql.connection.cursor()

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        ciudad = request.form["ciudad"]

        cur.execute(
            "UPDATE usuarios SET username = %s, email = %s, fecha_nacimiento = %s, ciudad = %s WHERE id = %s",
            (username, email, fecha_nacimiento, ciudad, id),
        )
        mysql.connection.commit()
        cur.close()

        flash("Usuario actualizado correctamente")
        return redirect(url_for("dashboard"))

    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cur.fetchone()
    cur.close()

    return render_template("edit.html", usuario=usuario)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
