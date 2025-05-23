# backend/tests/test_assessments.py
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

# Assuming your FastAPI app and test setup are correctly configured
# and you have a way to get a test_patient_id, e.g., from a fixture.

def parse_iso_datetime_str(datetime_str: str) -> datetime:
    if datetime_str and datetime_str.endswith("Z"):
        datetime_str = datetime_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(datetime_str)
    if dt.tzinfo is None: # Should be redundant if +00:00 is parsed, but good for safety
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

# Test creating an assessment without subscores
@pytest.mark.asyncio
async def test_create_assessment_no_subscores(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    assessment_data = {
        "assessment_type": "Cognitive Test",
        "score": 85.5,
        "max_possible_score": 100.0,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "diagnosis": "Mild cognitive impairment",
        "notes": "Patient performed well overall.",
        "subscores": []  # Explicitly empty
    }

    response = await client.post(f"/api/v1/patients/{patient_id}/assessments/", json=assessment_data)

    assert response.status_code == 201
    response_data = response.json()

    assert "assessment_id" in response_data
    assert response_data["assessment_type"] == assessment_data["assessment_type"]
    assert response_data["score"] == assessment_data["score"]
    assert response_data["max_possible_score"] == assessment_data["max_possible_score"]
    assert response_data["diagnosis"] == assessment_data["diagnosis"]
    assert response_data["notes"] == assessment_data["notes"]
    assert response_data["patient_id"] == patient_id

    # Check assessment_date (ignoring microseconds for comparison if necessary)
    response_assessment_date = parse_iso_datetime_str(response_data["assessment_date"])
    original_assessment_date = parse_iso_datetime_str(assessment_data["assessment_date"])
    assert response_assessment_date.replace(microsecond=0) == original_assessment_date.replace(microsecond=0)


    # Check timestamps
    assert "created_at" in response_data
    assert "updated_at" in response_data
    
    parse_iso_datetime_str(response_data["created_at"])  # Check if parsable
    parse_iso_datetime_str(response_data["updated_at"])  # Check if parsable

    assert len(response_data["subscores"]) == 0


from datetime import timedelta

# Test retrieving all assessments for a patient and checking order
@pytest.mark.asyncio
async def test_get_assessments_for_patient(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    num_assessments = 3
    created_assessment_ids = []
    assessment_dates = []

    # Create multiple assessments with different dates
    for i in range(num_assessments):
        # Ensure assessment dates are distinct and in a known order for later verification
        assessment_date = datetime.now(timezone.utc) - timedelta(days=i)
        assessment_dates.append(assessment_date)
        assessment_data = {
            "assessment_type": f"Test Type {i+1}",
            "score": 70.0 + i,
            "max_possible_score": 100.0,
            "assessment_date": assessment_date.isoformat(),
            "diagnosis": f"Diagnosis {i+1}",
            "notes": f"Notes for assessment {i+1}.",
            "subscores": []
        }
        response = await client.post(f"/api/v1/patients/{patient_id}/assessments/", json=assessment_data)
        assert response.status_code == 201
        created_assessment_ids.append(response.json()["assessment_id"])

    # Retrieve assessments for the patient
    response = await client.get(f"/api/v1/patients/{patient_id}/assessments/")
    assert response.status_code == 200
    response_data = response.json()

    assert isinstance(response_data, list)
    assert len(response_data) == num_assessments

    # Verify patient_id and sort order (descending by assessment_date)
    # assessment_dates was created in descending order (now, now-1day, now-2days)
    # so the response should match this order.
    expected_dates_iso = [date.isoformat() for date in assessment_dates]

    for i, assessment_resp in enumerate(response_data):
        assert assessment_resp["patient_id"] == patient_id
        assert "assessment_id" in assessment_resp
        # Verify the assessment_date matches the expected order
        response_assessment_date = parse_iso_datetime_str(assessment_resp["assessment_date"])

        # Compare ISO strings up to seconds precision, as DB might truncate microseconds differently
        # assessment_dates[i] is already a datetime object (timezone-aware)
        assert response_assessment_date.replace(microsecond=0) == assessment_dates[i].replace(microsecond=0)
        # Check basic fields
        assert assessment_resp["assessment_type"] == f"Test Type {i+1}"
        assert assessment_resp["score"] == 70.0 + i


# Test retrieving a single existing assessment
@pytest.mark.asyncio
async def test_get_single_assessment_exists(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    assessment_data_to_create = {
        "assessment_type": "Detailed Cognitive Profile",
        "score": 92.5,
        "max_possible_score": 100.0,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "diagnosis": "No cognitive impairment detected",
        "notes": "Excellent performance across all domains.",
        "subscores": [
            {"name": "Memory", "score": 45.0, "max_score": 50.0},
            {"name": "Attention", "score": 47.5, "max_score": 50.0},
        ],
    }

    # Create an assessment
    create_response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/",
        json=assessment_data_to_create
    )
    assert create_response.status_code == 201
    created_assessment = create_response.json()
    assessment_id = created_assessment["assessment_id"]

    # Retrieve the assessment by its ID
    get_response = await client.get(f"/api/v1/patients/{patient_id}/assessments/{assessment_id}")
    assert get_response.status_code == 200
    retrieved_assessment = get_response.json()

    # Verify the retrieved assessment data
    assert retrieved_assessment["assessment_id"] == assessment_id
    assert retrieved_assessment["patient_id"] == patient_id
    assert retrieved_assessment["assessment_type"] == assessment_data_to_create["assessment_type"]
    assert retrieved_assessment["score"] == assessment_data_to_create["score"]
    assert retrieved_assessment["max_possible_score"] == assessment_data_to_create["max_possible_score"]
    assert retrieved_assessment["diagnosis"] == assessment_data_to_create["diagnosis"]
    assert retrieved_assessment["notes"] == assessment_data_to_create["notes"]

    # Verify assessment_date (handling potential timezone differences as before)
    retrieved_assessment_date = parse_iso_datetime_str(retrieved_assessment["assessment_date"])
    original_assessment_date = parse_iso_datetime_str(assessment_data_to_create["assessment_date"])
    assert retrieved_assessment_date.replace(microsecond=0) == original_assessment_date.replace(microsecond=0)

    # Verify timestamps
    assert "created_at" in retrieved_assessment
    parse_iso_datetime_str(retrieved_assessment["created_at"]) 

    assert "updated_at" in retrieved_assessment
    parse_iso_datetime_str(retrieved_assessment["updated_at"])

    # Verify subscores (if any)
    assert len(retrieved_assessment["subscores"]) == len(assessment_data_to_create["subscores"])
    for i, subscore_resp in enumerate(retrieved_assessment["subscores"]):
        subscore_req = assessment_data_to_create["subscores"][i]
        assert "subscore_id" in subscore_resp
        assert subscore_resp["name"] == subscore_req["name"]
        assert subscore_resp["score"] == subscore_req["score"]
        assert subscore_resp["max_score"] == subscore_req["max_score"]
        # As per previous findings, 'assessment_id', 'created_at', 'updated_at' are not in the
        # SubscoreRead schema used in assessment_schema.py, so not asserting them here.

# Test attempting to retrieve a non-existent assessment
@pytest.mark.asyncio
async def test_get_single_assessment_not_exists(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"] # Get patient_id from fixture
    non_existent_assessment_id = 999999  # An ID that is unlikely to exist
    response = await client.get(f"/api/v1/patients/{patient_id}/assessments/{non_existent_assessment_id}")
    assert response.status_code == 404


# Test updating an assessment's own fields
@pytest.mark.asyncio
async def test_update_assessment_own_fields(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]

    # 1. Create an initial assessment
    initial_assessment_data = {
        "assessment_type": "Initial Mood Survey",
        "score": 75.0,
        "max_possible_score": 100.0,
        "assessment_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "diagnosis": "Mild anxiety",
        "notes": "Patient reports feeling generally well.",
        "subscores": [{"name": "Well-being", "score": 7.5, "max_score": 10.0}]
    }
    create_response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/",
        json=initial_assessment_data
    )
    assert create_response.status_code == 201
    created_assessment = create_response.json()
    assessment_id = created_assessment["assessment_id"]
    original_created_at = created_assessment["created_at"] # To check it doesn't change

    # 2. Prepare an update payload
    updated_assessment_date = datetime.now(timezone.utc).isoformat()
    update_payload = {
        "assessment_type": "Follow-up Mood Survey", # Changed
        "score": 80.0,  # Changed
        # max_possible_score remains unchanged
        "assessment_date": updated_assessment_date, # Changed
        "notes": "Patient reports improvement in mood.", # Changed
        # diagnosis remains unchanged
        # subscores are not updated in this test for own fields
    }

    # 3. Make a PUT request
    update_response = await client.put(
        f"/api/v1/patients/{patient_id}/assessments/{assessment_id}",
        json=update_payload
    )
    assert update_response.status_code == 200
    updated_assessment_response = update_response.json()

    # 4. Verify the response data reflects the updated values
    assert updated_assessment_response["assessment_id"] == assessment_id
    assert updated_assessment_response["patient_id"] == patient_id
    assert updated_assessment_response["assessment_type"] == update_payload["assessment_type"]
    assert updated_assessment_response["score"] == update_payload["score"]
    assert updated_assessment_response["notes"] == update_payload["notes"]

    # Handle 'Z' suffix for Python < 3.11 compatibility with fromisoformat
    retrieved_assessment_date = parse_iso_datetime_str(updated_assessment_response["assessment_date"])
    original_updated_date = parse_iso_datetime_str(updated_assessment_date)
    assert retrieved_assessment_date.replace(microsecond=0) == original_updated_date.replace(microsecond=0)

    # Verify fields that should not have changed from the update payload
    assert updated_assessment_response["max_possible_score"] == initial_assessment_data["max_possible_score"]
    assert updated_assessment_response["diagnosis"] == initial_assessment_data["diagnosis"] # Should remain
    
    response_created_at = parse_iso_datetime_str(updated_assessment_response["created_at"])
    original_created_at_dt = parse_iso_datetime_str(original_created_at)
    assert response_created_at == original_created_at_dt # created_at should not change

    assert "updated_at" in updated_assessment_response
    response_updated_at_dt = parse_iso_datetime_str(updated_assessment_response["updated_at"])
    assert response_updated_at_dt > original_created_at_dt


    # 5. Fetch the assessment again and verify persistence and unchanged fields
    get_response = await client.get(f"/api/v1/patients/{patient_id}/assessments/{assessment_id}")
    assert get_response.status_code == 200
    fetched_assessment = get_response.json()

    assert fetched_assessment["assessment_type"] == update_payload["assessment_type"]
    assert fetched_assessment["score"] == update_payload["score"]
    assert fetched_assessment["notes"] == update_payload["notes"]

    fetched_assessment_date_obj = parse_iso_datetime_str(fetched_assessment["assessment_date"])
    assert fetched_assessment_date_obj.replace(microsecond=0) == original_updated_date.replace(microsecond=0)

    # Verify fields that were not part of the update payload remained as they were initially
    assert fetched_assessment["max_possible_score"] == initial_assessment_data["max_possible_score"]
    assert fetched_assessment["diagnosis"] == initial_assessment_data["diagnosis"]
    assert len(fetched_assessment["subscores"]) == 1 # Subscores were not touched in this update
    assert fetched_assessment["subscores"][0]["name"] == initial_assessment_data["subscores"][0]["name"]
    
    fetched_created_at_dt = parse_iso_datetime_str(fetched_assessment["created_at"])
    assert fetched_created_at_dt == original_created_at_dt


# Test updating an assessment's subscores
@pytest.mark.asyncio
async def test_update_assessment_subscores(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]

    # 1. Create an initial assessment with subscores
    initial_assessment_data = {
        "assessment_type": "Comprehensive Skill Test",
        "score": 88.0,
        "assessment_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "subscores": [
            {"name": "Skill A", "score": 40.0, "max_score": 50.0}, # Will be updated
            {"name": "Skill B", "score": 48.0, "max_score": 50.0}  # Will be deleted
        ]
    }
    create_response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/",
        json=initial_assessment_data
    )
    assert create_response.status_code == 201
    created_assessment = create_response.json()
    assessment_id = created_assessment["assessment_id"]
    # original_subscore_a_id = next(s["subscore_id"] for s in created_assessment["subscores"] if s["name"] == "Skill A")

    # 2. Prepare an update payload for subscores
    # - Update Skill A, Delete Skill B, Add Skill C
    update_payload_subscores = {
        "subscores": [
            {"name": "Skill A", "score": 45.0, "max_score": 50.0}, # Updated score
            {"name": "Skill C", "score": 30.0, "max_score": 40.0}  # New subscore
        ]
        # Note: Skill B is omitted, so it should be deleted.
        # Other assessment fields (like score, notes) are not part of this payload,
        # so they should remain unchanged from their initial values.
    }

    # 3. Make a PUT request
    update_response = await client.put(
        f"/api/v1/patients/{patient_id}/assessments/{assessment_id}",
        json=update_payload_subscores # Send only subscores to test partial update behavior
    )
    assert update_response.status_code == 200
    updated_assessment_response = update_response.json()

    # 4. Verify the subscores in the response
    assert len(updated_assessment_response["subscores"]) == 2
    response_subscores_map = {s["name"]: s for s in updated_assessment_response["subscores"]}

    assert "Skill A" in response_subscores_map
    assert response_subscores_map["Skill A"]["score"] == 45.0
    # assert response_subscores_map["Skill A"]["subscore_id"] == original_subscore_a_id # Check if ID is retained - might be re-created

    assert "Skill C" in response_subscores_map
    assert response_subscores_map["Skill C"]["score"] == 30.0
    assert "subscore_id" in response_subscores_map["Skill C"] # New subscore should have an ID

    assert "Skill B" not in response_subscores_map # Skill B should be deleted

    # Verify that other assessment fields remained unchanged
    assert updated_assessment_response["assessment_type"] == initial_assessment_data["assessment_type"]
    assert updated_assessment_response["score"] == initial_assessment_data["score"]


    # 5. Fetch the assessment again and verify subscore changes persist
    get_response = await client.get(f"/api/v1/patients/{patient_id}/assessments/{assessment_id}")
    assert get_response.status_code == 200
    fetched_assessment = get_response.json()

    assert len(fetched_assessment["subscores"]) == 2
    fetched_subscores_map = {s["name"]: s for s in fetched_assessment["subscores"]}

    assert "Skill A" in fetched_subscores_map
    assert fetched_subscores_map["Skill A"]["score"] == 45.0

    assert "Skill C" in fetched_subscores_map
    assert fetched_subscores_map["Skill C"]["score"] == 30.0

    assert "Skill B" not in fetched_subscores_map


