import pytest

def test_survey_creation_and_questions(client):
    # 1. Create experiment
    exp_res = client.post("/api/experiments", json={
        "name": "Food App Survey Exp",
        "product_name": "QuickBite",
        "product_description": "Fast food delivery app",
        "target_audience": "Students and professionals",
        "research_objectives": ["Test pricing and delivery speed"],
        "number_of_personas": 3
    })
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    # 2. Create survey
    survey_res = client.post(f"/api/experiments/{exp_id}/surveys", json={
        "title": "Pricing & Feature Preferences",
        "description": "Survey regarding delivery fees and subscription passes."
    })
    assert survey_res.status_code == 201
    survey = survey_res.json()
    assert survey["title"] == "Pricing & Feature Preferences"
    survey_id = survey["id"]

    # 3. Add questions of diverse types (rating, yes_no, short_answer, opinion, open_ended)
    q1_res = client.post(f"/api/surveys/{survey_id}/questions", json={
        "question_text": "Rate the importance of delivery speed on a 1-5 scale.",
        "question_type": "rating",
        "options": ["1-5"],
        "order": 1
    })
    assert q1_res.status_code == 201
    assert q1_res.json()["question_type"] == "rating"

    q2_res = client.post(f"/api/surveys/{survey_id}/questions", json={
        "question_text": "Would you subscribe to a ₹199 monthly pass for zero delivery fees?",
        "question_type": "yes_no",
        "options": ["Yes", "No"],
        "order": 2
    })
    assert q2_res.status_code == 201

    q3_res = client.post(f"/api/surveys/{survey_id}/questions", json={
        "question_text": "What is your main frustration with current food delivery apps?",
        "question_type": "open_ended",
        "order": 3
    })
    assert q3_res.status_code == 201

    # 4. Generate Personas for experiment
    gen_res = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 3})
    assert gen_res.status_code == 201

    # 5. Run survey
    run_res = client.post(f"/api/surveys/{survey_id}/run")
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["survey_id"] == survey_id
    assert run_data["total_personas"] == 3
    assert run_data["total_responses_generated"] == 9 # 3 personas * 3 questions

    # 6. Retrieve Grouped Responses
    grouped_res = client.get(f"/api/surveys/{survey_id}/responses")
    assert grouped_res.status_code == 200
    g_data = grouped_res.json()
    assert len(g_data["grouped_by_question"]) == 3
    
    first_group = g_data["grouped_by_question"][0]
    assert len(first_group["responses"]) == 3
    assert "persona_name" in first_group["responses"][0]

def test_survey_duplicate_execution_handling(client):
    # Setup exp, survey, persona, question
    exp_res = client.post("/api/experiments", json={
        "name": "Duplicate Run Exp",
        "product_name": "App",
        "product_description": "Desc",
        "target_audience": "Audience",
        "research_objectives": ["Obj"],
        "number_of_personas": 1
    })
    exp_id = exp_res.json()["id"]

    survey_res = client.post(f"/api/experiments/{exp_id}/surveys", json={"title": "Test"})
    survey_id = survey_res.json()["id"]

    client.post(f"/api/surveys/{survey_id}/questions", json={
        "question_text": "Opinion question",
        "question_type": "opinion"
    })

    client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 1})

    # Run 1
    run1 = client.post(f"/api/surveys/{survey_id}/run")
    assert run1.status_code == 200
    cnt1 = len(run1.json()["responses"])

    # Run 2 (Should safely return existing responses without duplicating DB rows)
    run2 = client.post(f"/api/surveys/{survey_id}/run")
    assert run2.status_code == 200
    cnt2 = len(run2.json()["responses"])
    assert cnt1 == cnt2
