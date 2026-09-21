def test_full_persona_conversation_and_consistency_workflow(client):
    """
    Tests the complete end-to-end milestone workflow:
    Create Experiment -> Generate Personas -> Retrieve Persona ->
    Q1: "Would you pay ₹299 per month for unlimited food delivery?" ->
    Store Memory ->
    Q2: "Why do you think it is expensive?" ->
    Retrieve Previous Memory & Generate Consistent Response.
    """
    # 1. Create Experiment
    exp_payload = {
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
    exp_res = client.post("/api/experiments", json=exp_payload)
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    # 2. Generate 5 Personas
    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 5})
    assert gen_res.status_code == 201
    personas = gen_res.json()["personas"]
    assert len(personas) == 5

    # Select student persona (Rahul Sharma or first persona)
    persona_id = personas[0]["id"]

    # 3. Retrieve Persona
    get_persona_res = client.get(f"/api/personas/{persona_id}")
    assert get_persona_res.status_code == 200
    persona_data = get_persona_res.json()
    assert persona_data["id"] == persona_id

    # 4. Q1: Ask about pricing subscription
    q1_payload = {
        "message": "Would you pay ₹299 per month for unlimited food delivery?"
    }
    q1_res = client.post(f"/api/personas/{persona_id}/conversation", json=q1_payload)
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert q1_data["persona_id"] == persona_id
    assert len(q1_data["response"]) > 0
    assert q1_data["memory_updated"] is True

    # 5. Check Memory API to verify opinion was stored
    mem_res = client.get(f"/api/personas/{persona_id}/memory")
    assert mem_res.status_code == 200
    mem_data = mem_res.json()
    assert mem_data["persona_id"] == persona_id
    assert len(mem_data["conversation_history"]) == 1

    # 6. Q2: Follow-up question relying on established memory
    q2_payload = {
        "message": "Why do you think it is expensive?"
    }
    q2_res = client.post(f"/api/personas/{persona_id}/conversation", json=q2_payload)
    assert q2_res.status_code == 200
    q2_data = q2_res.json()
    assert q2_data["persona_id"] == persona_id
    assert len(q2_data["response"]) > 0

    # 7. Check Memory API again to verify multi-turn conversation history
    mem_res_2 = client.get(f"/api/personas/{persona_id}/memory")
    assert mem_res_2.status_code == 200
    mem_data_2 = mem_res_2.json()
    assert len(mem_data_2["conversation_history"]) == 2
    
    # Ensure previous answers are recorded
    first_turn = mem_data_2["conversation_history"][0]
    second_turn = mem_data_2["conversation_history"][1]
    assert first_turn["user_message"] == q1_payload["message"]
    assert second_turn["user_message"] == q2_payload["message"]
