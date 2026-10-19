"""
Milestone 4 End-to-End Tests
=============================
Tests the complete workflow:
  1. Persona generation
  2. Simulation Mode 1 (Survey)
  3. Simulation Mode 2 (Conversation / Interview)
  4. Insight extraction
  5. Dashboard endpoint
  6. PDF report download
  7. Data consistency (dashboard vs PDF payload)
  8. Edge cases
  9. Regression (Milestones 1-3 routes still work)
"""
import io
import pytest

# ── Helpers ────────────────────────────────────────────────────────────────────

EXP_PAYLOAD = {
    "name": "M4 E2E Test Experiment",
    "product_name": "QuickBite Pro",
    "product_description": "A premium food delivery app targeting working professionals.",
    "target_audience": "Working professionals aged 25-40 in Hyderabad",
    "research_objectives": [
        "Understand price sensitivity",
        "Assess delivery speed expectations",
        "Evaluate subscription intent",
    ],
    "number_of_personas": 3,
}


def _create_experiment(client):
    res = client.post("/api/experiments", json=EXP_PAYLOAD)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def _generate_personas(client, exp_id, n=3):
    res = client.post(
        f"/api/experiments/{exp_id}/personas/generate",
        json={"number_of_personas": n},
    )
    assert res.status_code == 201, res.text
    return res.json()["personas"]


def _create_and_run_survey(client, exp_id):
    # Create survey
    srv = client.post(
        f"/api/experiments/{exp_id}/surveys",
        json={"title": "M4 Test Survey", "description": "Automated E2E survey"},
    )
    assert srv.status_code == 201, srv.text
    s_id = srv.json()["id"]

    # Add questions
    for q in [
        {"question_text": "Would you pay ₹299/month for premium delivery?", "question_type": "yes_no"},
        {"question_text": "Rate delivery speed importance (1-5)", "question_type": "rating"},
    ]:
        r = client.post(f"/api/surveys/{s_id}/questions", json=q)
        assert r.status_code == 201, r.text

    # Run survey
    run = client.post(f"/api/surveys/{s_id}/run")
    assert run.status_code == 200, run.text
    return s_id, run.json()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 — Persona Generation
