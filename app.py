from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Conectar a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="tu_base_de_datos"
    )

# Ruta de inicio (login)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Persona WHERE usuario = %s", (usuario,))
        persona = cursor.fetchone()
        
        if persona and check_password_hash(persona['contrasena'], contrasena):
            session['usuario'] = persona['usuario']
            session['perfil'] = 'Administrador' if persona['idPerfil'] == 1 else 'Cliente'
            flash('Inicio de sesión exitoso', 'success')
            return redirect('/dashboard')
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
        
        cursor.close()
        conexion.close()
        
    return render_template('login.html')

# Ruta para el registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre1 = request.form['nombre1']
        nombre2 = request.form['nombre2']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        direccion = request.form['direccion']
        movil = request.form['movil']
        email = request.form['email']
        idPerfil = request.form['idPerfil']
        usuario = request.form['usuario']
        contrasena = generate_password_hash(request.form['contrasena'])

        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Persona (nombre1, nombre2, apellido1, apellido2, direccion, movil, email, idPerfil, usuario, contrasena, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (nombre1, nombre2, apellido1, apellido2, direccion, movil, email, idPerfil, usuario, contrasena))
        conexion.commit()
        cursor.close()
        conexion.close()
        
        flash('Cuenta creada exitosamente', 'success')
        return redirect('/')
    
    return render_template('registro.html')

# Ruta del dashboard
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')
    
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Persona")
    personas = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template('dashboard.html', personas=personas)

# Ruta para crear una persona
@app.route('/crear', methods=['GET', 'POST'])
def crear_persona():
    if 'usuario' not in session or session['perfil'] != 'Administrador':
        return redirect('/')
    if request.method == 'POST':
        nombre1 = request.form['nombre1']
        nombre2 = request.form['nombre2']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        direccion = request.form['direccion']
        movil = request.form['movil']
        email = request.form['email']
        idPerfil = request.form['idPerfil']
        usuario = request.form['usuario']
        contrasena = generate_password_hash(request.form['contrasena'])
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Persona (nombre1, nombre2, apellido1, apellido2, direccion, movil, email, idPerfil, usuario, contrasena, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """, (nombre1, nombre2, apellido1, apellido2, direccion, movil, email, idPerfil, usuario, contrasena))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Persona creada exitosamente', 'success')
        return redirect('/dashboard')
    return render_template('crear_persona.html')

# Ruta para editar una persona
@app.route('/editar/<int:idpersona>', methods=['GET', 'POST'])
def editar_persona(idpersona):
    if 'usuario' not in session:
        return redirect('/')
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    if request.method == 'POST':
        nombre1 = request.form['nombre1']
        nombre2 = request.form['nombre2']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        direccion = request.form['direccion']
        movil = request.form['movil']
        email = request.form['email']
        idPerfil = request.form['idPerfil']
        usuario = request.form['usuario']
        
        cursor.execute("""
            UPDATE Persona
            SET nombre1 = %s, nombre2 = %s, apellido1 = %s, apellido2 = %s,
                direccion = %s, movil = %s, email = %s, idPerfil = %s, usuario = %s
            WHERE idpersona = %s
        """, (nombre1, nombre2, apellido1, apellido2, direccion, movil, email, idPerfil, usuario, idpersona))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Datos actualizados exitosamente', 'success')
        return redirect('/dashboard')
    
    cursor.execute("SELECT * FROM Persona WHERE idpersona = %s", (idpersona,))
    persona = cursor.fetchone()
    cursor.close()
    conexion.close()
    return render_template('editar_persona.html', persona=persona)

# Ruta para inhabilitar una persona
@app.route('/inhabilitar/<int:idpersona>', methods=['GET'])
def inhabilitar_persona(idpersona):
    if 'usuario' not in session or session['perfil'] != 'Administrador':
        return redirect('/')
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("UPDATE Persona SET estado = 0 WHERE idpersona = %s", (idpersona,))
    conexion.commit()
    cursor.close()
    conexion.close()
    flash('Persona inhabilitada exitosamente', 'success')
    return redirect('/dashboard')

# Ruta para restablecer contraseña
@app.route('/restablecer', methods=['GET', 'POST'])
def restablecer():
    if request.method == 'POST':
        email = request.form['email']
        
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Persona WHERE email = %s", (email,))
        persona = cursor.fetchone()
        
        if persona:
            nueva_contrasena = 'NuevaContrasena123'  # Generar contraseña segura
            nueva_contrasena_hash = generate_password_hash(nueva_contrasena)
            
            cursor.execute("UPDATE Persona SET contrasena = %s WHERE email = %s", (nueva_contrasena_hash, email))
            conexion.commit()
            flash(f'Tu contraseña se ha restablecido. La nueva contraseña temporal es: {nueva_contrasena}', 'success')
        else:
            flash('El email no se encuentra registrado', 'danger')
        
        cursor.close()
        conexion.close()
        return redirect('/')
    
    return render_template('restablecer.html')

if __name__ == '__main__':
    app.run(debug=True)
