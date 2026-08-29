import secrets
from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for, session, flash
from config import Config
from models.user import (
    get_user_by_email, create_user, get_role_name,
    create_farmer_profile, create_company_profile, create_merchant_profile,
    verify_password, upgrade_password_if_plaintext,
    set_reset_token, get_user_by_reset_token, update_password
)
from utils.mailer import send_reset_email

def login(template='login.html'):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        
        if user and verify_password(user['password'], password):
            upgrade_password_if_plaintext(user['id'], user['password'], password)

            if user['estado'] == 'Inactivo':
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                return redirect(request.path)
            
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['role_id'] = user['rol_id']
            session['role_name'] = get_role_name(user['rol_id'])
            
            # Redirect based on role
            if session['role_name'] == 'Administrador':
                return redirect(url_for('admin.dashboard_route'))
            elif session['role_name'] == 'Campesino':
                return redirect(url_for('farmer.dashboard'))
            elif session['role_name'] == 'Empresa':
                return redirect(url_for('company.dashboard_route'))
            elif session['role_name'] == 'Comerciante':
                return redirect(url_for('merchant.dashboard_route'))
        else:
            flash('Credenciales incorrectas.', 'error')
            
    return render_template(template)

def logout():
    session.clear()
    return redirect(url_for('index'))

def register(template='registro.html', default_role_id=None, login_redirect='auth.login_page'):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        rol_id = request.form.get('rol_id') or default_role_id
        
        if get_user_by_email(email):
            flash('El correo ya está registrado.', 'error')
            return redirect(request.path)
        
        user_id = create_user(nombre, email, password, rol_id)
        if user_id:

            rol_id_int = int(rol_id) if rol_id else None
            if rol_id_int == 2:
                create_farmer_profile(user_id)
            elif rol_id_int == 3:
                create_company_profile(user_id)
            elif rol_id_int == 4:
                create_merchant_profile(user_id)

            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for(login_redirect))
        else:
            flash('Error al registrar el usuario.', 'error')
            
    return render_template(template)


def forgot_password():
    """Paso 1: el usuario ingresa su correo y, si existe, se le envía (o
    se le muestra, si no hay SMTP configurado) un enlace para restablecer
    su contraseña."""
    dev_link = None

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        user = get_user_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)
            expira = datetime.now() + timedelta(hours=1)
            set_reset_token(user['id'], token, expira)

            enlace = url_for('auth.reset_password_page', token=token, _external=True)
            enviado = send_reset_email(user['email'], user['nombre'], enlace)

            if not enviado and Config.ENV != 'production':
                # No hay servidor de correo configurado (MAIL_USERNAME /
                # MAIL_PASSWORD en .env): en desarrollo se muestra el
                # enlace directamente en pantalla para poder probar el
                # flujo completo sin depender de un SMTP real.
                dev_link = enlace

        # Mensaje genérico siempre, exista o no la cuenta, para no revelar
        # qué correos están registrados en la plataforma.
        flash(
            'Si el correo está registrado, te enviaremos instrucciones para restablecer tu contraseña.',
            'success'
        )

    return render_template('olvide_password.html', dev_link=dev_link)


def reset_password(token):
    """Paso 2: el usuario llega desde el enlace del correo y define su
    nueva contraseña, siempre que el token exista y no haya expirado."""
    user = get_user_by_reset_token(token)

    if not user:
        flash('El enlace no es válido o ya expiró. Solicita uno nuevo.', 'error')
        return redirect(url_for('auth.forgot_password_page'))

    if request.method == 'POST':
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(request.path)

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(request.path)

        update_password(user['id'], password)
        flash('Tu contraseña se actualizó correctamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login_page'))

    return render_template('restablecer_password.html', token=token)
