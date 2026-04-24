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


def test_respuestas_son_json(client):
    """Todas las respuestas deben tener Content-Type application/json"""
    response = client.get('/health')
    assert 'application/json' in response.content_type


def test_sql_injection_no_causa_500(client):
    """Intentos de SQL injection no deben causar errores del servidor"""
    payloads = [
        "' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "1 UNION SELECT * FROM usuarios",
    ]
    for payload in payloads:
        response = client.post('/usuarios', json={
            'nombre': payload,
            'apellido': payload,
            'email': f'test_{hash(payload)}@test.com'
        })
        assert response.status_code != 500, f"Error 500 con payload: {payload}"


def test_datos_nulos_no_causan_500(client):
    """Enviar body nulo o malformado no debe causar error 500"""
    response = client.post(
        '/usuarios',
        data='no-es-json',
        content_type='application/json'
    )
    assert response.status_code != 500


def test_id_string_en_endpoint_numerico(client):
    """Pasar un string donde se espera int debe retornar 404 no 500"""
    response = client.get('/usuarios/abc')
    assert response.status_code == 404


def test_xss_en_campos_no_causa_500(client):
    """Intentos de XSS en campos de texto no deben causar errores 500"""
    response = client.post('/usuarios', json={
        'nombre': '<script>alert("xss")</script>',
        'apellido': '<img src=x onerror=alert(1)>',
        'email': 'xss@test.com'
    })
    assert response.status_code in [201, 400]
    assert response.status_code != 500


def test_metodo_no_permitido_retorna_405(client):
    """Usar metodo HTTP no permitido debe retornar 405"""
    response = client.delete('/usuarios')
    assert response.status_code == 405


def test_campo_id_no_modificable_en_update(client):
    """El ID no debe cambiar al hacer PUT"""
    resp = client.post('/usuarios', json={
        'nombre': 'Test', 'apellido': 'Test', 'email': 'idtest@test.com'
    })
    usuario_id = resp.get_json()['id']

    response = client.put(f'/usuarios/{usuario_id}', json={
        'nombre': 'Nuevo Nombre',
        'id': 9999
    })
    assert response.status_code == 200
    assert response.get_json()['id'] == usuario_id
