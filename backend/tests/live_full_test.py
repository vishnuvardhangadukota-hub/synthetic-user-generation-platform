"""
Live Full API Test Suite — Tests every endpoint against the running server.
Run: python tests/live_full_test.py
"""
import httpx
import sys

BASE = "http://localhost:8000"
client = httpx.Client(base_url=BASE, timeout=30.0)
results = []
exp_id = None
persona_ids = []
survey_id = None

EXP_PAYLOAD = {
    "name": "Live API Test QuickBite Pro",
    "product_name": "QuickBite Pro",
    "product_description": "Premium food delivery app for working professionals",
    "target_audience": "Working professionals aged 25-40 in Hyderabad",
    "research_objectives": [
        "Understand price sensitivity",
        "Assess delivery speed expectations",
        "Evaluate subscription intent",
    ],
    "number_of_personas": 3,
}


def check(section, name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append({"section": section, "test": name, "status": status, "detail": str(detail)})
    tag = "OK  " if condition else "FAIL"
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{tag}] {name}{suffix}")


def sec(title):
    print(f"\n=== {title} ===")


# ── 1. HEALTH ─────────────────────────────────────────────────────────────────
sec("1. HEALTH CHECK & API DOCS")
r = client.get("/")
check("Health", "GET / 200", r.status_code == 200, f"status={r.status_code}")
check("Health", "status=online", r.json().get("status") == "online")
r_docs = client.get("/docs")
check("Health", "GET /docs 200 (Swagger)", r_docs.status_code == 200)
r_redoc = client.get("/redoc")
check("Health", "GET /redoc 200", r_redoc.status_code == 200)
r_oapi = client.get("/openapi.json")
check("Health", "GET /openapi.json 200", r_oapi.status_code == 200)
if r_oapi.status_code == 200:
    paths = list(r_oapi.json().get("paths", {}).keys())
    print(f"  Registered routes: {len(paths)}")
    check("Health", "dashboard route in OpenAPI", any("dashboard" in p for p in paths))
    check("Health", "pdf route in OpenAPI", any("pdf" in p for p in paths))

