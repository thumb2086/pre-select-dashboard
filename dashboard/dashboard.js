let data = {};
let histChart = null, compChart = null;

async function loadData() {
  const [dist, comp, dates, students, deptNames, summary, deptDetails] = await Promise.all([
    fetch('data/score_distribution.json').then(r=>r.json()),
    fetch('data/competition.json').then(r=>r.json()),
    fetch('data/date_conflicts.json').then(r=>r.json()),
    fetch('data/student_rankings.json').then(r=>r.json()),
    fetch('data/dept_names.json').then(r=>r.json()),
    fetch('data/summary.json').then(r=>r.json()),
    fetch('data/dept_details.json').then(r=>r.json()),
  ]);
  data = { dist, comp, dates, students, deptNames, summary, deptDetails };
  renderOverview();
  renderDeptSelect();
  renderStudentSelect();
  renderDetailSelect();
  renderCompetition();
  renderDates();
}

function showTab(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  document.querySelector('.nav a[onclick*="' + name + '"]').classList.add('active');
  if (name === 'distribution' && document.getElementById('deptSelect').value) updateDistribution();
}

function renderOverview() {
  const s = data.summary;
  document.getElementById('stats').innerHTML =
    '<div class="stat-card"><div class="num">' + s.total_departments + '</div><div class="label">校系總數</div></div>' +
    '<div class="stat-card"><div class="num">' + s.total_students + '</div><div class="label">成績總筆數</div></div>' +
    '<div class="stat-card"><div class="num">' + s.unique_students + '</div><div class="label">不重複考生</div></div>' +
    '<div class="stat-card"><div class="num">' + s.dates_with_conflicts + '</div><div class="label">面試日期數</div></div>';
  const ctx = document.getElementById('chartQuota').getContext('2d');
  const sorted = [...data.comp].sort((a,b) => b.applicants - a.applicants).slice(0, 30);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sorted.map(d => d.name.replace(/^\d+/, '')),
      datasets: [
        { label: '預選人數', data: sorted.map(d => d.applicants), backgroundColor: '#1a73e8' },
        { label: '招生名額', data: sorted.map(d => d.quota), backgroundColor: '#e8a01a' },
      ]
    },
    options: { responsive: true, indexAxis: 'y', plugins: { legend: { position: 'top' } },
      scales: { x: { beginAtZero: true, ticks: { stepSize: 10 } } } }
  });
}

function renderDeptSelect() {
  const sel = document.getElementById('deptSelect');
  const names = data.deptNames;
  sel.innerHTML = Object.keys(names).sort().map(function(id) {
    return '<option value="' + id + '">' + names[id] + '</option>';
  }).join('');
}

function renderStudentSelect() {
  const sel = document.getElementById('studentSelect');
  const ids = Object.keys(data.students).sort(function(a,b) {
    return parseInt(a) - parseInt(b);
  });
  sel.innerHTML = '<option value="">— 選擇准考證號碼 —</option>' +
    ids.map(function(id) { return '<option value="' + id + '">' + id + '</option>'; }).join('');
}

function renderDetailSelect() {
  const sel = document.getElementById('detailDeptSelect');
  const names = data.deptNames;
  sel.innerHTML = Object.keys(names).sort().map(function(id) {
    return '<option value="' + id + '">' + names[id] + '</option>';
  }).join('');
}

