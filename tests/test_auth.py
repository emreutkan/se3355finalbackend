import pytest
import json
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'full_name': 'Test User',
        'country': 'US',
        'city': 'New York'
    }

def test_user_registration(client, sample_user):
    """Test user registration endpoint."""
    response = client.post('/api/auth/register', 
                          data=json.dumps(sample_user),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['msg'] == 'User registered successfully'
    assert 'user' in data
    assert data['user']['email'] == sample_user['email']

def test_user_registration_invalid_password(client):
    """Test user registration with invalid password."""
    user_data = {
        'email': 'test@example.com',
        'password': 'weak',  # Too weak
        'full_name': 'Test User',
        'country': 'US',
        'city': 'New York'
    }
    
    response = client.post('/api/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Password must be at least 8 characters' in data['msg']

def test_user_login(client, sample_user):
    """Test user login endpoint."""
    # First register the user
    client.post('/api/auth/register',
               data=json.dumps(sample_user),
               content_type='application/json')
    
    # Then try to login
    login_data = {
        'email': sample_user['email'],
        'password': sample_user['password']
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data

def test_user_login_invalid_credentials(client):
    """Test user login with invalid credentials."""
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['msg'] == 'Invalid credentials'

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['msg'] == 'Authentication token required'

def test_protected_endpoint_with_token(client, sample_user):
    """Test accessing protected endpoint with valid token."""
    # Register and login to get token
    client.post('/api/auth/register',
               data=json.dumps(sample_user),
               content_type='application/json')
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps({
                                    'email': sample_user['email'],
                                    'password': sample_user['password']
                                }),
                                content_type='application/json')
    
    token = json.loads(login_response.data)['access_token']
    
    # Access protected endpoint
    response = client.get('/api/auth/me',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == sample_user['email'] 