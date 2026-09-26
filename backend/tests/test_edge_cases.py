def test_invalid_ids_return_404(client):
    assert client.get("/api/experiments/non_existent_exp").status_code == 404
    assert client.get("/api/personas/non_existent_persona").status_code == 404
    assert client.get("/api/experiments/non_existent_exp/surveys").status_code == 404
    assert client.get("/api/surveys/non_existent_srv/responses").status_code == 404
    assert client.get("/api/experiments/non_existent_exp/insights").status_code == 404
    assert client.get("/api/experiments/non_existent_exp/usage-score").status_code == 404

def test_run_survey_without_questions_returns_400(client):
    # Exp & survey with 0 questions
    exp_res = client.post("/api/experiments", json={
        "name": "Empty Survey Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj"],
        "number_of_personas": 1
    })
    exp_id = exp_res.json()["id"]

    client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 1})

    survey_res = client.post(f"/api/experiments/{exp_id}/surveys", json={"title": "Empty Survey"})
    s_id = survey_res.json()["id"]

    # Run should fail with 400
    run_res = client.post(f"/api/surveys/{s_id}/run")
    assert run_res.status_code == 400
    assert "no questions" in run_res.json()["error"].lower()

def test_insights_without_data_returns_400(client):
    exp_res = client.post("/api/experiments", json={
        "name": "No Data Insights Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj"],
        "number_of_personas": 1
    })
    exp_id = exp_res.json()["id"]

    ins_res = client.post(f"/api/experiments/{exp_id}/insights")
    assert ins_res.status_code == 400
    assert "no survey responses or interview conversations" in ins_res.json()["error"].lower()

def test_multi_domain_persona_consistency(client):
    """Verifies persona identity and preference consistency across EdTech and Fitness product domains."""
    # Domain 1: EdTech Platform
    exp1_res = client.post("/api/experiments", json={
        "name": "EdTech Domain",
        "product_name": "CodeMaster AI",
        "product_description": "AI coding mentor for students",
        "target_audience": "Computer Science undergrads",
        "research_objectives": ["Test pricing tolerance"],
        "number_of_personas": 2
    })
    exp1_id = exp1_res.json()["id"]
    gen1 = client.post(f"/api/experiments/{exp1_id}/personas/generate", json={"number_of_personas": 2})
    assert gen1.status_code == 201

    # Domain 2: Fitness & Health App
    exp2_res = client.post("/api/experiments", json={
        "name": "Fitness Domain",
        "product_name": "FitPulse",
        "product_description": "Personalized workout and meal planner",
        "target_audience": "Working professionals in Hyderabad",
        "research_objectives": ["Understand workout tracking habits"],
        "number_of_personas": 2
    })
    exp2_id = exp2_res.json()["id"]
    gen2 = client.post(f"/api/experiments/{exp2_id}/personas/generate", json={"number_of_personas": 2})
    assert gen2.status_code == 201