# Test attempting to update a non-existent assessment
@pytest.mark.asyncio
async def test_update_assessment_not_exists(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    non_existent_assessment_id = 999999  # An ID that is unlikely to exist
    update_payload = {"notes": "This should not apply."}

    response = await client.put(
        f"/api/v1/patients/{patient_id}/assessments/{non_existent_assessment_id}",
        json=update_payload
    )
    assert response.status_code == 404


# Test successfully deleting an existing assessment
@pytest.mark.asyncio
async def test_delete_assessment_exists(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]

    # 1. Create an assessment to delete
    assessment_data_to_create = {
        "assessment_type": "Temporary Assessment",
        "score": 50.0,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "notes": "This assessment will be deleted.",
    }
    create_response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/",
        json=assessment_data_to_create
    )
    assert create_response.status_code == 201
    created_assessment = create_response.json()
    assessment_id = created_assessment["assessment_id"]

    # 2. Make a DELETE request
    delete_response = await client.delete(
        f"/api/v1/patients/{patient_id}/assessments/{assessment_id}"
    )
    assert delete_response.status_code == 204

    # 3. Verify that attempting to GET the same assessment ID results in a 404
    get_response = await client.get(
        f"/api/v1/patients/{patient_id}/assessments/{assessment_id}"
    )
    assert get_response.status_code == 404


