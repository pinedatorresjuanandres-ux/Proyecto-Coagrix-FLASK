from flask import render_template, session
from models.favorite import get_user_favorites


def list_favorites():
    favorites = get_user_favorites(session['user_id'])
    return render_template('favorites.html', favorites=favorites)
