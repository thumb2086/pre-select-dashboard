import os, json, csv, re
from collections import defaultdict

DATA_DIR = r'C:\Users\CPXru\Desktop\thumb\program\分析'
OUT_DIR = os.path.join(DATA_DIR, 'dashboard', 'data')

def load_scores():
    scores = {}
    for f in os.listdir(DATA_DIR):
        m = re.match(r'scores_(\d+)\.csv', f)
        if not m: continue
        depid = m.group(1)
        with open(os.path.join(DATA_DIR, f), encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = []
            for r in reader:
                rows.append({
                    'examId': r['准考證號'],
                    'chinese': int(r['國文']),
                    'english': int(r['英文']),
                    'math': int(r['數學']),
                    'pro1': int(r['專一']),
                    'pro2': int(r['專二']),
                    'total': int(r['總分']),
                })
            if rows:
                scores[depid] = rows
    return scores

def load_departments():
    path = os.path.join(DATA_DIR, 'data.csv')
    depts = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            depts[r['校系名稱']] = {
                'name': r['校系名稱'],
                'date': r.get('甄試日期', ''),
                'quota': int(r['招生名額']) if r['招生名額'] else 0,
                'selected': r.get('預選人數', ''),
                'max_choices': int(r['可選填校系數']) if r.get('可選填校系數') else 0,
            }
    return depts

def analyze(scores, depts):
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Score distribution per department
    dist = {}
    for depid, rows in scores.items():
        totals = [s['total'] for s in rows]
        dist[depid] = {
            'min': min(totals),
            'max': max(totals),
            'avg': round(sum(totals) / len(totals), 1),
            'median': sorted(totals)[len(totals)//2],
            'count': len(totals),
            'totals': totals,
            'students': rows,
        }
    with open(os.path.join(OUT_DIR, 'score_distribution.json'), 'w', encoding='utf-8') as f:
        json.dump(dist, f, ensure_ascii=False)

    # 2. Competition intensity
    competition = []
    for depid, rows in scores.items():
        name = None
        for n, d in depts.items():
            if n.startswith(depid):
                name = n
                break
        quota = depts[name]['quota'] if name and name in depts else 0
        ratio = round(len(rows) / quota, 2) if quota > 0 else 0
        competition.append({
            'depid': depid,
            'name': name or depid,
            'quota': quota,
            'applicants': len(rows),
            'ratio': ratio,
        })
    competition.sort(key=lambda x: -x['ratio'])
    with open(os.path.join(OUT_DIR, 'competition.json'), 'w', encoding='utf-8') as f:
        json.dump(competition, f, ensure_ascii=False)

    # 3. Date conflict analysis
    date_groups = defaultdict(list)
    for depid, rows in scores.items():
        name = None
        for n, d in depts.items():
            if n.startswith(depid):
                name = n
                break
        date = depts[name]['date'] if name and name in depts else ''
        if date:
            date_groups[date].append({'depid': depid, 'name': name or depid, 'count': len(rows)})
    date_conflicts = {k: v for k, v in sorted(date_groups.items())}
    with open(os.path.join(OUT_DIR, 'date_conflicts.json'), 'w', encoding='utf-8') as f:
        json.dump(date_conflicts, f, ensure_ascii=False)

    # 4. Per-student ranking across all departments
    student_depts = defaultdict(list)
    for depid, rows in scores.items():
        sorted_rows = sorted(rows, key=lambda x: -x['total'])
        for rank, s in enumerate(sorted_rows, 1):
            student_depts[s['examId']].append({
                'depid': depid,
                'total': s['total'],
                'rank': rank,
                'count': len(rows),
            })
    for sid in student_depts:
        student_depts[sid].sort(key=lambda x: -x['total'])
    with open(os.path.join(OUT_DIR, 'student_rankings.json'), 'w', encoding='utf-8') as f:
        json.dump(student_depts, f, ensure_ascii=False)

    # 5. Department name mapping
    dept_names = {}
    for depid in scores:
        for n in depts:
            if n.startswith(depid):
                dept_names[depid] = n
                break
        if depid not in dept_names:
            dept_names[depid] = depid
    with open(os.path.join(OUT_DIR, 'dept_names.json'), 'w', encoding='utf-8') as f:
        json.dump(dept_names, f, ensure_ascii=False)

    # Summary
    summary = {
        'total_departments': len(scores),
        'total_students': sum(len(v) for v in scores.values()),
        'unique_students': len(student_depts),
        'dates_with_conflicts': len(date_groups),
    }
    with open(os.path.join(OUT_DIR, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False)

    print(f'分析完成！')
    print(f'  校系: {summary["total_departments"]}')
    print(f'  成績總筆數: {summary["total_students"]}')
    print(f'  不重複考生: {summary["unique_students"]}')
    print(f'  有面試日期衝突的日期數: {summary["dates_with_conflicts"]}')
    print(f'  競爭最激烈 TOP5:')
    for c in competition[:5]:
        print(f'    {c["name"]}: {c["applicants"]}人搶{c["quota"]}個名額 (比值{c["ratio"]})')

if __name__ == '__main__':
    scores = load_scores()
    depts = load_departments()
    analyze(scores, depts)
