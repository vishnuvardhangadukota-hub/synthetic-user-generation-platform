def test_get_persona_memory_empty_and_populated(client):
    # Create experiment & persona
    exp_payload = {
        "name": "Memory Test Exp",
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

    # Initial memory view
    mem_res = client.get(f"/api/personas/{persona_id}/memory")
    assert mem_res.status_code == 200
    data = mem_res.json()
    assert data["persona_id"] == persona_id
    assert "core_attributes" in data
    assert "name" in data["core_attributes"]
    assert "age" in data["core_attributes"]
    assert "behavioral_memories" in data
    assert "opinions" in data
    assert "conversation_history" in data
    assert len(data["conversation_history"]) == 0

    # Add conversation
    client.post(f"/api/personas/{persona_id}/conversation", json={"message": "What is your main priority when ordering food?"})

    # Updated memory view
    mem_res_updated = client.get(f"/api/personas/{persona_id}/memory")
    assert mem_res_updated.status_code == 200
    data_updated = mem_res_updated.json()
    assert len(data_updated["conversation_history"]) == 1
