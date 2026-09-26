def test_usage_score_calculation_and_segmentation(client):
    # 1. Create experiment & generate personas
    exp_res = client.post("/api/experiments", json={
        "name": "EdTech App Exp",
        "product_name": "LearnPulse",
        "product_description": "AI tutoring app for university students",
        "target_audience": "Undergraduate students in Hyderabad",
        "research_objectives": ["Test usage intent"],
        "number_of_personas": 3
    })
    exp_id = exp_res.json()["id"]

    client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 3})

    # 2. Calculate Usage Score
    score_res = client.post(f"/api/experiments/{exp_id}/usage-score", json={
        "custom_question": "How likely are you to use LearnPulse for weekly exam prep?"
    })
    assert score_res.status_code == 201
    data = score_res.json()

    assert data["experiment_id"] == exp_id
    assert "overall_score" in data
    assert "would_use_percentage" in data
    assert "segmentation_breakdown" in data
    assert "by_age_group" in data["segmentation_breakdown"]
    assert "by_occupation" in data["segmentation_breakdown"]
    assert "calculation_method" in data
    assert "limitations" in data
    assert "DISCLAIMER" in data["limitations"].upper()
    assert len(data["persona_scores"]) == 3

    # 3. Retrieve Usage Score GET endpoint
    get_res = client.get(f"/api/experiments/{exp_id}/usage-score")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]
