from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from controllers.company_controller import dashboard, search_products
from models.company import get_company_profile, update_company_profile

company_bp = Blueprint('company', __name__, url_prefix='/company')

@company_bp.before_request
def check_company():
    if 'user_id' not in session or session.get('role_name') != 'Empresa':
        return redirect(url_for('auth.login_page'))

@company_bp.route('/dashboard')
def dashboard_route():
    return dashboard()

@company_bp.route('/buscar')
def search_route():
    return search_products()

@company_bp.route('/perfil', methods=['GET', 'POST'])
def profile_route():
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        nit = request.form.get('nit')
        sector = request.form.get('sector')
        update_company_profile(session['user_id'], telefono, nit, sector)
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('company.profile_route'))

    company = get_company_profile(session['user_id'])
    return render_template('company/profile.html', company=company)