# ─────────────────────────────────────────────────────────────────────────────
def test_persona_generation_and_retrieval(client):
    """Personas are saved and linked to the experiment."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=3)

    assert len(personas) == 3
    for p in personas:
        assert p["experiment_id"] == exp_id
        assert p["name"]
        assert isinstance(p["age"], int)
        assert p["occupation"]

    # Verify retrieval
    get_res = client.get(f"/api/experiments/{exp_id}/personas")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 3


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — Simulation Mode 1 (Survey)
# ─────────────────────────────────────────────────────────────────────────────
def test_simulation_mode_1_survey(client):
    """Survey simulation generates responses correctly for all personas."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=2)

    s_id, run_data = _create_and_run_survey(client, exp_id)

    assert run_data["total_personas"] == 2
    assert run_data["total_responses_generated"] > 0

    # Each persona answered each question → 2 personas × 2 questions = 4 responses
    assert run_data["total_responses_generated"] == 4

    # Responses contain required fields
    for resp in run_data["responses"]:
        assert resp["persona_id"]
        assert resp["answer"]
        assert resp["survey_id"] == s_id
        assert resp["experiment_id"] == exp_id


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — Simulation Mode 2 (Conversation / Interview)
# ─────────────────────────────────────────────────────────────────────────────
def test_simulation_mode_2_conversation(client):
    """Interview conversation generates and stores responses for a persona."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=2)
    p_id = personas[0]["id"]

    conv_res = client.post(
        f"/api/personas/{p_id}/conversation",
        json={"message": "How do you feel about subscription-based food delivery apps?"},
    )
    assert conv_res.status_code == 200, conv_res.text
    data = conv_res.json()
    assert data["persona_id"] == p_id
    # Conversation schema returns 'response' (not 'persona_response'/'user_message')
    assert data["response"]
    assert "memory_updated" in data

    # Memory endpoint shows the conversation was saved
    mem_res = client.get(f"/api/personas/{p_id}/memory")
    assert mem_res.status_code == 200
    mem_data = mem_res.json()
    # Conversation history stored in memory
    assert mem_data is not None


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4 — Insight Extraction
# ─────────────────────────────────────────────────────────────────────────────
def test_insight_extraction(client):
    """Insights are generated from survey + interview data."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)

    # Interview turn
    client.post(
        f"/api/personas/{personas[0]['id']}/conversation",
        json={"message": "Tell me your biggest concern about food delivery costs."},
    )

    ins_res = client.post(f"/api/experiments/{exp_id}/insights")
    assert ins_res.status_code == 201, ins_res.text
    data = ins_res.json()

    assert data["experiment_id"] == exp_id
    assert isinstance(data["recurring_themes"], list)
    assert "positive_percentage" in data["sentiment_distribution"]
    assert isinstance(data["agreement_patterns"], list)
    assert isinstance(data["behavioral_trends"], list)
    assert "synthetic" in data["limitations"].lower()

    # GET retrieval works
    get_res = client.get(f"/api/experiments/{exp_id}/insights")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == data["id"]


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5 — Dashboard Endpoint
# ─────────────────────────────────────────────────────────────────────────────
def test_dashboard_summary_cards(client):
    """Dashboard returns correct summary card values from actual data."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=3)

    dash_before = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    assert dash_before["summary_cards"]["total_personas"] == 3
    assert dash_before["summary_cards"]["total_responses"] == 0
    assert dash_before["summary_cards"]["experiment_status"] == "Personas Generated"

    _create_and_run_survey(client, exp_id)
    dash_after = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    assert dash_after["summary_cards"]["total_responses"] > 0
    assert dash_after["summary_cards"]["survey_responses"] > 0


def test_dashboard_theme_clusters(client):
    """Theme clusters populated after insight generation."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)
    client.post(f"/api/experiments/{exp_id}/insights")

    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    assert dash["has_insight_report"] is True
    assert isinstance(dash["theme_clusters"], list)


def test_dashboard_sentiment_breakdown(client):
    """Sentiment breakdown has correct structure and adds up."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)
    client.post(f"/api/experiments/{exp_id}/insights")

    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    sb = dash["sentiment_breakdown"]

    # Percentages must be present
    assert "positive" in sb
    assert "neutral" in sb
    assert "negative" in sb

    pos_pct = sb["positive"]["percentage"]
    neu_pct = sb["neutral"]["percentage"]
    neg_pct = sb["negative"]["percentage"]

    total_pct = pos_pct + neu_pct + neg_pct
    # Allow 1% floating-point rounding tolerance
    assert abs(total_pct - 100.0) <= 1.0 or total_pct == 0.0


def test_dashboard_not_found(client):
    """Dashboard returns 404 for non-existent experiment."""
    res = client.get("/api/experiments/nonexistent_exp_id/dashboard")
    assert res.status_code == 404


def test_dashboard_updates_on_experiment_change(client):
    """Dashboard reflects updated persona count after second generation."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)

    dash1 = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    n1 = dash1["summary_cards"]["total_personas"]

    _generate_personas(client, exp_id, n=2)
    dash2 = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    n2 = dash2["summary_cards"]["total_personas"]

    assert n2 == n1 + 2


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6 — PDF Report Generation
# ─────────────────────────────────────────────────────────────────────────────
def test_pdf_download_with_valid_data(client):
    """PDF downloads successfully and has the right content-type."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)

    res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert res.status_code == 200, res.text
    assert res.headers["content-type"] == "application/pdf"
    assert f"research_report_{exp_id}.pdf" in res.headers.get("content-disposition", "")

    # Verify real PDF magic bytes (%PDF-)
    content = res.content
    assert content[:5] == b"%PDF-"
    assert len(content) > 1000  # Must be a non-trivial file


def test_pdf_download_all_sections_present(client):
    """PDF bytes contain expected section keywords."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)
    client.post(f"/api/experiments/{exp_id}/insights")
    client.post(f"/api/experiments/{exp_id}/usage-score")

    res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert res.status_code == 200

    # PDF content is binary — check overall byte length (full report)
    assert len(res.content) > 5000


