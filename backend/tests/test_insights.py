def test_generate_and_retrieve_insights(client):
    # 1. Create experiment
    exp_res = client.post("/api/experiments", json={
        "name": "Insight Exp",
        "product_name": "QuickBite",
        "product_description": "Food delivery app",
        "target_audience": "Students & professionals",
        "research_objectives": ["Analyze price sensitivity"],
        "number_of_personas": 2
    })
    exp_id = exp_res.json()["id"]

    # 2. Generate personas
    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 2})
    personas = gen_res.json()["personas"]

    # 3. Create & run survey
    survey_res = client.post(f"/api/experiments/{exp_id}/surveys", json={"title": "Insight Survey"})
    s_id = survey_res.json()["id"]

    client.post(f"/api/surveys/{s_id}/questions", json={
        "question_text": "Would you pay ₹299 per month for unlimited delivery?",
        "question_type": "yes_no"
    })

    client.post(f"/api/surveys/{s_id}/run")

    # 4. Have an interview conversation turn
    p_id = personas[0]["id"]
    client.post(f"/api/personas/{p_id}/conversation", json={
        "message": "Why do you prefer ordering online?"
    })

    # 5. Generate Insights
    ins_res = client.post(f"/api/experiments/{exp_id}/insights")
    assert ins_res.status_code == 201
    data = ins_res.json()

    assert data["experiment_id"] == exp_id
    assert "recurring_themes" in data
    assert "sentiment_distribution" in data
    assert "agreement_patterns" in data
    assert "disagreements" in data
    assert "behavioral_trends" in data
    assert "supporting_references" in data
    assert "limitations" in data
    assert "synthetic" in data["limitations"].lower()

    # 6. Retrieve Insights GET endpoint
    get_res = client.get(f"/api/experiments/{exp_id}/insights")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]