# Test attempting to delete a non-existent assessment
@pytest.mark.asyncio
async def test_delete_assessment_not_exists(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    non_existent_assessment_id = 999999  # An ID that is unlikely to exist

    delete_response = await client.delete(
        f"/api/v1/patients/{patient_id}/assessments/{non_existent_assessment_id}"
    )
    assert delete_response.status_code == 404


# Test creating an assessment with subscores
@pytest.mark.asyncio
async def test_create_assessment_with_subscores(client: AsyncClient, test_patient):
    patient_id = test_patient["patient_id"]
    assessment_data_with_subscores = {
        "assessment_type": "Speech Fluency Test",
        "score": 72.0,
        "max_possible_score": 100.0,
        "assessment_date": datetime.now(timezone.utc).isoformat(),
        "diagnosis": "Moderate dysarthria",
        "notes": "Difficulty with plosive sounds.",
        "subscores": [
            {"name": "Clarity", "score": 3.5, "max_score": 5.0},
            {"name": "Rate", "score": 4.0, "max_score": 5.0},
        ],
    }

    response = await client.post(
        f"/api/v1/patients/{patient_id}/assessments/",
        json=assessment_data_with_subscores
    )

    assert response.status_code == 201
    response_data = response.json()

    assert "assessment_id" in response_data
    assert response_data["assessment_type"] == assessment_data_with_subscores["assessment_type"]
    assert response_data["score"] == assessment_data_with_subscores["score"]
    # ... (add other assertions for top-level fields as in the previous test) ...
    assert response_data["patient_id"] == patient_id

    response_assessment_date = parse_iso_datetime_str(response_data["assessment_date"])
    original_assessment_date = parse_iso_datetime_str(assessment_data_with_subscores["assessment_date"])
    assert response_assessment_date.replace(microsecond=0) == original_assessment_date.replace(microsecond=0)

    assert "created_at" in response_data
    parse_iso_datetime_str(response_data["created_at"])

    assert "updated_at" in response_data
    parse_iso_datetime_str(response_data["updated_at"])

    # Check subscores
    assert len(response_data["subscores"]) == len(assessment_data_with_subscores["subscores"])
    for i, subscore_resp in enumerate(response_data["subscores"]):
        subscore_req = assessment_data_with_subscores["subscores"][i]
        assert "subscore_id" in subscore_resp
        assert subscore_resp["name"] == subscore_req["name"]
        assert subscore_resp["score"] == subscore_req["score"]
        assert subscore_resp["max_score"] == subscore_req["max_score"]
            # assert subscore_resp["assessment_id"] == response_data["assessment_id"] # assessment_id is not in SubscoreRead from assessment_schema.py
            # assert "created_at" in subscore_resp # created_at is not in SubscoreRead from assessment_schema.py
            # assert "updated_at" in subscore_resp # updated_at is not in SubscoreRead from assessment_schema.py
            # datetime.fromisoformat(subscore_resp["created_at"]) # created_at is not in SubscoreRead from assessment_schema.py
            # datetime.fromisoformat(subscore_resp["updated_at"]) # updated_at is not in SubscoreRead from assessment_schema.py
