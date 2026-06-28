import os
import json

BASE_DIR = "docs"

def generate_index():
    os.makedirs(BASE_DIR, exist_ok=True)
    archive_data = {}

    years = [d for d in os.listdir(BASE_DIR) if d.isdigit()]
    for year in years:
        y_int = int(year) 
        if y_int not in archive_data: archive_data[y_int] = {}
        months = [d for d in os.listdir(os.path.join(BASE_DIR, year)) if d.isdigit()]
        for month in months:
            m_int = int(month) 
            if m_int not in archive_data[y_int]: archive_data[y_int][m_int] = {}
            files = sorted([f for f in os.listdir(os.path.join(BASE_DIR, year, month)) if f.endswith('.html')], reverse=True)
            for file in files:
                try:
                    parts = file.replace(".html", "").split('_')
                    if len(parts) >= 4:
                        d_int = int(parts[2]) 
                        # 保留了时间截取修复：仅截取 2 到 4 位的字符作为分钟
                        time_str = f"{parts[3][:2]}:{parts[3][2:4]}"
                        file_path = f"{year}/{month}/{file}"

                        title = "📌 网页摘录"
                        with open(os.path.join(BASE_DIR, year, month, file), 'r', encoding='utf-8') as f_html:
                            content = f_html.read(2000)
                            start = content.find('<title>')
                            end = content.find('</title>')
                            if start != -1 and end != -1: title = content[start+7:end]

                        if d_int not in archive_data[y_int][m_int]: archive_data[y_int][m_int][d_int] = []
                        archive_data[y_int][m_int][d_int].append({"time": time_str, "path": file_path, "title": title})
                except: pass

    json_data = json.dumps(archive_data)

    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Web Notes 枢纽</title>
    <style>
        :root { --bg: #f5f5f7; --primary: #2980b9; --accent: #27ae60; --card: #ffffff; --border: #e0e0e0; --text: #333; --btn-blue: #6482f0; }
        body, html { font-family: -apple-system, sans-serif; background: var(--bg); margin: 0; padding: 0; color: var(--text); height: 100%; overflow: auto; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; border-bottom: 1px dashed var(--border); margin-bottom: 20px; }
        .header h1 { margin: 0 0 5px 0; font-size: 2rem; color: var(--primary); font-weight: 800; }
        .header h1 span { color: var(--accent); }
        .header p { margin: 0; font-size: 0.9rem; color: #7f8c8d; letter-spacing: 1px; }
        
        /* 更新了 controls 布局，支持新按钮 */
        .controls { display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px; }
        .select-box { padding: 0 12px; border: 1px solid var(--border); border-radius: 6px; outline: none; font-weight: bold; background: var(--card); color: var(--primary); height: 36px; box-sizing: border-box; font-size: 0.95rem; }
        
        /* 新增按钮样式 */
        .btn-nav, .btn-today {
            background-color: var(--btn-blue);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 36px;
            box-sizing: border-box;
            font-weight: 600;
        }
        .btn-nav { width: 36px; padding: 0; }
        .btn-today { padding: 0 12px; }
        .btn-nav:active, .btn-today:active { transform: scale(0.95); }
        .btn-nav:hover, .btn-today:hover { opacity: 0.9; }

        .calendar-wrapper { background: var(--card); padding: 20px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }
        .weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 13px; color: #888; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
        .days-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
        .day-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-weight: bold; border-radius: 10px; position: relative; cursor: pointer; transition: all 0.2s; }
        .day-cell.empty { visibility: hidden; }
        .day-cell.has-news { color: var(--text); background: #fdfdfd; border: 1px solid #f5f5f5; }
        .day-cell.no-news { color: #dcdde1; }
        .day-cell.selected { background: #e8f8f5; color: var(--accent); border: 1px solid var(--accent); }
        .day-cell.today { background: #fff9e6; border: 1px solid #f1c40f; }
        .dot { width: 5px; height: 5px; background: var(--accent); border-radius: 50%; position: absolute; bottom: 5px; display: none; }
        .day-cell.has-news .dot { display: block; }
        
        .feed-list { display: flex; flex-direction: column; gap: 12px; }
        .feed-item { background: var(--card); padding: 16px 18px; border-radius: 12px; text-decoration: none; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.03); display: flex; flex-direction: row; align-items: center; gap: 15px; border: 1px solid transparent; }
        .feed-time { font-family: sans-serif; font-weight: 800; color: #111; font-size: 0.95rem; flex-shrink: 0; min-width: 45px; text-align: center; }
        .feed-title { color: #7f8c8d; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-grow: 1; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span>Web</span> Matrix</h1>
            <p>全网摘录与深度笔记枢纽</p>
        </div>
        <div class="controls">
            <button class="btn-nav" id="prevMonthBtn">&lt;</button>
            <select class="select-box" id="yearSelect"></select>
            <select class="select-box" id="monthSelect">
                <option value="1">01月</option><option value="2">02月</option><option value="3">03月</option>
                <option value="4">04月</option><option value="5">05月</option><option value="6">06月</option>
                <option value="7">07月</option><option value="8">08月</option><option value="9">09月</option>
                <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
            </select>
            <button class="btn-nav" id="nextMonthBtn">&gt;</button>
            <button class="btn-today" id="todayBtn">回到今天</button>
        </div>
        <div class="calendar-wrapper">
            <div class="weekdays"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div>
            <div class="days-grid" id="daysGrid"></div>
        </div>
        <div class="feed-list" id="feedList"></div>
    </div>

    <script>
        const archiveData = REPLACEME_JSON_DATA;
        const today = new Date();
        let sY = today.getFullYear(), sM = today.getMonth() + 1, sD = today.getDate();
        
        const yearSelect = document.getElementById('yearSelect');
        const monthSelect = document.getElementById('monthSelect');
        const daysGrid = document.getElementById('daysGrid');
        
        function initSelects() {
            const years = Object.keys(archiveData).map(Number).sort((a,b)=>b-a);
            if(!years.includes(sY)) years.unshift(sY);
            yearSelect.innerHTML = ''; // 清空重新生成
            years.forEach(y => {
                const opt = document.createElement('option'); opt.value = y; opt.textContent = y + '年';
                yearSelect.appendChild(opt);
            });
            yearSelect.value = sY; monthSelect.value = sM;
        }

        // 同步 UI 状态，确保下拉框和当前 sY, sM 保持一致
        function syncUI() {
            let yearFound = false;
            for(let i=0; i<yearSelect.options.length; i++) {
                if(parseInt(yearSelect.options[i].value) === sY) { yearFound = true; break; }
            }
            // 如果切换到了一个下拉框里没有的年份，动态添加进去
            if(!yearFound) {
                const opt = document.createElement('option'); opt.value = sY; opt.textContent = sY + '年';
                yearSelect.appendChild(opt);
            }
            yearSelect.value = sY;
            monthSelect.value = sM;
        }

        // 限制日期合法性 (防止例如 1月31日 切到 2月变成 2月31日)
        function clampDate() {
            const daysInMonth = new Date(sY, sM, 0).getDate();
            if (sD > daysInMonth) sD = daysInMonth;
        }
        
        function renderCalendar() {
            daysGrid.innerHTML = '';
            let firstDay = new Date(sY, sM - 1, 1).getDay();
            if (firstDay === 0) firstDay = 7;
            const daysInMonth = new Date(sY, sM, 0).getDate();
            
            for(let i=1; i<firstDay; i++) {
                daysGrid.innerHTML += '<div class="day-cell empty"></div>';
            }
            
            const monthData = (archiveData[sY] && archiveData[sY][sM]) || {};
            for(let d=1; d<=daysInMonth; d++) {
                const hasNews = monthData[d] && monthData[d].length > 0;
                const isToday = sY === today.getFullYear() && sM === today.getMonth()+1 && d === today.getDate();
                const isSelected = d === sD;
                
                let classes = 'day-cell';
                if(hasNews) classes += ' has-news'; else classes += ' no-news';
                if(isToday) classes += ' today';
                if(isSelected) classes += ' selected';
                
                const cell = document.createElement('div');
                cell.className = classes;
                cell.innerHTML = d + `<div class="dot" style="display:${hasNews?'block':'none'}"></div>`;
                cell.onclick = () => { sD = d; renderCalendar(); renderList(); };
                daysGrid.appendChild(cell);
            }
        }
        
        function renderList() {
            const list = document.getElementById('feedList');
            const data = (archiveData[sY] && archiveData[sY][sM] && archiveData[sY][sM][sD]) || [];
            if(data.length) {
                list.innerHTML = data.map(item => `<a href="${item.path}" class="feed-item"><span class="feed-time">${item.time}</span><span class="feed-title">${item.title}</span></a>`).join('');
            } else {
                list.innerHTML = '<div style="text-align:center; padding: 25px 20px; color:#bdc3c7; font-size: 0.9rem;">当日无全网摘录</div>';
            }
        }
        
        yearSelect.onchange = e => { sY = parseInt(e.target.value); clampDate(); renderCalendar(); renderList(); };
        monthSelect.onchange = e => { sM = parseInt(e.target.value); clampDate(); renderCalendar(); renderList(); };

        // 按钮事件绑定
        document.getElementById('prevMonthBtn').onclick = () => {
            sM--;
            if(sM < 1) { sM = 12; sY--; }
            clampDate(); syncUI(); renderCalendar(); renderList();
        };

        document.getElementById('nextMonthBtn').onclick = () => {
            sM++;
            if(sM > 12) { sM = 1; sY++; }
            clampDate(); syncUI(); renderCalendar(); renderList();
        };

        document.getElementById('todayBtn').onclick = () => {
            sY = today.getFullYear();
            sM = today.getMonth() + 1;
            sD = today.getDate();
            syncUI(); renderCalendar(); renderList();
        };
        
        initSelects(); 
        renderCalendar(); 
        renderList();
    </script>
</body>
</html>"""

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content.replace("REPLACEME_JSON_DATA", json_data))

if __name__ == "__main__":
    generate_index()
