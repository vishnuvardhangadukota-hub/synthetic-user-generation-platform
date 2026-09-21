def test_create_experiment_success(client):
    payload = {
        "name": "Food Delivery User Research",
        "product_name": "QuickBite",
        "product_description": "A food delivery application focused on affordable and fast delivery.",
        "target_audience": "College students aged 18-25 in Hyderabad",
        "research_objectives": [
            "Understand price sensitivity",
            "Understand delivery time preferences",
            "Understand subscription interest"
        ],
        "number_of_personas": 5
    }
    response = client.post("/api/experiments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Food Delivery User Research"
    assert data["product_name"] == "QuickBite"
    assert len(data["research_objectives"]) == 3
    assert data["number_of_personas"] == 5
    assert "id" in data

def test_create_experiment_validation_error(client):
    # Empty name & invalid personas count (>20)
    payload = {
        "name": "  ",
        "product_name": "QuickBite",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": [],
        "number_of_personas": 25
    }
    response = client.post("/api/experiments", json=payload)
    assert response.status_code == 422

def test_get_all_experiments(client):
    payload = {
        "name": "Test Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 3
    }
    client.post("/api/experiments", json=payload)
    response = client.get("/api/experiments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_experiment_by_id(client):
    payload = {
        "name": "Target Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 3
    }
    create_res = client.post("/api/experiments", json=payload)
    exp_id = create_res.json()["id"]

    response = client.get(f"/api/experiments/{exp_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Target Exp"

    # Non-existent ID
    response = client.get("/api/experiments/non_existent_id")
    assert response.status_code == 404

def test_update_experiment(client):
    payload = {
        "name": "Original Name",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 3
    }
    create_res = client.post("/api/experiments", json=payload)
    exp_id = create_res.json()["id"]

    update_payload = {"name": "Updated Name", "number_of_personas": 10}
    response = client.put(f"/api/experiments/{exp_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["number_of_personas"] == 10

def test_delete_experiment(client):
    payload = {
        "name": "Delete Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 3
    }
    create_res = client.post("/api/experiments", json=payload)
    exp_id = create_res.json()["id"]

    response = client.delete(f"/api/experiments/{exp_id}")
    assert response.status_code == 200

    # Ensure deleted
    response = client.get(f"/api/experiments/{exp_id}")
    assert response.status_code == 404
