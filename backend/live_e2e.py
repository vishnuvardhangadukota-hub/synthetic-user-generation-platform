import httpx, sys
BASE = 'http://127.0.0.1:8000'
results = []

def check(label, condition, detail=''):
    status = 'PASS' if condition else 'FAIL'
    results.append((label, status, str(detail)))
    icon = 'OK' if condition else 'FAIL'
    print(f'  [{icon}] {label}: {detail}')
    return condition

# 1. Health
r = httpx.get(BASE + '/')
check('Root 200', r.status_code == 200, r.status_code)
data = r.json()
check('status=online', data.get('status') == 'online', data.get('status'))
check('/docs 200', httpx.get(BASE + '/docs').status_code == 200)

# 2. Create experiment
EXP = {
    'name': 'Live E2E Test',
    'product_name': 'QuickBite Pro',
    'product_description': 'Food delivery app for professionals',
    'target_audience': 'Professionals aged 25-40',
    'research_objectives': ['Price sensitivity', 'Speed expectations'],
    'number_of_personas': 3,
}
r = httpx.post(BASE + '/api/experiments', json=EXP, timeout=30)
check('Create exp 201', r.status_code == 201, r.status_code)
exp_id = r.json().get('id', '')
check('Exp has ID', bool(exp_id), exp_id)

r = httpx.get(BASE + '/api/experiments')
check('GET all exps 200', r.status_code == 200, len(r.json()))
r = httpx.get(BASE + f'/api/experiments/{exp_id}')
check('GET single exp 200', r.status_code == 200, r.status_code)
r = httpx.put(BASE + f'/api/experiments/{exp_id}', json={'name': 'Updated Name'}, timeout=10)
check('PUT exp 200', r.status_code == 200, r.json().get('name'))
r = httpx.get(BASE + '/api/experiments/invalid_id_xyz')
check('GET invalid exp 404', r.status_code == 404, r.status_code)

# 3. Persona generation
r = httpx.post(BASE + f'/api/experiments/{exp_id}/personas/generate', json={'number_of_personas': 3}, timeout=60)
check('Gen personas 201', r.status_code == 201, r.status_code)
personas = r.json().get('personas', [])
check('3 personas generated', len(personas) == 3, len(personas))
p_id = personas[0]['id'] if personas else ''
if personas:
    p = personas[0]
    check('Persona has name', bool(p.get('name')), p.get('name'))
    check('Persona age is int', isinstance(p.get('age'), int), p.get('age'))
    check('Persona has occupation', bool(p.get('occupation')), p.get('occupation'))

r = httpx.get(BASE + f'/api/experiments/{exp_id}/personas')
check('GET personas 200', r.status_code == 200, len(r.json()))

# 4. Survey (Mode 1)
r = httpx.post(BASE + f'/api/experiments/{exp_id}/surveys', json={'title': 'Test Survey', 'description': 'E2E'}, timeout=10)
check('Create survey 201', r.status_code == 201, r.status_code)
s_id = r.json().get('id', '')

r = httpx.post(BASE + f'/api/surveys/{s_id}/questions', json={'question_text': 'Would you pay?', 'question_type': 'yes_no'}, timeout=10)
check('Add yes_no question 201', r.status_code == 201, r.status_code)
r = httpx.post(BASE + f'/api/surveys/{s_id}/questions', json={'question_text': 'Rate 1-5', 'question_type': 'rating'}, timeout=10)
check('Add rating question 201', r.status_code == 201, r.status_code)

