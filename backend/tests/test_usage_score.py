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


def test_analytics_overview_endpoint(client):
    """Analytics overview returns platform-wide aggregated metrics."""
    # 1. Before creating data, endpoint returns 200 with initial counters
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_experiments" in data
    assert "total_personas" in data
    assert "total_surveys" in data
    assert "total_responses" in data
    assert "total_insights" in data
    assert "total_usage_scores" in data
    assert data["total_experiments"] == 0
    assert data["total_personas"] == 0

    # 2. Create an experiment & generate personas
    exp_res = client.post("/api/experiments", json={
        "name": "Analytics Test Exp",
        "product_name": "TestProduct",
        "product_description": "Testing product analytics overview",
        "target_audience": "Researchers",
        "research_objectives": ["Evaluate metrics"],
        "number_of_personas": 2
    })
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 2})

    # 3. Verify counts reflect in analytics overview
    res_after = client.get("/api/analytics/overview")
    assert res_after.status_code == 200
    data_after = res_after.json()
    assert data_after["total_experiments"] == 1
    assert data_after["total_personas"] == 2

