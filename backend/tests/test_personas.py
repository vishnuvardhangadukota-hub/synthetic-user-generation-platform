def test_generate_personas(client):
    # 1. Create experiment
    exp_payload = {
        "name": "Food Delivery User Research",
        "product_name": "QuickBite",
        "product_description": "A food delivery application focused on affordable and fast delivery.",
        "target_audience": "College students aged 18-25 in Hyderabad",
        "research_objectives": [
            "Understand price sensitivity",
            "Understand delivery time preferences"
        ],
        "number_of_personas": 5
    }
    exp_res = client.post("/api/experiments", json=exp_payload)
    exp_id = exp_res.json()["id"]

    # 2. Generate personas
    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 5})
    assert gen_res.status_code == 201
    data = gen_res.json()
    assert data["experiment_id"] == exp_id
    personas = data["personas"]
    assert len(personas) == 5

    first_persona = personas[0]
    assert "name" in first_persona
    assert "age" in first_persona
    assert "occupation" in first_persona
    assert "personality_traits" in first_persona
    assert "behavioral_patterns" in first_persona
    assert "psychological_profile" in first_persona

def test_get_personas_for_experiment(client):
    exp_payload = {
        "name": "Exp 2",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 2
    }
    exp_res = client.post("/api/experiments", json=exp_payload)
    exp_id = exp_res.json()["id"]

    client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 2})

    response = client.get(f"/api/experiments/{exp_id}/personas")
    assert response.status_code == 200
    personas = response.json()
    assert len(personas) == 2

def test_get_persona_by_id(client):
    exp_payload = {
        "name": "Exp 3",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 1
    }
    exp_res = client.post("/api/experiments", json=exp_payload)
    exp_id = exp_res.json()["id"]

    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 1})
    persona_id = gen_res.json()["personas"][0]["id"]

    response = client.get(f"/api/personas/{persona_id}")
    assert response.status_code == 200
    assert response.json()["id"] == persona_id

def test_delete_persona(client):
    exp_payload = {
        "name": "Exp 4",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj 1"],
        "number_of_personas": 1
    }
    exp_res = client.post("/api/experiments", json=exp_payload)
    exp_id = exp_res.json()["id"]

    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 1})
    persona_id = gen_res.json()["personas"][0]["id"]

    del_res = client.delete(f"/api/personas/{persona_id}")
    assert del_res.status_code == 200

    get_res = client.get(f"/api/personas/{persona_id}")
    assert get_res.status_code == 404