function updateDetail() {
  const id = document.getElementById('detailDeptSelect').value;
  const d = data.deptDetails[id];
  if (!d) { document.getElementById('detailContent').innerHTML = ''; return; }
  const sbj = ['國文','英文','數學','專一','專二'];
  const keys = ['chinese','english','math','pro1','pro2'];
  let html = '<div class="chart-row">';
  html += '<div class="chart-box"><h3>篩選倍率</h3>';
  html += '<table class="detail-table"><thead><tr><th>科目</th><th>篩選倍率</th><th>加權倍數</th></tr></thead><tbody>';
  for (let i = 0; i < 5; i++) {
    const fr = d.filter_ratios[keys[i]] || '--';
    const w = d.weight_multipliers[keys[i]] || '--';
    html += '<tr><td>' + sbj[i] + '</td><td><strong>' + fr + '</strong></td><td>' + w + '</td></tr>';
  }
  html += '</tbody></table></div>';
  html += '<div class="chart-box"><h3>基本資訊</h3>';
  html += '<table class="detail-table"><tbody>' +
    '<tr><td style="width:40%;color:#666;">學校</td><td><strong>' + d.college_name + '</strong></td></tr>' +
    '<tr><td style="width:40%;color:#666;">科系</td><td><strong>' + d.name + '</strong></td></tr>' +
    '<tr><td style="color:#666;">群類別</td><td>' + (d.category_code || '--') + '</td></tr>' +
    '<tr><td style="color:#666;">招生名額</td><td>' + d.quota_general + '人</td></tr>' +
    '<tr><td style="color:#666;">預計甄試</td><td>' + d.expected_interviews + '人</td></tr>' +
    '<tr><td style="color:#666;">統測占比</td><td>' + d.tcte_score_rate + '%</td></tr>' +
    '<tr><td style="color:#666;">甄試費</td><td>' + d.interview_fee + '元</td></tr>' +
    '<tr><td style="color:#666;">甄試日期</td><td>' + (d.interview_date || '--') + '</td></tr>' +
    '</tbody></table></div>';
  html += '</div><div class="chart-row">';
  html += '<div class="chart-box full"><h3>第二階段指定項目</h3>';
  if (d.assign_items.length === 0) {
    html += '<p style="color:#999;padding:8px;">無指定項目</p>';
  } else {
    html += '<table class="detail-table"><thead><tr><th style="width:50px;">項次</th><th>名稱</th><th style="width:80px;">最低得分</th><th style="width:100px;">占比</th></tr></thead><tbody>';
    d.assign_items.forEach(function(a, i) {
      html += '<tr><td>' + (i+1) + '</td><td>' + a.name + '</td><td>' + (a.min_score || '--') + '</td><td>' + a.rate + '</td></tr>';
    });
    html += '</tbody></table>';
  }
  html += '</div>';
  html += '</div><div class="chart-row">';
  html += '<div class="chart-box"><h3>學習歷程上傳限制</h3>';
  html += '<table class="detail-table"><thead><tr><th>項目</th><th>件數</th></tr></thead><tbody>' +
    '<tr><td>A.修課紀錄</td><td>' + d.upload_limits.A + '</td></tr>' +
    '<tr><td>B-1.專題實作</td><td>' + d.upload_limits.B1 + '</td></tr>' +
    '<tr><td>B-2.其他學習成果</td><td>' + d.upload_limits.B2 + '</td></tr>' +
    '<tr><td>C.多元表現</td><td>' + d.upload_limits.C + '</td></tr>' +
    '<tr><td>D-1.綜整心得</td><td>' + d.upload_limits.D1 + '</td></tr>' +
    '<tr><td>D-2.學習歷程自述</td><td>' + d.upload_limits.D2 + '</td></tr>' +
    '<tr><td>D-3.其他有利審查</td><td>' + d.upload_limits.D3 + '</td></tr>' +
    '</tbody></table></div>';
  html += '<div class="chart-box"><h3>同分參酌順序</h3>';
  if (d.ref_order && d.ref_order.length > 0) {
    html += '<ol style="padding-left:20px;margin:8px 0;font-size:13px;">';
    d.ref_order.forEach(function(r) {
      if (r && r !== '--') html += '<li style="padding:2px 0;">' + r + '</li>';
    });
    html += '</ol>';
  } else {
    html += '<p style="color:#999;padding:8px;">--</p>';
  }
  html += '</div>';
  html += '</div>';
  if (d.notes) {
    html += '<div class="chart-box full"><h3>備註</h3><p style="font-size:12px;line-height:1.6;white-space:pre-wrap;">' + d.notes + '</p></div>';
  }
  document.getElementById('detailContent').innerHTML = html;
}

