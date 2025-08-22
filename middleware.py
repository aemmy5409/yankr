from flask import session, jsonify
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return jsonify({"error": "Authentication required. Kindly login or register!"}), 401
        return f(args, kwargs)
    return decorated_function