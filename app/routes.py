from flask import Blueprint, jsonify, request, render_template
from app import db
from app.models import Usuario

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@api.route('/health', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'ok', 'message': 'API funcionando correctamente'}), 200


@api.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@api.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    if not data or not data.get('nombre') or not data.get('apellido') or not data.get('email'):
        return jsonify({'error': 'Faltan campos requeridos: nombre, apellido, email'}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya esta registrado'}), 409

    usuario = Usuario(
        nombre=data['nombre'],
        apellido=data['apellido'],
        email=data['email']
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


@api.route('/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict()), 200


@api.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def actualizar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'apellido' in data:
        usuario.apellido = data['apellido']
    if 'email' in data:
        existente = Usuario.query.filter(
            Usuario.email == data['email'],
            Usuario.id != usuario_id
        ).first()
        if existente:
            return jsonify({'error': 'El email ya esta registrado'}), 409
        usuario.email = data['email']
    if 'activo' in data:
        usuario.activo = data['activo']

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


@api.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': f'Usuario {usuario_id} eliminado correctamente'}), 200