function updateDistribution() {
  const id = document.getElementById('deptSelect').value;
  const d = data.dist[id];
  if (!d) return;
  document.getElementById('deptStats').innerHTML =
    '<div class="stat-card"><div class="num">' + d.count + '</div><div class="label">預選人數</div></div>' +
    '<div class="stat-card"><div class="num">' + d.min + '</div><div class="label">最低總分</div></div>' +
    '<div class="stat-card"><div class="num">' + d.max + '</div><div class="label">最高總分</div></div>' +
    '<div class="stat-card"><div class="num">' + d.avg + '</div><div class="label">平均總分</div></div>';
  const totals = d.totals;
  const min = Math.min(...totals), max = Math.max(...totals);
  const binSize = Math.max(1, Math.floor((max - min) / 10));
  const bins = {};
  for (let i = min; i <= max; i += binSize) {
    bins[i + '-' + (i+binSize-1)] = 0;
  }
  totals.forEach(function(t) {
    const idx = Math.floor((t - min) / binSize) * binSize + min;
    const key = idx + '-' + (idx + binSize - 1);
    if (bins[key] !== undefined) bins[key]++;
  });
  if (histChart) histChart.destroy();
  histChart = new Chart(document.getElementById('chartHistogram'), {
    type: 'bar',
    data: {
      labels: Object.keys(bins),
      datasets: [{ label: '人數', data: Object.values(bins), backgroundColor: '#1a73e8' }]
    },
    options: { responsive: true, plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
  });
}

function renderCompetition() {
  const top = data.comp.slice(0, 30);
  const ctx = document.getElementById('chartCompetition').getContext('2d');
  compChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top.map(d => d.name.replace(/^\d+/, '')),
      datasets: [{ label: '競爭比 (預選人數/名額)', data: top.map(d => d.ratio), backgroundColor: top.map(function(d) {
        return d.ratio > 3 ? '#d32f2f' : d.ratio > 1.5 ? '#e65100' : '#2e7d32';
      }) }]
    },
    options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true } } }
  });
  const tbody = document.querySelector('#compTable tbody');
  tbody.innerHTML = data.comp.map(function(d, i) {
    const badge = d.ratio > 3 ? 'badge-red' : d.ratio > 1.5 ? 'badge-orange' : 'badge-green';
    return '<tr><td>' + (i+1) + '</td><td>' + d.name + '</td><td>' + d.quota + '</td><td>' + d.applicants + '</td><td><span class="badge ' + badge + '">' + d.ratio + 'x</span></td></tr>';
  }).join('');
}

function renderDates() {
  const dates = data.dates;
  let html = '<h3>面試日期衝突分析</h3>';
  for (const [date, depts] of Object.entries(dates)) {
    html += '<div class="stat-card" style="margin:12px 0;text-align:left;padding:16px;">' +
      '<strong style="font-size:16px;color:#1a73e8;">' + date + '</strong> — ' + depts.length + ' 個校系<br><br>';
    depts.forEach(function(d) {
      html += '<span class="badge badge-orange" style="margin:2px;font-size:12px;">' + d.name.replace(/^\d+/,'') + ' (' + d.count + '人)</span> ';
    });
    html += '</div>';
  }
  document.getElementById('dateContent').innerHTML = html;
}

function searchStudent() {
  const q = document.getElementById('studentSelect').value;
  const div = document.getElementById('studentResult');
  if (!q) { div.innerHTML = ''; return; }
  const st = data.students[q];
  if (!st) { div.innerHTML = '<p style="color:#999;">查無此准考證號</p>'; return; }
  const quotaMap = {};
  data.comp.forEach(function(c) { quotaMap[c.depid] = c.quota; });
  let html = '<div class="stat-card" style="text-align:left;padding:16px;"><strong>准考證號：' + q + '</strong> — 報名 ' + st.length + ' 個校系</div>' +
    '<div style="overflow-x:auto;"><table><thead><tr><th>校系</th><th>總分</th><th>大安排名</th><th>大安人數</th><th>全國招生名額</th><th>大安占比</th></tr></thead><tbody>';
  st.forEach(function(s) {
    const pct = Math.round(s.rank / s.count * 100);
    const quota = quotaMap[s.depid] || 0;
    html += '<tr><td>' + (data.deptNames[s.depid] || s.depid).replace(/^\d+/,'') + '</td>' +
      '<td><strong>' + s.total + '</strong></td><td>' + s.rank + '</td><td>' + s.count + '</td>' +
      '<td>' + quota + '</td><td>' + pct + '%</td></tr>';
  });
  html += '</tbody></table></div>';
  div.innerHTML = html;
}

loadData();