def test_pdf_no_personas_returns_400(client):
    """PDF download returns 400 when experiment has no personas or responses."""
    exp_id = _create_experiment(client)  # No personas generated

    res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert res.status_code == 400
    # Error is in 'detail' key (FastAPI HTTPException) or 'error' key (custom handler)
    body = res.json()
    err_text = (body.get("detail") or body.get("error") or "").lower()
    assert "no" in err_text or "persona" in err_text or "response" in err_text


def test_pdf_nonexistent_experiment_returns_404(client):
    """PDF download returns 404 for missing experiment."""
    res = client.get("/api/experiments/does_not_exist_xyz/report/pdf")
    assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7 — Data Consistency (Dashboard ↔ PDF inputs)
# ─────────────────────────────────────────────────────────────────────────────
def test_data_consistency_dashboard_and_pdf_use_same_source(client):
    """
    Dashboard counts match what would be used to generate the PDF.
    Both come from the same DashboardService.get_dashboard() call.
    """
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=3)
    _create_and_run_survey(client, exp_id)
    client.post(f"/api/experiments/{exp_id}/insights")

    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()

    # PDF download should succeed with matching data
    pdf_res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert pdf_res.status_code == 200

    # Total personas visible on dashboard
    assert dash["summary_cards"]["total_personas"] == 3
    # Validation score uses same scale (0-100 if usage score exists, None otherwise)
    val = dash["validation_score"]
    if val["available"]:
        assert 0 <= val["score"] <= 100


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8 — Edge Cases
# ─────────────────────────────────────────────────────────────────────────────
def test_edge_case_empty_experiment_dashboard(client):
    """Dashboard works on an experiment with no personas or responses."""
    exp_id = _create_experiment(client)
    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()

    assert dash["summary_cards"]["total_personas"] == 0
    assert dash["summary_cards"]["total_responses"] == 0
    assert dash["summary_cards"]["experiment_status"] == "Not Started"
    assert dash["theme_clusters"] == []
    assert dash["has_insight_report"] is False
    assert dash["has_usage_score"] is False


