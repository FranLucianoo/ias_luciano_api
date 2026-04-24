import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_flujo_completo_abm(client):
    """Test del flujo completo: crear, listar, obtener, actualizar y eliminar"""
    # Crear
    response = client.post('/usuarios', json={
        'nombre': 'Maria',
        'apellido': 'Garcia',
        'email': 'maria@test.com'
    })
    assert response.status_code == 201
    usuario_id = response.get_json()['id']

    # Listar - debe haber 1 usuario
    response = client.get('/usuarios')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    # Obtener por ID
    response = client.get(f'/usuarios/{usuario_id}')
    assert response.status_code == 200
    assert response.get_json()['email'] == 'maria@test.com'

    # Actualizar nombre
    response = client.put(f'/usuarios/{usuario_id}', json={'nombre': 'Maria Jose'})
    assert response.status_code == 200
    assert response.get_json()['nombre'] == 'Maria Jose'

    # Eliminar
    response = client.delete(f'/usuarios/{usuario_id}')
    assert response.status_code == 200

    # Verificar que fue eliminado
    response = client.get(f'/usuarios/{usuario_id}')
    assert response.status_code == 404


def test_email_duplicado_retorna_409(client):
    """No se pueden crear dos usuarios con el mismo email"""
    client.post('/usuarios', json={
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'ana@test.com'
    })
    response = client.post('/usuarios', json={
        'nombre': 'Ana2', 'apellido': 'Lopez2', 'email': 'ana@test.com'
    })
    assert response.status_code == 409


def test_actualizar_a_email_existente_retorna_409(client):
    """No se puede actualizar el email a uno ya registrado"""
    client.post('/usuarios', json={
        'nombre': 'A', 'apellido': 'A', 'email': 'a@test.com'
    })
    resp = client.post('/usuarios', json={
        'nombre': 'B', 'apellido': 'B', 'email': 'b@test.com'
    })
    usuario_b_id = resp.get_json()['id']

    response = client.put(f'/usuarios/{usuario_b_id}', json={'email': 'a@test.com'})
    assert response.status_code == 409


def test_multiples_usuarios(client):
    """Se pueden crear y listar multiples usuarios"""
    for i in range(5):
        client.post('/usuarios', json={
            'nombre': f'Usuario{i}',
            'apellido': 'Test',
            'email': f'usuario{i}@test.com'
        })

    response = client.get('/usuarios')
    assert response.status_code == 200
    assert len(response.get_json()) == 5


def test_actualizar_estado_activo(client):
    """Se puede cambiar el estado activo de un usuario"""
    resp = client.post('/usuarios', json={
        'nombre': 'Carlos', 'apellido': 'Ruiz', 'email': 'carlos@test.com'
    })
    usuario_id = resp.get_json()['id']

    response = client.put(f'/usuarios/{usuario_id}', json={'activo': False})
    assert response.status_code == 200
    assert response.get_json()['activo'] is False
