from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Conexión a la base de datos
app.config["MYSQL_HOST"] = "localhost"  # Host de la base de datos
app.config["MYSQL_USER"] = "root"  # Usuario de la base de datos
app.config["MYSQL_PASSWORD"] = "2569"  # Contraseña de la base de datos
app.config["MYSQL_DB"] = "prueba_crud"  # Nombre de la base de datos

mysql = MySQL(app)  # Inicializa la extensión MySQL con la app Flask


#prueba para saber si la base de datos se conecta correctamente
""" try:
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        print("✅ Conexión exitosa a la base de datos")
except Exception as e:
    print(f"❌ Error al conectar a la base de datos: {e}")

 """

@app.route("/")
def home():
    return redirect(url_for("login"))

# Registro de usuario
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]  # Nombre del usuario
        apellido = request.form["apellido"]  # Apellido del usuario
        telefono = request.form["telefono"]  # Teléfono del usuario
        email = request.form["email"]  # Email del usuario
        fecha_nacimiento = request.form.get("fecha_nacimiento", "2000-01-01")  # Fecha de nacimiento
        contraseña = generate_password_hash(request.form["password"])  # Contraseña hasheada

        cur = mysql.connection.cursor()  # Cursor para ejecutar consultas
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, telefono, email, fecha_nacimiento, contraseña)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, apellido, telefono, email, fecha_nacimiento, contraseña))
        mysql.connection.commit()  # Guarda los cambios en la base de datos
        cur.close()  # Cierra el cursor

        flash("Cuenta creada exitosamente. Ahora puedes iniciar sesión.")  # Mensaje de éxito
        return redirect(url_for("login"))  # Redirige al login

    return render_template("registro.html")  # Muestra el formulario de registro

# Inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]  # Email ingresado
        password = request.form["password"]  # Contraseña ingresada

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        row = cur.fetchone()  # Obtiene el usuario si existe
        column_names = [desc[0] for desc in cur.description]  # Nombres de columnas
        usuario = dict(zip(column_names, row)) if row else None  # Diccionario usuario
        cur.close()

        # Verifica si el usuario existe y la contraseña es correcta
        if usuario and check_password_hash(usuario["contraseña"], password):
            session["username"] = usuario.get("nombre", usuario.get("username", ""))  # Guarda nombre en sesión
            session["nombre"] = usuario["nombre"]  # Guarda nombre en sesión para dashboard
            return redirect(url_for("dashboard"))  # Redirige al dashboard
        else:
            flash("Credenciales inválidas")  # Mensaje de error

    return render_template("login.html")  # Muestra el formulario de login

def process_email(email):
    """Corrige el error anterior y permite procesar el email correctamente."""
    print(f"Procesando email: {email}")

# Panel principal, muestra todos los usuarios si hay sesión activa
@app.route("/dashboard")
def dashboard():
    if "nombre" in session:  # Verifica si hay sesión iniciada
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios")
        column_names = [desc[0] for desc in cur.description]
        usuarios = [dict(zip(column_names, row)) for row in cur.fetchall()]  # Lista de usuarios
        cur.close()
        return render_template("dashboard.html", usuarios=usuarios)  # Muestra el dashboard con usuarios
    
    return redirect(url_for("login"))  # Si no hay sesión, redirige al login

# Eliminar usuario por ID
@app.route("/delete/<int:id>")
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))  # Elimina usuario por ID
    mysql.connection.commit()
    cur.close()

    flash("Usuario eliminado correctamente")  # Mensaje de éxito
    return redirect(url_for("dashboard"))  # Redirige al dashboard

# Editar usuario por ID
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    cur = mysql.connection.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]  # Nuevo nombre
        apellido = request.form["apellido"]  # Nuevo apellido
        telefono = request.form["telefono"]  # Nuevo teléfono
        email = request.form["email"]  # Nuevo email
        fecha_nacimiento = request.form["fecha_nacimiento"]  # Nueva fecha de nacimiento

        cur.execute("""
            UPDATE usuarios
            SET nombre = %s, apellido = %s, telefono = %s, email = %s, fecha_nacimiento = %s
            WHERE id = %s
        """, (nombre, apellido, telefono, email, fecha_nacimiento, id))  # Actualiza datos

        mysql.connection.commit()
        cur.close()

        flash("Usuario actualizado correctamente")  # Mensaje de éxito
        return redirect(url_for("dashboard"))  # Redirige al dashboard

    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))  # Busca usuario por ID
    row = cur.fetchone()
    columnas = [desc[0] for desc in cur.description]
    usuario = dict(zip(columnas, row))  # Diccionario usuario
    cur.close()

    return render_template("edit.html", usuario=usuario)  # Muestra formulario de edición

# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("username", None)  # Elimina la variable de sesión
    return redirect(url_for("login"))  # Redirige al login

# Ejecuta la aplicación en modo debug
if __name__ == "__main__":
    app.run(debug=True)