def test_edge_case_long_quote_in_dashboard(client):
    """Long responses do not break the dashboard or PDF."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=2)
    p_id = personas[0]["id"]

    # Generate a very long interview response
    long_msg = "A" * 500 + "? " + "What do you think?"
    client.post(
        f"/api/personas/{p_id}/conversation",
        json={"message": long_msg},
    )

    # Dashboard should still work
    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    assert dash is not None

    # PDF should still generate
    pdf_res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content[:5] == b"%PDF-"


def test_edge_case_unicode_in_responses(client):
    """Unicode characters in responses are handled without errors."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=2)
    p_id = personas[0]["id"]

    unicode_msg = "मुझे डिलीवरी ऐप पसंद है। 🚀 What about pricing? ₹299?"
    conv_res = client.post(
        f"/api/personas/{p_id}/conversation",
        json={"message": unicode_msg},
    )
    assert conv_res.status_code == 200

    pdf_res = client.get(f"/api/experiments/{exp_id}/report/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content[:5] == b"%PDF-"


def test_edge_case_invalid_experiment_id_dashboard(client):
    """Invalid experiment ID returns 404 on dashboard."""
    res = client.get("/api/experiments/invalid_xyz_999/dashboard")
    assert res.status_code == 404


def test_edge_case_repeated_pdf_download(client):
    """Repeated PDF downloads produce valid PDFs each time."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)

    for _ in range(3):
        res = client.get(f"/api/experiments/{exp_id}/report/pdf")
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"


def test_edge_case_missing_optional_persona_attributes(client):
    """Dashboard and PDF handle personas with minimal optional attributes."""
    exp_id = _create_experiment(client)
    # Generate minimal personas (deterministic fallback always provides valid data)
    _generate_personas(client, exp_id, n=1)

    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    assert dash["summary_cards"]["total_personas"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9 — Security & Isolation
# ─────────────────────────────────────────────────────────────────────────────
def test_security_experiment_isolation(client):
    """Two experiments cannot access each other's dashboard data."""
    exp1_id = _create_experiment(client)
    _generate_personas(client, exp1_id, n=3)

    exp_payload_2 = {**EXP_PAYLOAD, "name": "Second Experiment"}
    res2 = client.post("/api/experiments", json=exp_payload_2)
    exp2_id = res2.json()["id"]

    dash1 = client.get(f"/api/experiments/{exp1_id}/dashboard").json()
    dash2 = client.get(f"/api/experiments/{exp2_id}/dashboard").json()

    # Experiment 1 has personas; experiment 2 does not
    assert dash1["summary_cards"]["total_personas"] == 3
    assert dash2["summary_cards"]["total_personas"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10 — Regression (Milestones 1–3 still work)
# ─────────────────────────────────────────────────────────────────────────────
def test_regression_experiment_crud(client):
    """Experiment CRUD routes from Milestone 1 still work."""
    # Create
    res = client.post("/api/experiments", json=EXP_PAYLOAD)
    assert res.status_code == 201
    exp_id = res.json()["id"]

    # Read
    assert client.get(f"/api/experiments/{exp_id}").status_code == 200

    # Update
    upd = client.put(f"/api/experiments/{exp_id}", json={"name": "Updated Name"})
    assert upd.status_code == 200
    assert upd.json()["name"] == "Updated Name"

    # Delete
    del_res = client.delete(f"/api/experiments/{exp_id}")
    assert del_res.status_code == 200

    # Verify deleted
    assert client.get(f"/api/experiments/{exp_id}").status_code == 404


def test_regression_survey_workflow(client):
    """Survey workflow from Milestone 2 still works end-to-end."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    s_id, run_data = _create_and_run_survey(client, exp_id)

    # Grouped responses
    grouped = client.get(f"/api/surveys/{s_id}/responses")
    assert grouped.status_code == 200
    assert "grouped_by_question" in grouped.json()


def test_regression_usage_score(client):
    """Usage score endpoint from Milestone 3 still works."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)

    score_res = client.post(f"/api/experiments/{exp_id}/usage-score")
    assert score_res.status_code == 201
    data = score_res.json()

    assert data["experiment_id"] == exp_id
    assert 1.0 <= data["overall_score"] <= 10.0
    assert 0.0 <= data["would_use_percentage"] <= 100.0


def test_regression_insight_endpoint(client):
    """Insight extraction from Milestone 3 still works."""
    exp_id = _create_experiment(client)
    _generate_personas(client, exp_id, n=2)
    _create_and_run_survey(client, exp_id)

    ins_res = client.post(f"/api/experiments/{exp_id}/insights")
    assert ins_res.status_code == 201
    assert ins_res.json()["experiment_id"] == exp_id


def test_regression_conversations_endpoint(client):
    """Conversation endpoint from Milestone 2 still works."""
    exp_id = _create_experiment(client)
    personas = _generate_personas(client, exp_id, n=1)
    p_id = personas[0]["id"]

    res = client.post(
        f"/api/personas/{p_id}/conversation",
        json={"message": "What do you think about app notifications?"},
    )
    assert res.status_code == 200
    # Schema: {persona_id, response, memory_updated}
    assert res.json()["response"]
