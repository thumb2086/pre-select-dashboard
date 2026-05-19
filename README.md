# 預選系統分析儀表板

大安高工日間部 115 學年度四技二專甄選入學預選系統資料分析。

## 功能

- **成績分布** — 各校系預選學生成績分布直方圖及統計
- **競爭激烈度** — 預選人數 vs 招生名額比值排行
- **日期衝突** — 同一天面試的校系統整
- **考生排名** — 輸入准考證號查詢在各校系的排名及占比
- **校系詳情** — 篩選倍率、加權倍數、第二階段指定項目、學習歷程限制等

## 資料來源

- 預選名單：大安高工預選系統
- 校系詳細資訊：技專校院招生委員會聯合會 115 學年度資料

## 技術架構

```
dashboard/
├── index.html          # 主頁面
├── dashboard.js        # JavaScript 邏輯
├── vercel.json         # Vercel 部署設定
└── data/               # 分析資料 (JSON)
    ├── score_distribution.json
    ├── competition.json
    ├── date_conflicts.json
    ├── student_rankings.json
    ├── dept_names.json
    ├── dept_details.json
    └── summary.json
```

- 前端：Chart.js 圖表、純靜態 HTML/JS
- 部署：Vercel（自動從 GitHub 部署）
- 資料更新：執行 `scrape_all.py` 從預選系統抓取最新資料，再執行 `analyze.py` 產生 JSON

## 本機工具

| 腳本 | 用途 |
|------|------|
| `scrape_all.py` | 從大安高工預選系統自動抓取所有成績 |
| `fetch_jctv_data2.py` | 從招生委員會下載校系詳細資料 |
| `analyze.py` | 將 CSV 資料轉換為儀表板 JSON |

## 部署

推送到 GitHub 後 Vercel 自動部署：
```
https://pre-select-dashboard.vercel.app
```
