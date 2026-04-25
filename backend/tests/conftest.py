import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from core.database import Base, get_db
from main import app
from models.user import User
from models.organization import Organization, OrganizationMember
from models.invitation import Invitation
from core.security import get_password_hash


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        name="Test User",
        is_active=True,
        is_superuser=False,
        tenant_id=str(uuid.uuid4()),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def superuser(db):
    user = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        name="Admin User",
        is_active=True,
        is_superuser=True,
        tenant_id=str(uuid.uuid4()),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superuser_headers(client, superuser):
    response = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_org(db, test_user):
    org = Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        owner_id=test_user.id,
    )
    db.add(org)
    db.commit()

    member = OrganizationMember(
        id=str(uuid.uuid4()),
        org_id=org.id,
        user_id=test_user.id,
        role="owner",
    )
    db.add(member)
    db.commit()
    db.refresh(org)
    return org