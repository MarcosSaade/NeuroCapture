import pytest
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_create_and_read_patient(client):
    # Create
    payload = {"study_identifier": "TEST-123"}
    create_resp = await client.post("/api/v1/patients/", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert data["study_identifier"] == "TEST-123"
    assert "patient_id" in data
    pid = data["patient_id"]
    # Read
    read_resp = await client.get(f"/api/v1/patients/{pid}")
    assert read_resp.status_code == 200
    rd = read_resp.json()
    assert rd["patient_id"] == pid
    assert rd["study_identifier"] == "TEST-123"
    # Timestamps are UTC strings
    created = datetime.fromisoformat(rd["created_at"])
    assert created.tzinfo == timezone.utc

@pytest.mark.asyncio
async def test_read_patients_list_and_pagination(client):
    # Create a few
    for i in range(3):
        await client.post("/api/v1/patients/", json={"study_identifier": f"ID-{i}"})
    list_resp = await client.get("/api/v1/patients/?skip=1&limit=2")
    assert list_resp.status_code == 200
    arr = list_resp.json()
    assert isinstance(arr, list)
    assert len(arr) == 2

@pytest.mark.asyncio
async def test_update_patient_and_delete(client):
    # Create
    cr = await client.post("/api/v1/patients/", json={"study_identifier": "UPD-OLD"})
    pid = cr.json()["patient_id"]
    # Update
    upd = await client.put(f"/api/v1/patients/{pid}", json={"study_identifier": "UPD-NEW"})
    assert upd.status_code == 200
    assert upd.json()["study_identifier"] == "UPD-NEW"
    # Delete
    del_resp = await client.delete(f"/api/v1/patients/{pid}")
    assert del_resp.status_code == 204
    # Confirm missing
    miss = await client.get(f"/api/v1/patients/{pid}")
    assert miss.status_code == 404