r = httpx.post(BASE + f'/api/surveys/{s_id}/run', timeout=120)
check('Run survey 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    rd = r.json()
    check('Survey responses > 0', rd.get('total_responses_generated', 0) > 0, rd.get('total_responses_generated'))

r = httpx.get(BASE + f'/api/surveys/{s_id}/responses', timeout=10)
check('GET survey responses 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    check('Has grouped_by_question', 'grouped_by_question' in r.json(), list(r.json().keys()))

# 5. Conversation (Mode 2)
r = httpx.post(BASE + f'/api/personas/{p_id}/conversation', json={'message': 'Tell me about food delivery apps'}, timeout=60)
check('Conversation 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    cd = r.json()
    check('Conversation has response', bool(cd.get('response')), cd.get('response', '')[:60])
    check('memory_updated present', 'memory_updated' in cd, cd.get('memory_updated'))

r = httpx.get(BASE + f'/api/personas/{p_id}/memory', timeout=10)
check('GET persona memory 200', r.status_code == 200, r.status_code)

# 6. Insights
r = httpx.post(BASE + f'/api/experiments/{exp_id}/insights', timeout=120)
check('Extract insights 201', r.status_code == 201, r.status_code)
if r.status_code == 201:
    idata = r.json()
    check('Has recurring_themes list', isinstance(idata.get('recurring_themes'), list), len(idata.get('recurring_themes', [])))
    check('Has sentiment_distribution', 'positive_percentage' in idata.get('sentiment_distribution', {}))
    check('Has limitations with synthetic', 'synthetic' in idata.get('limitations', '').lower(), idata.get('limitations', '')[:60])

r = httpx.get(BASE + f'/api/experiments/{exp_id}/insights', timeout=10)
check('GET insights 200', r.status_code == 200, r.status_code)

# 7. Usage score
r = httpx.post(BASE + f'/api/experiments/{exp_id}/usage-score', timeout=60)
check('Usage score 201', r.status_code == 201, r.status_code)
if r.status_code == 201:
    sd = r.json()
    check('Score in 1-10', 1.0 <= sd.get('overall_score', 0) <= 10.0, sd.get('overall_score'))
    check('Pct in 0-100', 0 <= sd.get('would_use_percentage', -1) <= 100, sd.get('would_use_percentage'))

r = httpx.get(BASE + f'/api/experiments/{exp_id}/usage-score', timeout=10)
check('GET usage score 200', r.status_code == 200, r.status_code)

# 8. Dashboard
r = httpx.get(BASE + f'/api/experiments/{exp_id}/dashboard', timeout=30)
check('Dashboard 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    dash = r.json()
    cards = dash.get('summary_cards', {})
    check('Personas=3', cards.get('total_personas') == 3, cards.get('total_personas'))
    check('Responses>0', cards.get('total_responses', 0) > 0, cards.get('total_responses'))
    check('has_insight_report=True', dash.get('has_insight_report') is True, dash.get('has_insight_report'))
    check('has_usage_score=True', dash.get('has_usage_score') is True, dash.get('has_usage_score'))
    check('theme_clusters is list', isinstance(dash.get('theme_clusters'), list), len(dash.get('theme_clusters', [])))
    sb = dash.get('sentiment_breakdown', {})
    if sb:
        total = sb.get('positive',{}).get('percentage',0)+sb.get('neutral',{}).get('percentage',0)+sb.get('negative',{}).get('percentage',0)
        check('Sentiment sums ~100', abs(total-100.0)<=1.0 or total==0, f'sum={total}')
    val = dash.get('validation_score', {})
    if val.get('available'):
        check('Val score 0-100', 0 <= val.get('score',-1) <= 100, val.get('score'))

r = httpx.get(BASE + '/api/experiments/nope/dashboard', timeout=10)
check('Dashboard 404', r.status_code == 404, r.status_code)

# 9. PDF
r = httpx.get(BASE + f'/api/experiments/{exp_id}/report/pdf', timeout=60)
check('PDF 200', r.status_code == 200, r.status_code)
if r.status_code == 200:
    check('PDF content-type', r.headers.get('content-type') == 'application/pdf', r.headers.get('content-type'))
    check('PDF has filename', f'research_report_{exp_id}.pdf' in r.headers.get('content-disposition',''), r.headers.get('content-disposition','')[:80])
    check('PDF magic bytes', r.content[:5] == b'%PDF-', r.content[:10])
    check('PDF size>5000', len(r.content) > 5000, len(r.content))

r = httpx.get(BASE + '/api/experiments/nope/report/pdf', timeout=10)
check('PDF 404 invalid', r.status_code == 404, r.status_code)

r2 = httpx.post(BASE + '/api/experiments', json={**EXP, 'name':'Empty'}, timeout=10)
eid2 = r2.json().get('id','')
r3 = httpx.get(BASE + f'/api/experiments/{eid2}/report/pdf', timeout=10)
check('PDF 400 no data', r3.status_code == 400, r3.status_code)

# 10. Error handling
r = httpx.post(BASE + '/api/experiments', json={}, timeout=10)
check('Empty body 422', r.status_code == 422, r.status_code)
r = httpx.get(BASE + '/api/experiments/nope/personas', timeout=10)
check('Invalid exp personas 404', r.status_code == 404, r.status_code)

# Summary
passed = sum(1 for _,s,_ in results if s=='PASS')
failed = sum(1 for _,s,_ in results if s=='FAIL')
print(f'\n=== FINAL: {len(results)} tests | {passed} PASSED | {failed} FAILED ===')
for label,status,detail in results:
    if status == 'FAIL':
        print(f'  FAIL: {label} - {detail}')
sys.exit(0 if failed==0 else 1)
