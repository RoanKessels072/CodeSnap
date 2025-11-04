from services.code_execution_service import execute_code
from flask import Blueprint, request, jsonify
from middleware.keycloak_auth import require_auth

bp = Blueprint("code", __name__)

@bp.route('/execute', methods=['POST'])
@require_auth
def execute_code_route():
    data = request.get_json()
    result = execute_code(data.get('code', ''), data.get('language', 'python'))
    return jsonify(result)
