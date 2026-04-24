import pytest
from app import create_app, db
from app.models import Usuario


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


def test_health_retorna_ok(client):
    """El endpoint /health debe retornar status 200 y status ok"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_usuario_to_dict():
    """El modelo Usuario debe convertirse a dict correctamente"""
    usuario = Usuario(nombre='Juan', apellido='Perez', email='juan@test.com', activo=True)
    d = usuario.to_dict()
    assert d['nombre'] == 'Juan'
    assert d['apellido'] == 'Perez'
    assert d['email'] == 'juan@test.com'
    assert d['activo'] is True


def test_crear_usuario_sin_campos_retorna_400(client):
    """Crear usuario sin datos requeridos debe retornar 400"""
    response = client.post('/usuarios', json={})
    assert response.status_code == 400


def test_crear_usuario_sin_email_retorna_400(client):
    """Crear usuario sin email debe retornar 400"""
    response = client.post('/usuarios', json={'nombre': 'Ana', 'apellido': 'Lopez'})
    assert response.status_code == 400


def test_crear_usuario_exitoso(client):
    """Crear usuario con datos completos debe retornar 201"""
    response = client.post('/usuarios', json={
        'nombre': 'Pedro',
        'apellido': 'Ramirez',
        'email': 'pedro@test.com'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['nombre'] == 'Pedro'
    assert data['id'] is not None


def test_listar_usuarios_retorna_lista(client):
    """Listar usuarios debe retornar una lista"""
    response = client.get('/usuarios')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_obtener_usuario_inexistente_retorna_404(client):
    """Buscar usuario que no existe debe retornar 404"""
    response = client.get('/usuarios/99999')
    assert response.status_code == 404
