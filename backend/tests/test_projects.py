import pytest
import uuid
from models.project import Project
from models.project_member import ProjectMember


class TestCreateProject:
    def test_create_project_success(self, client, auth_headers, test_org):
        response = client.post("/api/projects", headers=auth_headers, json={
            "name": "Test Project",
            "description": "A test project",
            "org_id": test_org.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Test Project"
        assert data["data"]["description"] == "A test project"
        assert data["data"]["org_id"] == test_org.id
        assert data["data"]["status"] == "active"

    def test_create_project_unauthorized(self, client, test_org):
        response = client.post("/api/projects", json={
            "name": "Test Project",
            "description": "A test project",
            "org_id": test_org.id
        })
        assert response.status_code == 401

    def test_create_project_org_not_found(self, client, auth_headers):
        response = client.post("/api/projects", headers=auth_headers, json={
            "name": "Test Project",
            "description": "A test project",
            "org_id": str(uuid.uuid4())
        })
        assert response.status_code == 404


class TestListProjects:
    def test_list_projects_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="My Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1
        assert any(p["name"] == "My Project" for p in data["data"])

    def test_list_projects_unauthorized(self, client):
        response = client.get("/api/projects")
        assert response.status_code == 401


class TestGetProject:
    def test_get_project_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Get Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.get(f"/api/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Get Test Project"
        assert "members" in data["data"]

    def test_get_project_not_found(self, client, auth_headers):
        response = client.get(f"/api/projects/{str(uuid.uuid4())}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_project_access_denied(self, client, auth_headers, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Private Project",
            description="Test",
            org_id=str(uuid.uuid4()),
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 403


class TestUpdateProject:
    def test_update_project_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Update Test Project",
            description="Original description",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.put(f"/api/projects/{project.id}", headers=auth_headers, json={
            "name": "Updated Name",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["description"] == "Updated description"

    def test_update_project_not_owner_or_admin(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Update Test Project",
            description="Original description",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        response = client.put(f"/api/projects/{project.id}", headers=auth_headers, json={
            "name": "Updated Name"
        })
        assert response.status_code == 403


class TestDeleteProject:
    def test_delete_project_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Delete Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "deleted" in data["message"].lower()

        db.refresh(project)
        assert project.status == "deleted"

    def test_delete_project_not_owner(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Delete Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="admin",
        )
        db.add(member)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 403


class TestListProjectMembers:
    def test_list_project_members_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Members Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/members", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] >= 1


class TestAddProjectMember:
    def test_add_project_member_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Add Member Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        owner_member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(owner_member)

        new_user_id = str(uuid.uuid4())
        new_user = test_user.__class__(
            id=new_user_id,
            email="newmember@example.com",
            password_hash=test_user.password_hash,
            name="New Member",
            is_active=True,
            is_superuser=False,
        )
        db.add(new_user)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/members", headers=auth_headers, json={
            "user_id": new_user_id,
            "role": "member"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["user_id"] == new_user_id
        assert data["data"]["role"] == "member"


class TestRemoveProjectMember:
    def test_remove_project_member_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Remove Member Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        owner_member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(owner_member)

        member_user_id = str(uuid.uuid4())
        member_user = test_user.__class__(
            id=member_user_id,
            email="member@example.com",
            password_hash=test_user.password_hash,
            name="Member User",
            is_active=True,
            is_superuser=False,
        )
        db.add(member_user)

        member_to_remove = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=member_user_id,
            role="member",
        )
        db.add(member_to_remove)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/members/{member_user_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "removed" in data["message"].lower()

    def test_remove_project_owner_forbidden(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Remove Owner Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        owner_member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(owner_member)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/members/{test_user.id}", headers=auth_headers)
        assert response.status_code == 403
