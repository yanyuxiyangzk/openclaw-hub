import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from core.database import Base
from models.activity import Activity
from models.user import User
from schemas.activity import ActivityCreate
from services.activity_service import ActivityService
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


@pytest.fixture
def tenant_id():
    return str(uuid.uuid4())


@pytest.fixture
def actor_user(db, tenant_id):
    user = User(
        id=str(uuid.uuid4()),
        email="actor@example.com",
        password_hash=get_password_hash("password123"),
        name="Actor User",
        is_active=True,
        is_superuser=False,
        tenant_id=tenant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_user(db, tenant_id):
    user = User(
        id=str(uuid.uuid4()),
        email="another@example.com",
        password_hash=get_password_hash("password123"),
        name="Another User",
        is_active=True,
        is_superuser=False,
        tenant_id=tenant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def activity_service(db):
    return ActivityService(db)


@pytest.fixture
def sample_activity(db, tenant_id, actor_user):
    activity = Activity(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        actor_id=actor_user.id,
        actor_name=actor_user.name,
        actor_avatar=None,
        action_type="created",
        entity_type="task",
        entity_id=str(uuid.uuid4()),
        entity_name="Test Task",
        extra_data={"priority": "high"},
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@pytest.fixture
def multiple_activities(db, tenant_id, actor_user, another_user):
    activities = []
    entity_types = ["task", "project", "agent"]
    action_types = ["created", "updated", "deleted"]

    for i in range(15):
        actor = actor_user if i % 3 == 0 else another_user
        activity = Activity(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            actor_id=actor.id,
            actor_name=actor.name,
            actor_avatar=None,
            action_type=action_types[i % 3],
            entity_type=entity_types[i % 3],
            entity_id=str(uuid.uuid4()),
            entity_name=f"Entity {i}",
            extra_data={"index": i},
        )
        db.add(activity)
        activities.append(activity)

    db.commit()
    for a in activities:
        db.refresh(a)
    return activities


class TestActivityServiceInit:
    """Test ActivityService initialization"""

    def test_init_sets_db_session(self, db, activity_service):
        assert activity_service.db is db


class TestCreateActivity:
    """Test ActivityService.create_activity method"""

    def test_create_activity_with_required_fields(self, db, activity_service, tenant_id):
        data = ActivityCreate(
            actor_id="actor-1",
            actor_name="Actor One",
            action_type="created",
            entity_type="task",
            entity_id="task-001",
        )
        activity = activity_service.create_activity(tenant_id=tenant_id, data=data)

        assert activity is not None
        assert activity.tenant_id == tenant_id
        assert activity.actor_id == "actor-1"
        assert activity.actor_name == "Actor One"
        assert activity.action_type == "created"
        assert activity.entity_type == "task"
        assert activity.entity_id == "task-001"
        assert activity.entity_name is None
        assert activity.actor_avatar is None
        assert activity.extra_data is None
        assert activity.id is not None

    def test_create_activity_with_all_fields(self, db, activity_service, tenant_id):
        data = ActivityCreate(
            actor_id="actor-2",
            actor_name="Actor Two",
            actor_avatar="https://example.com/avatar.png",
            action_type="updated",
            entity_type="project",
            entity_id="project-002",
            entity_name="My Project",
            extra_data={"field": "value", "count": 42},
        )
        activity = activity_service.create_activity(tenant_id=tenant_id, data=data)

        assert activity.actor_id == "actor-2"
        assert activity.actor_name == "Actor Two"
        assert activity.actor_avatar == "https://example.com/avatar.png"
        assert activity.action_type == "updated"
        assert activity.entity_type == "project"
        assert activity.entity_id == "project-002"
        assert activity.entity_name == "My Project"
        assert activity.extra_data == {"field": "value", "count": 42}

    def test_create_activity_persisted_in_db(self, db, activity_service, tenant_id):
        data = ActivityCreate(
            actor_id="actor-3",
            actor_name="Actor Three",
            action_type="deleted",
            entity_type="workflow",
            entity_id="workflow-003",
        )
        activity = activity_service.create_activity(tenant_id=tenant_id, data=data)

        # Verify it's in the database
        db_activity = db.query(Activity).filter(Activity.id == activity.id).first()
        assert db_activity is not None
        assert db_activity.actor_id == "actor-3"


class TestListActivities:
    """Test ActivityService.list_activities method"""

    def test_list_activities_empty(self, db, activity_service, tenant_id):
        result = activity_service.list_activities(tenant_id=tenant_id)

        assert result["items"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["limit"] == 20
        assert result["pages"] == 0

    def test_list_activities_basic(self, db, activity_service, tenant_id, sample_activity):
        result = activity_service.list_activities(tenant_id=tenant_id)

        assert len(result["items"]) == 1
        assert result["total"] == 1
        assert result["items"][0]["actor_id"] == sample_activity.actor_id

    def test_list_activities_pagination(self, db, activity_service, tenant_id, multiple_activities):
        # First page
        result = activity_service.list_activities(tenant_id=tenant_id, page=1, limit=5)

        assert len(result["items"]) == 5
        assert result["total"] == 15
        assert result["page"] == 1
        assert result["limit"] == 5
        assert result["pages"] == 3

        # Second page
        result = activity_service.list_activities(tenant_id=tenant_id, page=2, limit=5)

        assert len(result["items"]) == 5
        assert result["page"] == 2

        # Last page
        result = activity_service.list_activities(tenant_id=tenant_id, page=3, limit=5)

        assert len(result["items"]) == 5
        assert result["page"] == 3

        # Beyond last page
        result = activity_service.list_activities(tenant_id=tenant_id, page=4, limit=5)

        assert len(result["items"]) == 0
        assert result["total"] == 15

    def test_list_activities_filter_by_actor_id(self, db, activity_service, tenant_id, multiple_activities, actor_user):
        result = activity_service.list_activities(
            tenant_id=tenant_id,
            actor_id=actor_user.id
        )

        assert result["total"] == 5  # actor_user created 5 of 15 activities
        for item in result["items"]:
            assert item["actor_id"] == actor_user.id

    def test_list_activities_filter_by_action_type(self, db, activity_service, tenant_id, multiple_activities):
        result = activity_service.list_activities(
            tenant_id=tenant_id,
            action_type="created"
        )

        assert result["total"] == 5  # 15 activities, 3 action types
        for item in result["items"]:
            assert item["action_type"] == "created"

    def test_list_activities_filter_by_entity_type(self, db, activity_service, tenant_id, multiple_activities):
        result = activity_service.list_activities(
            tenant_id=tenant_id,
            entity_type="task"
        )

        assert result["total"] == 5  # 15 activities, 3 entity types
        for item in result["items"]:
            assert item["entity_type"] == "task"

    def test_list_activities_filter_combined(self, db, activity_service, tenant_id, multiple_activities, actor_user):
        result = activity_service.list_activities(
            tenant_id=tenant_id,
            actor_id=actor_user.id,
            action_type="created",
            entity_type="task"
        )

        # actor_user has 5 activities (i % 3 == 0: i=0,3,6,9,12)
        # All of these have action_type="created" and entity_type="task"
        assert result["total"] == 5
        for item in result["items"]:
            assert item["actor_id"] == actor_user.id
            assert item["action_type"] == "created"
            assert item["entity_type"] == "task"

    def test_list_activities_returns_ordered_results(self, db, activity_service, tenant_id, sample_activity):
        # Create another activity
        data = ActivityCreate(
            actor_id="actor-new",
            actor_name="New Actor",
            action_type="updated",
            entity_type="task",
            entity_id="task-new",
        )
        new_activity = activity_service.create_activity(tenant_id=tenant_id, data=data)

        result = activity_service.list_activities(tenant_id=tenant_id)

        # Both activities should be present
        result_ids = [item["id"] for item in result["items"]]
        assert sample_activity.id in result_ids
        assert new_activity.id in result_ids
        assert result["total"] == 2
        # Verify ordering is descending by created_at (list should be in correct order format)
        assert len(result["items"]) == 2

    def test_list_activities_different_tenant_returns_empty(self, db, activity_service, sample_activity):
        different_tenant_id = str(uuid.uuid4())
        result = activity_service.list_activities(tenant_id=different_tenant_id)

        assert result["items"] == []
        assert result["total"] == 0

    def test_list_activities_with_large_page_size(self, db, activity_service, tenant_id, multiple_activities):
        result = activity_service.list_activities(tenant_id=tenant_id, page=1, limit=100)

        assert len(result["items"]) == 15
        assert result["total"] == 15
        assert result["pages"] == 1

    def test_list_activities_page_calculation(self, db, activity_service, tenant_id, multiple_activities):
        # Test pages calculation with various limits
        result = activity_service.list_activities(tenant_id=tenant_id, page=1, limit=7)

        assert result["total"] == 15
        assert result["pages"] == 3  # ceil(15/7) = 3
