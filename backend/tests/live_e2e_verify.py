"""
Live E2E verification script — runs against the running server at localhost:8000.
Not a pytest test; execute directly with: python tests/live_e2e_verify.py
"""
import httpx, sys, os

BASE = "http://localhost:8000"

def main():
    client = httpx.Client(base_url=BASE, timeout=30.0)
    ok = 0
    fail = 0

    def check(name, condition, detail=""):
        nonlocal ok, fail
        if condition:
            ok += 1
            print(f"  ✅ {name}")
        else:
            fail += 1
            print(f"  ❌ {name}  {detail}")

    print("\n═══ Live E2E Verification ═══\n")

    # 1. Create experiment
    print("─── Step 1: Create Experiment ───")
    exp = client.post("/api/experiments", json={
        "name": "Live E2E Test",
        "product_name": "QuickBite",
        "product_description": "Fast food delivery app",
        "target_audience": "Young professionals in Hyderabad",
        "research_objectives": ["Understand pricing sensitivity", "Evaluate feature demand"],
        "number_of_personas": 3,
    }).json()
    exp_id = exp.get("id", "")
    check("Experiment created", bool(exp_id), f"id={exp_id}")

    # 2. Generate personas
    print("─── Step 2: Generate Personas ───")
    gen = client.post(f"/api/experiments/{exp_id}/personas/generate", json={"number_of_personas": 3}).json()
    personas = gen.get("personas", [])
    check("Personas generated", len(personas) == 3, f"got {len(personas)}")

    # 3. Survey simulation
    print("─── Step 3: Survey Simulation ───")
    srv = client.post(f"/api/experiments/{exp_id}/surveys", json={"title": "Live Test Survey"}).json()
    s_id = srv.get("id", "")
    check("Survey created", bool(s_id))
    client.post(f"/api/surveys/{s_id}/questions", json={
        "question_text": "Would you pay ₹299/month for premium delivery?",
        "question_type": "yes_no",
    })
    client.post(f"/api/surveys/{s_id}/questions", json={
        "question_text": "Rate delivery speed importance (1-5)",
        "question_type": "rating",
    })
    run = client.post(f"/api/surveys/{s_id}/run").json()
    n_resp = run.get("total_responses_generated", 0)
    check("Survey responses generated", n_resp == 6, f"got {n_resp}")

    # 4. Conversation (interview simulation)
    print("─── Step 4: Interview Simulation ───")
    p_id = personas[0]["id"]
    conv = client.post(f"/api/personas/{p_id}/conversation", json={
        "message": "What would make you switch to a competing delivery app?",
    }).json()
    check("Conversation response", bool(conv.get("response")))

    # 5. Insight extraction
    print("─── Step 5: Insight Extraction ───")
    ins = client.post(f"/api/experiments/{exp_id}/insights").json()
    check("Insights generated", bool(ins.get("recurring_themes")))
    check("Sentiment distribution", "positive_percentage" in ins.get("sentiment_distribution", {}))

    # 6. Usage score
    print("─── Step 6: Usage Score ───")
    score = client.post(f"/api/experiments/{exp_id}/usage-score").json()
    check("Usage score computed", score.get("overall_score") is not None)

    # 7. Dashboard
    print("─── Step 7: Dashboard ───")
    dash = client.get(f"/api/experiments/{exp_id}/dashboard").json()
    cards = dash.get("summary_cards", {})
    check("Total personas on dashboard", cards.get("total_personas") == 3)
    check("Total responses on dashboard", cards.get("total_responses", 0) > 0)
    check("Themes discovered", cards.get("themes_discovered", 0) > 0)
    check("Positive sentiment %", cards.get("positive_sentiment_pct") is not None)
    check("Validation score", cards.get("validation_score") is not None)
    check("Theme clusters populated", len(dash.get("theme_clusters", [])) > 0)
    check("Sentiment breakdown", dash.get("sentiment_breakdown", {}).get("total", 0) > 0)
    check("Key quotes present", len(dash.get("key_quotes", [])) > 0)
    check("Has insight report", dash.get("has_insight_report") is True)
    check("Has usage score", dash.get("has_usage_score") is True)

    # 8. PDF report
    print("─── Step 8: PDF Report Download ───")
    pdf_resp = client.get(f"/api/experiments/{exp_id}/report/pdf")
    check("PDF status 200", pdf_resp.status_code == 200)
    check("PDF content-type", pdf_resp.headers.get("content-type") == "application/pdf")
    check("PDF magic bytes", pdf_resp.content[:5] == b"%PDF-")
    check("PDF file size > 5KB", len(pdf_resp.content) > 5000, f"size={len(pdf_resp.content)}")
    fname = pdf_resp.headers.get("content-disposition", "")
    check("PDF filename correct", f"research_report_{exp_id}.pdf" in fname)

    # Save PDF for manual inspection
    pdf_path = os.path.join(os.path.dirname(__file__), f"live_report_{exp_id}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_resp.content)
    print(f"\n  📄 PDF saved to: {pdf_path}")

    # 9. Error handling
    print("─── Step 9: Error Handling ───")
    r404 = client.get("/api/experiments/nonexistent_xyz/dashboard")
    check("Dashboard 404 for missing exp", r404.status_code == 404)
    r404_pdf = client.get("/api/experiments/nonexistent_xyz/report/pdf")
    check("PDF 404 for missing exp", r404_pdf.status_code == 404)

    # 10. Cleanup
    print("─── Step 10: Cleanup ───")
    del_res = client.delete(f"/api/experiments/{exp_id}")
    check("Experiment deleted", del_res.status_code == 200)

    print(f"\n═══ Results: {ok} passed, {fail} failed ═══\n")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
