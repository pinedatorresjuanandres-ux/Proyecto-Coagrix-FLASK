from flask import Blueprint, session, redirect, url_for
from controllers.merchant_controller import dashboard, compare_prices

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')

@merchant_bp.before_request
def check_merchant():
    if 'user_id' not in session or session.get('role_name') != 'Comerciante':
        return redirect(url_for('auth.login_page'))

@merchant_bp.route('/dashboard')
def dashboard_route():
    return dashboard()

@merchant_bp.route('/comparar')
def compare_route():
    return compare_prices()