# ── 2. EXPERIMENT CRUD ────────────────────────────────────────────────────────
sec("2. EXPERIMENT CRUD (Milestone 1)")
r = client.post("/api/experiments", json=EXP_PAYLOAD)
check("Experiments", "POST create 201", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    exp_id = r.json()["id"]
    print(f"  exp_id={exp_id}")
    check("Experiments", "response has id", bool(exp_id))
    check("Experiments", "product_name matches", r.json()["product_name"] == "QuickBite Pro")

r2 = client.get("/api/experiments")
check("Experiments", "GET all 200", r2.status_code == 200)
check("Experiments", "returns list", isinstance(r2.json(), list))

r3 = client.get(f"/api/experiments/{exp_id}")
check("Experiments", "GET by id 200", r3.status_code == 200)

r4 = client.get("/api/experiments/nonexistent_xyz")
check("Experiments", "GET nonexistent 404", r4.status_code == 404)

r5 = client.put(f"/api/experiments/{exp_id}", json={"name": "Updated Name"})
check("Experiments", "PUT update 200", r5.status_code == 200)
check("Experiments", "name updated", r5.json().get("name") == "Updated Name")
client.put(f"/api/experiments/{exp_id}", json={"name": EXP_PAYLOAD["name"]})

r6 = client.post("/api/experiments", json={"name": "bad"})
check("Experiments", "POST missing fields 422", r6.status_code == 422)

# ── 3. PERSONA GENERATION ─────────────────────────────────────────────────────
sec("3. PERSONA GENERATION (Milestone 1)")
r = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 3})
check("Personas", "POST generate 201", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    personas = r.json()["personas"]
    persona_ids = [p["id"] for p in personas]
    check("Personas", "3 personas returned", len(personas) == 3, f"got {len(personas)}")
    for p in personas:
        pname = p.get("name", "?")
        check("Personas", f"{pname}: has experiment_id", p["experiment_id"] == exp_id)
        check("Personas", f"{pname}: age is int", isinstance(p.get("age"), int), f"age={p.get('age')}")
        check("Personas", f"{pname}: has occupation", bool(p.get("occupation")), p.get("occupation", ""))

r2 = client.get(f"/api/experiments/{exp_id}/personas")
check("Personas", "GET personas 200", r2.status_code == 200)
check("Personas", "GET returns 3", len(r2.json()) == 3, f"got {len(r2.json())}")

r3 = client.get(f"/api/personas/{persona_ids[0]}")
check("Personas", "GET by id 200", r3.status_code == 200)

r4 = client.get("/api/personas/nonexistent_p")
check("Personas", "GET nonexistent 404", r4.status_code == 404)

# ── 4. SURVEY (Mode 1) ────────────────────────────────────────────────────────
sec("4. SURVEY SIMULATION (Mode 1) — Milestone 2")
r = client.post(f"/api/experiments/{exp_id}/surveys",
                json={"title": "Live Test Survey", "description": "E2E test"})
check("Survey", "POST create survey 201", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    survey_id = r.json()["id"]
    q1 = client.post(f"/api/surveys/{survey_id}/questions",
                     json={"question_text": "Would you pay 299/month?", "question_type": "yes_no"})
    check("Survey", "add yes_no question 201", q1.status_code == 201)

    q2 = client.post(f"/api/surveys/{survey_id}/questions",
                     json={"question_text": "Rate delivery speed 1-5", "question_type": "rating"})
    check("Survey", "add rating question 201", q2.status_code == 201)

    q3 = client.post(f"/api/surveys/{survey_id}/questions",
                     json={"question_text": "Best feature?", "question_type": "open_ended"})
    check("Survey", "add open_ended question 201", q3.status_code == 201)

    run = client.post(f"/api/surveys/{survey_id}/run")
    check("Survey", "POST run survey 200", run.status_code == 200, f"status={run.status_code}")
    if run.status_code == 200:
        rd = run.json()
        check("Survey", "total_personas=3", rd.get("total_personas") == 3, f"got {rd.get('total_personas')}")
        expected = 9  # 3 personas x 3 questions
        check("Survey", f"total_responses={expected}", rd.get("total_responses_generated") == expected,
              f"got {rd.get('total_responses_generated')}")
        for resp in rd.get("responses", []):
            check("Survey", "response has persona_id", bool(resp.get("persona_id")))
            check("Survey", "response has answer", bool(resp.get("answer")))
            check("Survey", "survey_id matches", resp.get("survey_id") == survey_id)

    gr = client.get(f"/api/surveys/{survey_id}/responses")
    check("Survey", "GET responses 200", gr.status_code == 200)
    check("Survey", "grouped_by_question key", "grouped_by_question" in gr.json())

    run2 = client.post(f"/api/surveys/{survey_id}/run")
    check("Survey", "rerun survey 400 or 200", run2.status_code in (200, 400), f"status={run2.status_code}")

r_es = client.post(f"/api/experiments/{exp_id}/surveys", json={"title": "Empty"})
if r_es.status_code == 201:
    r_re = client.post(f"/api/surveys/{r_es.json()['id']}/run")
    check("Survey", "run empty survey 400", r_re.status_code == 400, f"status={r_re.status_code}")

# ── 5. CONVERSATION (Mode 2) ──────────────────────────────────────────────────
sec("5. CONVERSATION SIMULATION (Mode 2) — Milestone 2")
p_id = persona_ids[0]
r = client.post(f"/api/personas/{p_id}/conversation",
                json={"message": "How do you feel about subscription food delivery apps?"})
check("Conv", "POST conversation 200", r.status_code == 200, f"status={r.status_code}")
if r.status_code == 200:
    d = r.json()
    check("Conv", "response field present", bool(d.get("response")), str(d.get("response", ""))[:60])
    check("Conv", "persona_id matches", d.get("persona_id") == p_id)
    check("Conv", "memory_updated present", "memory_updated" in d)

r2 = client.post(f"/api/personas/{p_id}/conversation",
                 json={"message": "What makes you pay premium for delivery?"})
check("Conv", "second turn 200", r2.status_code == 200)

mem = client.get(f"/api/personas/{p_id}/memory")
check("Conv", "GET memory 200", mem.status_code == 200)
check("Conv", "memory not None", mem.json() is not None)

r3 = client.post(f"/api/personas/{persona_ids[1]}/conversation",
                 json={"message": "Pricing concerns? 299 rupees per month?"})
check("Conv", "second persona conversation 200", r3.status_code == 200)

r4 = client.post("/api/personas/nonexistent_p/conversation", json={"message": "Hello"})
check("Conv", "nonexistent persona 404", r4.status_code == 404)

# ── 6. INSIGHTS ───────────────────────────────────────────────────────────────
sec("6. INSIGHT EXTRACTION — Milestone 3")
r = client.post(f"/api/experiments/{exp_id}/insights")
check("Insights", "POST insights 201", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    ins = r.json()
    check("Insights", "experiment_id matches", ins.get("experiment_id") == exp_id)
    check("Insights", "recurring_themes list", isinstance(ins.get("recurring_themes"), list))
    sd = ins.get("sentiment_distribution", {})
    check("Insights", "positive_percentage in distribution", "positive_percentage" in sd)
    check("Insights", "agreement_patterns list", isinstance(ins.get("agreement_patterns"), list))
    check("Insights", "behavioral_trends list", isinstance(ins.get("behavioral_trends"), list))
    check("Insights", "limitations has 'synthetic'", "synthetic" in ins.get("limitations", "").lower())

r2 = client.get(f"/api/experiments/{exp_id}/insights")
check("Insights", "GET insights 200", r2.status_code == 200)
if r.status_code == 201:
    check("Insights", "GET id matches POST", r2.json().get("id") == r.json().get("id"))

r_ei = client.post("/api/experiments", json={**EXP_PAYLOAD, "name": "Empty insight test"})
if r_ei.status_code == 201:
    r_if = client.post(f"/api/experiments/{r_ei.json()['id']}/insights")
    check("Insights", "empty experiment 400", r_if.status_code in (400, 422), f"status={r_if.status_code}")

# ── 7. USAGE SCORE ────────────────────────────────────────────────────────────
sec("7. USAGE SCORE — Milestone 3")
r = client.post(f"/api/experiments/{exp_id}/usage-score")
check("Score", "POST usage-score 201", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    sc = r.json()
    check("Score", "experiment_id matches", sc.get("experiment_id") == exp_id)
    check("Score", "overall_score 1-10", 1.0 <= sc.get("overall_score", 0) <= 10.0,
          f"score={sc.get('overall_score')}")
    check("Score", "would_use_pct 0-100", 0.0 <= sc.get("would_use_percentage", -1) <= 100.0,
          f"pct={sc.get('would_use_percentage')}")
    check("Score", "persona_scores list", isinstance(sc.get("persona_scores"), list))
    check("Score", "calculation_method present", bool(sc.get("calculation_method")))

# ── 8. DASHBOARD ──────────────────────────────────────────────────────────────
sec("8. DASHBOARD ENDPOINT — Milestone 4")
r = client.get(f"/api/experiments/{exp_id}/dashboard")
check("Dashboard", "GET dashboard 200", r.status_code == 200, f"status={r.status_code}")
if r.status_code == 200:
    dash = r.json()
    cards = dash.get("summary_cards", {})
    check("Dashboard", "total_personas=3", cards.get("total_personas") == 3, f"got {cards.get('total_personas')}")
    check("Dashboard", "total_responses>0", cards.get("total_responses", 0) > 0, f"got {cards.get('total_responses')}")
    check("Dashboard", "survey_responses>0", cards.get("survey_responses", 0) > 0)
    check("Dashboard", "interview_responses>0", cards.get("interview_responses", 0) > 0)
    check("Dashboard", "themes_discovered>0", cards.get("themes_discovered", 0) > 0, f"got {cards.get('themes_discovered')}")
    check("Dashboard", "positive_sentiment_pct not None", cards.get("positive_sentiment_pct") is not None)
    check("Dashboard", "validation_score not None", cards.get("validation_score") is not None,
          f"got {cards.get('validation_score')}")
    check("Dashboard", "status=Analysis Complete",
          cards.get("experiment_status") == "Analysis Complete", f"got {cards.get('experiment_status')}")

    themes = dash.get("theme_clusters", [])
    check("Dashboard", "theme_clusters list", isinstance(themes, list))
    check("Dashboard", "theme_clusters not empty", len(themes) > 0, f"got {len(themes)}")
    for t in themes[:3]:
        check("Dashboard", f"theme '{t.get('theme')}' has description", bool(t.get("description")))
        check("Dashboard", f"theme '{t.get('theme')}' has percentage", t.get("percentage") is not None)

    sb = dash.get("sentiment_breakdown", {})
    check("Dashboard", "pos/neu/neg keys", all(k in sb for k in ["positive", "neutral", "negative"]))
    total_pct = (sb.get("positive", {}).get("percentage", 0) +
                 sb.get("neutral", {}).get("percentage", 0) +
                 sb.get("negative", {}).get("percentage", 0))
    check("Dashboard", "sentiment pcts sum ~100", abs(total_pct - 100.0) <= 1.0 or total_pct == 0.0,
          f"sum={total_pct:.1f}")

    quotes = dash.get("key_quotes", [])
    check("Dashboard", "key_quotes not empty", len(quotes) > 0, f"got {len(quotes)}")
    for q in quotes[:3]:
        check("Dashboard", "quote has quote field", bool(q.get("quote")))
        check("Dashboard", "quote has persona_name", bool(q.get("persona_name")))

    val = dash.get("validation_score", {})
    check("Dashboard", "validation_score.available=True", val.get("available") is True)
    if val.get("available"):
        vs = val.get("score", -1)
        check("Dashboard", "val score 0-100", 0 <= vs <= 100, f"score={vs}")
        wup = val.get("would_use_percentage", -1)
        check("Dashboard", "would_use_pct 0-100", 0 <= wup <= 100, f"pct={wup}")

    check("Dashboard", "has_insight_report=True", dash.get("has_insight_report") is True)
    check("Dashboard", "has_usage_score=True", dash.get("has_usage_score") is True)
    check("Dashboard", "experiment.id matches", dash.get("experiment", {}).get("id") == exp_id)
    print(f"  Dashboard keys: {list(dash.keys())}")

r2 = client.get("/api/experiments/nonexistent_xyz/dashboard")
check("Dashboard", "nonexistent 404", r2.status_code == 404)

r3 = client.post("/api/experiments", json={**EXP_PAYLOAD, "name": "Empty Dash Test"})
if r3.status_code == 201:
    de = client.get(f"/api/experiments/{r3.json()['id']}/dashboard").json()
    check("Dashboard", "empty: total_personas=0", de["summary_cards"]["total_personas"] == 0)
    check("Dashboard", "empty: status=Not Started", de["summary_cards"]["experiment_status"] == "Not Started")
    check("Dashboard", "empty: theme_clusters=[]", de["theme_clusters"] == [])
    check("Dashboard", "empty: has_insight_report=False", de["has_insight_report"] is False)

# ── 9. PDF ────────────────────────────────────────────────────────────────────
sec("9. PDF REPORT DOWNLOAD — Milestone 4")
r = client.get(f"/api/experiments/{exp_id}/report/pdf")
check("PDF", "GET pdf 200", r.status_code == 200, f"status={r.status_code}")
check("PDF", "content-type=application/pdf",
      r.headers.get("content-type") == "application/pdf", r.headers.get("content-type"))
check("PDF", "magic bytes %PDF-", r.content[:5] == b"%PDF-", repr(r.content[:5]))
check("PDF", "size>5KB", len(r.content) > 5000, f"{len(r.content)} bytes")
fname = r.headers.get("content-disposition", "")
check("PDF", "filename has exp_id", f"research_report_{exp_id}.pdf" in fname, fname[:80])
if r.status_code == 200:
    pdf_path = f"d:/Milestone2/backend/tests/live_report_{exp_id}.pdf"
    with open(pdf_path, "wb") as fh:
        fh.write(r.content)
    print(f"  PDF saved: {pdf_path} ({len(r.content):,} bytes)")

r2 = client.get("/api/experiments/nonexistent_xyz/report/pdf")
check("PDF", "nonexistent 404", r2.status_code == 404)

r3 = client.post("/api/experiments", json={**EXP_PAYLOAD, "name": "No Personas PDF"})
if r3.status_code == 201:
    r_pe = client.get(f"/api/experiments/{r3.json()['id']}/report/pdf")
    check("PDF", "no personas 400", r_pe.status_code == 400, f"status={r_pe.status_code}")
    body = r_pe.json()
    err = (body.get("detail") or body.get("error") or "").lower()
    check("PDF", "400 mentions 'persona' or 'no'", "no" in err or "persona" in err, err[:80])

for i in range(3):
    rr = client.get(f"/api/experiments/{exp_id}/report/pdf")
    check("PDF", f"repeated download #{i+1} valid PDF",
          rr.status_code == 200 and rr.content[:5] == b"%PDF-")

# ── 10. CONSISTENCY ───────────────────────────────────────────────────────────
sec("10. DATA CONSISTENCY — Dashboard vs PDF")
dash2 = client.get(f"/api/experiments/{exp_id}/dashboard").json()
check("Consistency", "dashboard total_personas=3",
      dash2["summary_cards"]["total_personas"] == 3,
      f"got {dash2['summary_cards']['total_personas']}")
check("Consistency", "dashboard total_responses>0",
      dash2["summary_cards"]["total_responses"] > 0,
      f"got {dash2['summary_cards']['total_responses']}")

# ── 11. ANALYTICS ─────────────────────────────────────────────────────────────
sec("11. ANALYTICS ENDPOINT")
r = client.get("/api/analytics/overview")
check("Analytics", "GET overview 200", r.status_code == 200, f"status={r.status_code}")

# ── 12. EXPERIMENT ISOLATION ──────────────────────────────────────────────────
sec("12. SECURITY — EXPERIMENT ISOLATION")
r_exp2 = client.post("/api/experiments", json={**EXP_PAYLOAD, "name": "Isolation Exp 2"})
if r_exp2.status_code == 201:
    exp2_id = r_exp2.json()["id"]
    d1 = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    d2 = client.get(f"/api/experiments/{exp2_id}/dashboard").json()
    n1 = d1["summary_cards"]["total_personas"]
    n2 = d2["summary_cards"]["total_personas"]
    check("Security", "exp1=3 personas, exp2=0", n1 == 3 and n2 == 0, f"exp1={n1}, exp2={n2}")

# ── 13. CLEANUP ───────────────────────────────────────────────────────────────
sec("13. CLEANUP")
r_del = client.delete(f"/api/experiments/{exp_id}")
check("Cleanup", "DELETE experiment 200", r_del.status_code == 200)
r_gd = client.get(f"/api/experiments/{exp_id}")
check("Cleanup", "GET after delete 404", r_gd.status_code == 404)

# ── RESULTS ───────────────────────────────────────────────────────────────────
passed = [x for x in results if x["status"] == "PASS"]
failed = [x for x in results if x["status"] == "FAIL"]

print(f"\n{'='*60}")
print("  LIVE API TEST RESULTS")
print(f"{'='*60}")
print(f"  PASSED : {len(passed)}")
print(f"  FAILED : {len(failed)}")
print(f"  TOTAL  : {len(results)}")
if failed:
    print(f"\n  FAILURES:")
    for f in failed:
        print(f"    [{f['section']}] {f['test']}")
        if f["detail"]:
            print(f"      detail: {f['detail'][:100]}")
print(f"{'='*60}")
sys.exit(0 if not failed else 1)
