import datetime
import http.server
import json
import socketserver
import sqlite3

PORT = 8080
DB_FILE = "platform.db"

# -------------------------------------------------------------
# إدارة قاعدة البيانات (SQLite Database Engine)
# -------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # جدول الإحصائيات العامة
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total_volume REAL,
            platform_revenue REAL,
            trading_status INTEGER
        )
    ''')
    
    # جدول المستخدمين
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            balance REAL,
            status TEXT
        )
    ''')
    
    # جدول أصول المحفظة (العملات)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_assets (
            symbol TEXT PRIMARY KEY,
            amount REAL,
            avg_price REAL
        )
    ''')
    
    # جدول سجل الصفقات
    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id TEXT PRIMARY KEY,
            symbol TEXT,
            type TEXT,
            amount REAL,
            price REAL,
            time TEXT
        )
    ''')
    
    # جدول طلبات السحب
    cur.execute('''
        CREATE TABLE IF NOT EXISTS withdraw_requests (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            network TEXT,
            address TEXT,
            amount REAL,
            time TEXT,
            status TEXT
        )
    ''')
    
    # حقن بيانات أولية إذا كانت القاعدة فارغة
    cur.execute('SELECT COUNT(*) FROM stats')
    if cur.fetchone()[0] == 0:
        cur.execute('INSERT INTO stats VALUES (1, 4825900.0, 14250.0, 1)')
        
        users_initial = [
            ("USR-101", "أحمد الشمري", "ahmed@example.com", 35000.0, "نشط"),
            ("USR-102", "سارة القحطاني", "sara.q@example.com", 18450.0, "نشط"),
            ("USR-103", "محمود إبراهيم", "m.ibrahim@example.com", 820.0, "معلق"),
            ("USR-104", "خالد المنصور", "khaled@example.com", 92400.0, "نشط")
        ]
        cur.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?)', users_initial)
        
        assets_initial = [
            ("BTC", 0.65, 63200.0),
            ("ETH", 5.20, 3100.0),
            ("SOL", 42.0, 140.0),
            ("BNB", 15.0, 575.0)
        ]
        cur.executemany('INSERT INTO portfolio_assets VALUES (?, ?, ?)', assets_initial)
        
        history_initial = [
            ("TX-9011", "BTC", "BUY", 0.15, 64100.0, "2026-09-01 10:15"),
            ("TX-9010", "ETH", "BUY", 2.50, 3050.0, "2026-08-31 18:40")
        ]
        cur.executemany('INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)', history_initial)
        
        withdraws_initial = [
            ("REQ-7701", "USR-101", "USDT BEP20", "0x71C...98B2", 2500.0, "2026-09-01 03:20", "معلق"),
            ("REQ-7700", "USR-104", "USDT BEP20", "0x34A...21F4", 12000.0, "2026-08-31 22:10", "مكتمل")
        ]
        cur.executemany('INSERT INTO withdraw_requests VALUES (?, ?, ?, ?, ?, ?, ?)', withdraws_initial)
        
    conn.commit()
    conn.close()

MARKET_PRICES = {
    "BTC": 64850.0,
    "ETH": 3490.0,
    "SOL": 148.5,
    "BNB": 585.0,
    "XRP": 0.58,
}

# -------------------------------------------------------------
# 1. كود واجهة لوحة التحكم الفائقة /admi1/
# -------------------------------------------------------------
ADMIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>غرفة الإشراف والتحكم الكلي | الجود برو</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --admin-bg: #05070c; --admin-panel: #0d121d; --admin-card: rgba(19, 26, 41, 0.85);
            --admin-border: rgba(255, 255, 255, 0.08); --gold: #ffb703; --green: #00f29b;
            --red: #ff3366; --blue: #00d2ff; --text-main: #f8fafc; --text-sub: #94a3b8;
            --font-mono: 'JetBrains Mono', monospace;
        }
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Cairo', sans-serif; }
        body { background: var(--admin-bg); color: var(--text-main); display:flex; min-height:100vh; overflow-x:hidden; }
        aside { width: 280px; background: var(--admin-panel); border-left: 1px solid var(--admin-border); display: flex; flex-direction: column; padding: 24px 16px; position: fixed; height: 100vh; right: 0; top: 0; z-index: 100; }
        .side-brand { display: flex; align-items: center; gap: 12px; padding-bottom: 24px; border-bottom: 1px solid var(--admin-border); margin-bottom: 24px; }
        .side-brand-icon { width: 44px; height: 44px; background: linear-gradient(135deg, var(--gold), #fb8500); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #000; font-size: 1.4rem; box-shadow: 0 0 20px rgba(255, 183, 3, 0.35); }
        .side-nav { list-style: none; display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }
        .side-link { display: flex; align-items: center; gap: 14px; padding: 12px 16px; color: var(--text-sub); text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: all 0.2s ease; }
        .side-link:hover, .side-link.active { background: rgba(255, 183, 3, 0.12); color: var(--gold); border: 1px solid rgba(255, 183, 3, 0.25); }
        .side-link i { font-size: 1.1rem; width: 22px; text-align: center; }
        main { margin-right: 280px; flex-grow: 1; padding: 30px; display: flex; flex-direction: column; gap: 24px; }
        @media (max-width: 992px) { aside { display: none; } main { margin-right: 0; } }
        .top-stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
        .stat-card { background: var(--admin-card); border: 1px solid var(--admin-border); border-radius: 16px; padding: 20px; backdrop-filter: blur(12px); position: relative; overflow: hidden; }
        .stat-card::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: var(--stat-color, var(--gold)); }
        .stat-label { font-size: 0.8rem; color: var(--text-sub); margin-bottom: 6px; }
        .stat-num { font-size: 1.8rem; font-weight: 900; font-family: var(--font-mono); color: #fff; }
        .content-card { background: var(--admin-card); border: 1px solid var(--admin-border); border-radius: 16px; padding: 24px; backdrop-filter: blur(12px); }
        .card-header-box { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--admin-border); padding-bottom: 12px; }
        .card-title { font-size: 1.1rem; font-weight: 800; display: flex; align-items: center; gap: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th { text-align: right; padding: 12px; color: var(--text-sub); border-bottom: 1px solid var(--admin-border); font-weight: 600; }
        td { padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.02); font-family: var(--font-mono); }
        .badge-status { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; font-family: 'Cairo'; }
        .badge-pending { background: rgba(255, 183, 3, 0.15); color: var(--gold); }
        .badge-done { background: rgba(0, 242, 155, 0.15); color: var(--green); }
        .badge-reject { background: rgba(255, 51, 102, 0.15); color: var(--red); }
        .btn-table-action { border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 0.75rem; margin-left: 4px; }
        .btn-approve { background: var(--green); color: #000; }
        .btn-reject { background: rgba(255, 51, 102, 0.2); color: var(--red); border: 1px solid var(--red); }
        .input-admin { background: rgba(0,0,0,0.5); border: 1px solid var(--admin-border); padding: 8px 12px; border-radius: 8px; color: #fff; outline: none; font-family: var(--font-mono); }
        .tab-section { display: none; }
        .tab-section.active { display: block; }
    </style>
</head>
<body>
    <aside>
        <div class="side-brand">
            <div class="side-brand-icon"><i class="fa-solid fa-database"></i></div>
            <div>
                <h2 style="font-size: 1.1rem; font-weight:900;">إدارة الجود</h2>
                <span style="font-size: 0.7rem; color:var(--green); font-weight:700;">SQLITE DATABASE ACTIVE</span>
            </div>
        </div>
        <ul class="side-nav">
            <li class="side-link active" onclick="switchTab('overview', this)"><i class="fa-solid fa-gauge-high"></i> النظرة الشاملة والـ KPIs</li>
            <li class="side-link" onclick="switchTab('withdraws', this)"><i class="fa-solid fa-money-bill-transfer"></i> طلبات السحب (USDT)</li>
            <li class="side-link" onclick="switchTab('users', this)"><i class="fa-solid fa-users-gear"></i> إدارة العملاء والمحافظ</li>
            <li class="side-link" onclick="switchTab('prices', this)"><i class="fa-solid fa-chart-candlestick"></i> أسعار السوق الفورية</li>
            <li class="side-link" onclick="window.location.href='/'"><i class="fa-solid fa-arrow-up-right-from-square"></i> منصة التداول الحية</li>
        </ul>
        <div style="margin-top:auto; padding:12px; background:rgba(255,51,102,0.1); border:1px solid rgba(255,51,102,0.3); border-radius:10px;">
            <div style="font-size:0.75rem; color:var(--red); font-weight:bold; margin-bottom:6px;">حالة محرك التداول</div>
            <button id="btn-engine-toggle" onclick="toggleEngine()" style="width:100%; padding:8px; background:var(--red); color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:0.8rem;">إيقاف التداول طارئاً</button>
        </div>
    </aside>

    <main>
        <div class="top-stats-grid">
            <div class="stat-card" style="--stat-color: var(--blue);">
                <div class="stat-label"><i class="fa-solid fa-users"></i> إجمالي المستخدمين المسجلين</div>
                <div class="stat-num" id="adm-user-count">0</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--green);">
                <div class="stat-label"><i class="fa-solid fa-vault"></i> السيولة الكلية في النظام</div>
                <div class="stat-num" id="adm-total-liquidity">$0</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--gold);">
                <div class="stat-label"><i class="fa-solid fa-chart-line"></i> حجم التداول الإجمالي</div>
                <div class="stat-num" id="adm-total-volume">$0</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--red);">
                <div class="stat-label"><i class="fa-solid fa-clock"></i> طلبات السحب المعلقة</div>
                <div class="stat-num" id="adm-pending-withdraws" style="color:var(--gold);">0</div>
            </div>
        </div>

        <div id="tab-overview" class="tab-section active">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-list-check" style="color:var(--blue);"></i> آخر العمليات المالية المسجلة بالقاعدة</div>
                    <span style="font-size:0.8rem; color:var(--green);">● تخزين دائم ومباشر في platform.db</span>
                </div>
                <table>
                    <thead>
                        <tr><th>المعرف</th><th>العملة/الرمز</th><th>نوع العملية</th><th>الكمية</th><th>السعر</th><th>الوقت والتاريخ</th></tr>
                    </thead>
                    <tbody id="adm-overview-history"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-withdraws" class="tab-section">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-money-bill-transfer" style="color:var(--gold);"></i> مركز معالجة طلبات السحب (USDT BEP20)</div>
                </div>
                <table>
                    <thead>
                        <tr><th>معرف الطلب</th><th>العميل</th><th>الشبكة</th><th>عنوان المحفظة (Address)</th><th>المبلغ المطلوب</th><th>الحالة</th><th>الإجراء</th></tr>
                    </thead>
                    <tbody id="adm-withdraws-tbody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-users" class="tab-section">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-users-gear" style="color:var(--green);"></i> حسابات العملاء وتعديل الأرصدة</div>
                </div>
                <table>
                    <thead>
                        <tr><th>المعرف</th><th>الاسم الكامل</th><th>البريد الإلكتروني</th><th>الرصيد الكاش</th><th>الحالة</th><th>تعديل الرصيد</th></tr>
                    </thead>
                    <tbody id="adm-users-tbody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-prices" class="tab-section">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-chart-candlestick" style="color:var(--gold);"></i> ضبط أسعار السوق الفورية للعملاء</div>
                </div>
                <table>
                    <thead>
                        <tr><th>الرمز المالي</th><th>السعر المباشر</th><th>السعر المستهدف الجديد</th><th>تطبيق</th></tr>
                    </thead>
                    <tbody id="adm-prices-tbody"></tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        function switchTab(tabId, el) {
            document.querySelectorAll('.tab-section').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.side-link').forEach(l => l.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            el.classList.add('active');
        }

        async function loadAdminData() {
            try {
                const res = await fetch('/api/admin/all-data');
                const data = await res.json();

                document.getElementById('adm-user-count').innerText = data.users.length;
                document.getElementById('adm-total-volume').innerText = '$' + data.stats.total_volume.toLocaleString();
                
                let totalCash = data.users.reduce((acc, u) => acc + u.balance, 0);
                document.getElementById('adm-total-liquidity').innerText = '$' + totalCash.toLocaleString();

                let pendingCount = data.withdraws.filter(w => w.status === 'معلق').length;
                document.getElementById('adm-pending-withdraws').innerText = pendingCount;

                const btnEng = document.getElementById('btn-engine-toggle');
                if(data.stats.trading_status) {
                    btnEng.innerText = 'إيقاف التداول طارئاً';
                    btnEng.style.background = 'var(--red)';
                    btnEng.style.color = '#fff';
                } else {
                    btnEng.innerText = 'استئناف التداول';
                    btnEng.style.background = 'var(--green)';
                    btnEng.style.color = '#000';
                }

                const histBody = document.getElementById('adm-overview-history');
                histBody.innerHTML = '';
                data.history.forEach(tx => {
                    histBody.innerHTML += `
                        <tr>
                            <td><b>${tx.id}</b></td>
                            <td>${tx.symbol}</td>
                            <td style="color:${tx.type==='BUY'?'var(--green)':'var(--red)'}; font-weight:bold;">${tx.type}</td>
                            <td>${tx.amount}</td>
                            <td>$${tx.price.toLocaleString()}</td>
                            <td style="color:var(--text-sub);">${tx.time}</td>
                        </tr>
                    `;
                });

                const withBody = document.getElementById('adm-withdraws-tbody');
                withBody.innerHTML = '';
                data.withdraws.forEach(w => {
                    let badgeClass = w.status === 'معلق' ? 'badge-pending' : (w.status === 'مكتمل' ? 'badge-done' : 'badge-reject');
                    let actions = w.status === 'معلق' ? `
                        <button class="btn-table-action btn-approve" onclick="handleWithdraw('${w.id}', 'APPROVE')">قبول وإرسال</button>
                        <button class="btn-table-action btn-reject" onclick="handleWithdraw('${w.id}', 'REJECT')">رفض</button>
                    ` : `<span style="color:var(--text-sub); font-size:0.75rem;">تمت المعالجة</span>`;

                    withBody.innerHTML += `
                        <tr>
                            <td><b>${w.id}</b></td>
                            <td>${w.user_id}</td>
                            <td><span style="color:var(--gold);">${w.network}</span></td>
                            <td style="font-size:0.75rem; color:var(--blue);">${w.address}</td>
                            <td style="font-weight:bold; color:#fff;">$${w.amount.toLocaleString()}</td>
                            <td><span class="badge-status ${badgeClass}">${w.status}</span></td>
                            <td>${actions}</td>
                        </tr>
                    `;
                });

                const usersBody = document.getElementById('adm-users-tbody');
                usersBody.innerHTML = '';
                data.users.forEach(u => {
                    usersBody.innerHTML += `
                        <tr>
                            <td><b>${u.id}</b></td>
                            <td style="font-family:'Cairo'; font-weight:700;">${u.name}</td>
                            <td style="color:var(--text-sub);">${u.email}</td>
                            <td style="color:var(--green); font-weight:bold;">$${u.balance.toLocaleString()}</td>
                            <td><span class="badge-status badge-done">${u.status}</span></td>
                            <td>
                                <input type="number" id="usr-adj-${u.id}" placeholder="+/- مبلغ" style="width:110px;" class="input-admin">
                                <button class="btn-table-action btn-approve" onclick="adjustUserBalance('${u.id}')">تعديل</button>
                            </td>
                        </tr>
                    `;
                });

                const priceBody = document.getElementById('adm-prices-tbody');
                priceBody.innerHTML = '';
                for(let [sym, p] of Object.entries(data.market_prices)) {
                    priceBody.innerHTML += `
                        <tr>
                            <td><b>${sym}/USDT</b></td>
                            <td>$${p.toLocaleString()}</td>
                            <td><input type="number" id="adm-p-${sym}" value="${p}" step="any" class="input-admin" style="width:120px;"></td>
                            <td><button class="btn-table-action btn-approve" onclick="saveNewPrice('${sym}')">حفظ السعر</button></td>
                        </tr>
                    `;
                }
            } catch(e) {
                console.error("خطأ في جلب بيانات لوحة التحكم:", e);
            }
        }

        async function handleWithdraw(reqId, action) {
            await fetch('/api/admin/action-withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ req_id: reqId, action: action })
            });
            alert('تم حفظ الإجراء في قاعدة البيانات بنجاح');
            loadAdminData();
        }

        async function adjustUserBalance(userId) {
            const val = parseFloat(document.getElementById('usr-adj-' + userId).value);
            if(isNaN(val)) return alert('أدخل قيمة صحيحة للزيادة أو الخصم');
            await fetch('/api/admin/adjust-balance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: userId, amount: val })
            });
            alert('تم تعديل الرصيد وتحديث قاعدة البيانات بنجاح');
            loadAdminData();
        }

        async function saveNewPrice(sym) {
            const p = parseFloat(document.getElementById('adm-p-' + sym).value);
            if(isNaN(p) || p <= 0) return alert('أدخل سعراً صحيحاً');
            await fetch('/api/admin/set-price', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ symbol: sym, price: p })
            });
            alert('تم تحديث سعر ' + sym);
            loadAdminData();
        }

        async function toggleEngine() {
            await fetch('/api/admin/toggle-engine', { method: 'POST' });
            loadAdminData();
        }

        window.addEventListener('DOMContentLoaded', loadAdminData);
    </script>
</body>
</html>
"""

# -------------------------------------------------------------
# 2. كود واجهة التداول للمستخدمين /
# -------------------------------------------------------------
TRADING_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الجود العالمية للتداول</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-base: #07090e; --bg-card: rgba(18, 25, 38, 0.85); --border-glass: rgba(255, 255, 255, 0.07);
            --accent-green: #00f29b; --accent-red: #ff3864; --accent-cyan: #00d4ff; --accent-gold: #ffb703;
            --text-primary: #f8fafc; --text-muted: #8492a6; --font-mono: 'JetBrains Mono', monospace;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Cairo', sans-serif; }
        body { background-color: var(--bg-base); color: var(--text-primary); min-height: 100vh; display: flex; flex-direction: column; }
        header { background: rgba(14, 19, 29, 0.95); border-bottom: 1px solid var(--border-glass); padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .brand-box { display: flex; align-items: center; gap: 12px; }
        .brand-icon { width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent-gold), #fb8500); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #000; box-shadow: 0 0 20px rgba(255, 183, 3, 0.35); }
        .btn-withdraw-header { background: linear-gradient(135deg, rgba(255, 183, 3, 0.2), rgba(251, 133, 0, 0.2)); color: var(--accent-gold); border: 1px solid rgba(255, 183, 3, 0.4); padding: 8px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; }
        
        .main-layout { display: grid; grid-template-columns: 280px 1fr 340px; gap: 15px; padding: 15px; flex-grow: 1; }
        @media (max-width: 1200px) { .main-layout { grid-template-columns: 1fr; } }
        
        .glass-panel { background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 14px; padding: 16px; backdrop-filter: blur(15px); }
        .panel-heading { font-size: 0.95rem; font-weight: 700; margin-bottom: 12px; display: flex; justify-content: space-between; }
        .balance-card { background: linear-gradient(135deg, rgba(0, 242, 155, 0.08), rgba(0, 212, 255, 0.04)); border: 1px solid rgba(0, 242, 155, 0.2); border-radius: 12px; padding: 14px; margin-bottom: 14px; }
        .balance-card .val { font-size: 1.6rem; font-weight: 900; font-family: var(--font-mono); margin: 4px 0; }
        
        .chart-box { height: 500px; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-glass); margin-bottom: 15px; background: #0d121d; position: relative; }
        .tradingview-widget-container { height: 100% !important; width: 100% !important; }
        
        .order-tabs { display: flex; gap: 8px; margin-bottom: 15px; }
        .order-tab { flex: 1; padding: 10px; text-align: center; border-radius: 8px; font-weight: 800; cursor: pointer; border: 1px solid var(--border-glass); background: rgba(255, 255, 255, 0.03); }
        .order-tab.buy.active { background: var(--accent-green); color: #000; border-color: var(--accent-green); }
        .order-tab.sell.active { background: var(--accent-red); color: #fff; border-color: var(--accent-red); }
        .custom-input { width: 100%; background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-glass); border-radius: 8px; padding: 10px 12px; color: #fff; font-family: var(--font-mono); outline: none; margin-bottom: 12px; }
        .btn-order-submit { width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: 900; cursor: pointer; }
        .btn-order-submit.buy { background: var(--accent-green); color: #000; }
        .btn-order-submit.sell { background: var(--accent-red); color: #fff; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        th { text-align: right; padding: 8px; color: var(--text-muted); border-bottom: 1px solid var(--border-glass); }
        td { padding: 10px 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.02); font-family: var(--font-mono); }
        
        .withdraw-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5, 7, 12, 0.88); backdrop-filter: blur(25px); z-index: 9999; display: none; justify-content: center; align-items: center; padding: 20px; }
        .withdraw-modal { background: #0f1624; border: 1px solid rgba(255, 183, 3, 0.3); border-radius: 20px; width: 100%; max-width: 480px; padding: 30px; position: relative; }
        .check-circle { width: 80px; height: 80px; background: rgba(0, 242, 155, 0.15); border: 2px solid var(--accent-green); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: var(--accent-green); margin: 0 auto 20px; }
    </style>
</head>
<body>
    <header>
        <div class="brand-box">
            <div class="brand-icon"><i class="fa-solid fa-gem"></i></div>
            <div><h1 style="font-size:1.2rem; font-weight:900;">الجود للتداول</h1><span style="font-size:0.7rem; color:var(--accent-gold);">PRO TRADING PLATFORM</span></div>
        </div>
        <div style="display:flex; gap:10px;">
            <button class="btn-withdraw-header" onclick="document.getElementById('withdraw-modal').style.display='flex'"><i class="fa-solid fa-wallet"></i> سحب الأرباح</button>
            <button class="btn-withdraw-header" style="background:rgba(255,255,255,0.05); color:#fff;" onclick="window.location.href='/admi1/'"><i class="fa-solid fa-shield-halved"></i> الإشراف /admi1/</button>
        </div>
    </header>

    <div class="main-layout">
        <!-- المحفظة -->
        <div class="glass-panel">
            <div class="panel-heading"><span><i class="fa-solid fa-chart-pie" style="color:var(--accent-gold)"></i> المحفظة (قاعدة بيانات حية)</span></div>
            <div class="balance-card">
                <div style="font-size:0.8rem; color:var(--text-muted)">إجمالي رصيد الحساب</div>
                <div class="val" id="net-worth-display">$0.00</div>
                <div style="font-size:0.8rem; margin-top: 5px;">كاش متاح: <b id="cash-balance-display" style="color:var(--accent-green);">$0.00</b></div>
            </div>
            <div id="assets-container"></div>
        </div>

        <!-- الشارت -->
        <div>
            <div class="chart-box" id="tv_chart_container">
                <div class="tradingview-widget-container" id="tv_chart"></div>
            </div>
            <div class="glass-panel">
                <div class="panel-heading"><span><i class="fa-solid fa-clock-rotate-left"></i> سجل العمليات الموثق</span></div>
                <table>
                    <thead><tr><th>الرمز</th><th>النوع</th><th>الكمية</th><th>السعر</th><th>الوقت</th></tr></thead>
                    <tbody id="history-table-body"></tbody>
                </table>
            </div>
        </div>

        <!-- التداول -->
        <div class="glass-panel">
            <div class="panel-heading"><span><i class="fa-solid fa-bolt-lightning" style="color:var(--accent-cyan)"></i> تداول فوري</span></div>
            <div class="order-tabs">
                <div class="order-tab buy active" id="tab-buy" onclick="setSide('BUY')">شراء</div>
                <div class="order-tab sell" id="tab-sell" onclick="setSide('SELL')">بيع</div>
            </div>
            <select class="custom-input" id="symbol-selector" onchange="onSymChange()">
                <option value="BTC">BTC/USDT</option>
                <option value="ETH">ETH/USDT</option>
                <option value="SOL">SOL/USDT</option>
                <option value="BNB">BNB/USDT</option>
            </select>
            <input type="number" class="custom-input" id="order-quantity" placeholder="الكمية" step="any" oninput="calcTotal()">
            <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:8px; margin-bottom:12px; font-size:0.85rem;">
                <div>السعر: <span id="live-price-tag">$0.00</span></div>
                <div style="margin-top:4px; font-weight:bold;">الإجمالي: <span id="order-total-tag" style="color:var(--accent-gold)">$0.00</span></div>
            </div>
            <button class="btn-order-submit buy" id="submit-order-btn" onclick="executeTrade()">تنفيذ الأمر</button>
        </div>
    </div>

    <!-- نافذة السحب -->
    <div class="withdraw-overlay" id="withdraw-modal">
        <div class="withdraw-modal">
            <div onclick="document.getElementById('withdraw-modal').style.display='none'" style="position:absolute; top:20px; left:20px; cursor:pointer; font-size:1.2rem;"><i class="fa-solid fa-xmark"></i></div>
            <div id="w-form">
                <h3 style="margin-bottom:15px; color:var(--accent-gold);"><i class="fa-solid fa-money-bill-transfer"></i> سحب الأرباح</h3>
                <div style="background:rgba(255,183,3,0.1); border:1px solid rgba(255,183,3,0.3); padding:6px 10px; border-radius:6px; font-size:0.8rem; color:var(--accent-gold); margin-bottom:12px;">شبكة السحب: USDT (BEP20 - BNB Smart Chain)</div>
                <input type="text" class="custom-input" id="w-address" placeholder="عنوان محفظة USDT BEP20 (0x...)">
                <input type="number" class="custom-input" id="w-amt" placeholder="مبلغ السحب ($)">
                <button class="btn-order-submit" style="background:linear-gradient(135deg, var(--accent-gold), #fb8500); color:#000;" onclick="submitWithdraw()">سحب الارباح</button>
            </div>
            <div id="w-success" style="display:none; text-align:center; padding:15px;">
                <div class="check-circle"><i class="fa-solid fa-check"></i></div>
                <h3 style="margin-bottom:8px;">تتم معالجة السحب</h3>
                <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:15px;">تم استلام طلب السحب وحفظه في قاعدة البيانات ويتم مراجعته وتأكيده.</p>
                <button class="btn-withdraw-header" onclick="document.getElementById('withdraw-modal').style.display='none'; document.getElementById('w-form').style.display='block'; document.getElementById('w-success').style.display='none';">حسناً</button>
            </div>
        </div>
    </div>

    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        let curSide = 'BUY';
        let curSym = 'BTC';
        let marketPrices = {};

        function initChart(sym) {
            const container = document.getElementById('tv_chart');
            if (!container) return;
            container.innerHTML = '';

            if (typeof TradingView !== 'undefined') {
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "BINANCE:" + sym + "USDT",
                    "interval": "15",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "ar_AE",
                    "toolbar_bg": "#0d121d",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": true,
                    "container_id": "tv_chart"
                });
            } else {
                container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#ff3864;font-size:0.9rem;">تعذر تحميل الشارت.. تأكد من اتصال اللابتوب بالإنترنت ومسح مانع الإعلانات.</div>';
            }
        }

        function setSide(side) {
            curSide = side;
            document.getElementById('tab-buy').classList.toggle('active', side === 'BUY');
            document.getElementById('tab-sell').classList.toggle('active', side === 'SELL');
            const btn = document.getElementById('submit-order-btn');
            btn.className = 'btn-order-submit ' + (side === 'BUY' ? 'buy' : 'sell');
            btn.innerText = side === 'BUY' ? 'تنفيذ الشراء' : 'تنفيذ البيع';
        }

        function onSymChange() {
            curSym = document.getElementById('symbol-selector').value;
            initChart(curSym);
            calcTotal();
        }

        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const d = await res.json();
                marketPrices = d.market_prices;
                document.getElementById('net-worth-display').innerText = '$' + d.total_net_worth.toLocaleString();
                document.getElementById('cash-balance-display').innerText = '$' + d.cash_balance.toLocaleString();

                const ac = document.getElementById('assets-container');
                ac.innerHTML = '';
                for(let [sym, info] of Object.entries(d.assets)) {
                    ac.innerHTML += `<div style="display:flex; justify-content:space-between; padding:8px; border-bottom:1px solid rgba(255,255,255,0.03);"><div><b>${sym}</b> <small style="color:var(--text-muted)">(${info.amount})</small></div><div>$${(info.amount * (marketPrices[sym]||info.avg_price)).toFixed(2)}</div></div>`;
                }

                const hb = document.getElementById('history-table-body');
                hb.innerHTML = '';
                d.history.forEach(tx => {
                    hb.innerHTML += `<tr><td><b>${tx.symbol}</b></td><td style="color:${tx.type==='BUY'?'var(--accent-green)':'var(--accent-red)'}">${tx.type}</td><td>${tx.amount}</td><td>$${tx.price}</td><td style="color:var(--text-muted)">${tx.time}</td></tr>`;
                });
                calcTotal();
            } catch(err) {
                console.error("خطأ في جلب بيانات التداول:", err);
            }
        }

        function calcTotal() {
            const amt = parseFloat(document.getElementById('order-quantity').value) || 0;
            const p = marketPrices[curSym] || 0;
            document.getElementById('live-price-tag').innerText = '$' + p;
            document.getElementById('order-total-tag').innerText = '$' + (amt * p).toFixed(2);
        }

        async function executeTrade() {
            const amt = parseFloat(document.getElementById('order-quantity').value);
            if(!amt || amt <= 0) return alert('أدخل كمية صحيحة');
            const res = await fetch('/api/trade', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ symbol: curSym, order_type: curSide, amount: amt })
            });
            const d = await res.json();
            alert(d.message);
            if(d.status === 'success') { 
                document.getElementById('order-quantity').value = ''; 
                loadData(); 
            }
        }

        async function submitWithdraw() {
            const addr = document.getElementById('w-address').value.trim();
            const amt = parseFloat(document.getElementById('w-amt').value);
            if(!addr || !amt || amt <= 0) return alert('أدخل العنوان والمبلغ بالشكل الصحيح');

            const res = await fetch('/api/withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ address: addr, amount: amt })
            });
            const d = await res.json();
            if(d.status === 'success') {
                document.getElementById('w-form').style.display = 'none';
                document.getElementById('w-success').style.display = 'block';
                loadData();
            } else {
                alert(d.message);
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            initChart('BTC');
            loadData();
        });
    </script>
</body>
</html>
"""

# -------------------------------------------------------------
# 3. محرك الخادم والـ API الموحد (Unified HTTP Handler with SQLite)
# -------------------------------------------------------------
class FullPlatformServer(http.server.BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/admi1", "/admi1/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ADMIN_PAGE.encode("utf-8"))

        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TRADING_PAGE.encode("utf-8"))

        elif self.path == "/api/data":
            conn = get_db()
            cur = conn.cursor()
            
            # جلب كاش المستخدم الافتراضي USR-101
            cur.execute('SELECT balance FROM users WHERE id = "USR-101"')
            user_row = cur.fetchone()
            cash_balance = user_row["balance"] if user_row else 0.0
            
            # جلب الأصول
            cur.execute('SELECT symbol, amount, avg_price FROM portfolio_assets')
            assets = {}
            total_assets = 0.0
            for r in cur.fetchall():
                sym = r["symbol"]
                amt = r["amount"]
                avg = r["avg_price"]
                assets[sym] = {"amount": amt, "avg_price": avg}
                total_assets += amt * MARKET_PRICES.get(sym, avg)
                
            # جلب سجل العمليات
            cur.execute('SELECT * FROM history ORDER BY rowid DESC LIMIT 30')
            history = [dict(r) for r in cur.fetchall()]
            conn.close()
            
            self._json({
                "cash_balance": round(cash_balance, 2),
                "total_net_worth": round(cash_balance + total_assets, 2),
                "assets": assets,
                "history": history,
                "market_prices": MARKET_PRICES
            })

        elif self.path == "/api/admin/all-data":
            conn = get_db()
            cur = conn.cursor()
            
            cur.execute('SELECT * FROM stats WHERE id = 1')
            stats_row = cur.fetchone()
            stats = {
                "total_volume": stats_row["total_volume"],
                "platform_revenue": stats_row["platform_revenue"],
                "trading_status": bool(stats_row["trading_status"])
            }
            
            cur.execute('SELECT * FROM users')
            users = [dict(r) for r in cur.fetchall()]
            
            cur.execute('SELECT * FROM withdraw_requests ORDER BY rowid DESC')
            withdraws = [dict(r) for r in cur.fetchall()]
            
            cur.execute('SELECT * FROM history ORDER BY rowid DESC LIMIT 40')
            history = [dict(r) for r in cur.fetchall()]
            conn.close()

            self._json({
                "stats": stats,
                "users": users,
                "withdraws": withdraws,
                "history": history,
                "market_prices": MARKET_PRICES
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # 1. أوامر التداول
        if self.path == "/api/trade":
            conn = get_db()
            cur = conn.cursor()
            
            cur.execute('SELECT trading_status FROM stats WHERE id = 1')
            if not bool(cur.fetchone()["trading_status"]):
                conn.close()
                return self._json({"status": "error", "message": "عذراً! محرك التداول معطل مؤقتاً لأعمال الصيانة."})

            sym = body.get("symbol", "BTC").upper()
            side = body.get("order_type")
            amt = float(body.get("amount", 0))
            price = MARKET_PRICES.get(sym, 100.0)
            cost = amt * price

            cur.execute('SELECT balance FROM users WHERE id = "USR-101"')
            cash = cur.fetchone()["balance"]

            if side == "BUY":
                if cash < cost:
                    conn.close()
                    return self._json({"status": "error", "message": "رصيدك غير كافٍ لإتمام الصفقة!"})
                
                # خصم الرصيد
                cur.execute('UPDATE users SET balance = balance - ? WHERE id = "USR-101"', (cost,))
                
                # تحديث أو إضافة الأصل
                cur.execute('SELECT amount, avg_price FROM portfolio_assets WHERE symbol = ?', (sym,))
                asset = cur.fetchone()
                if asset:
                    new_amt = asset["amount"] + amt
                    new_avg = ((asset["amount"] * asset["avg_price"]) + cost) / new_amt
                    cur.execute('UPDATE portfolio_assets SET amount = ?, avg_price = ? WHERE symbol = ?', 
                                (round(new_amt, 4), new_avg, sym))
                else:
                    cur.execute('INSERT INTO portfolio_assets VALUES (?, ?, ?)', (sym, round(amt, 4), price))
                    
            elif side == "SELL":
                cur.execute('SELECT amount FROM portfolio_assets WHERE symbol = ?', (sym,))
                asset = cur.fetchone()
                if not asset or asset["amount"] < amt:
                    conn.close()
                    return self._json({"status": "error", "message": "لا تمتلك كمية كافية من العملة للبيع!"})
                
                cur.execute('UPDATE users SET balance = balance + ? WHERE id = "USR-101"', (cost,))
                rem_amt = asset["amount"] - amt
                if rem_amt <= 0.0001:
                    cur.execute('DELETE FROM portfolio_assets WHERE symbol = ?', (sym,))
                else:
                    cur.execute('UPDATE portfolio_assets SET amount = ? WHERE symbol = ?', (round(rem_amt, 4), sym))

            # تحديث الإحصائيات العامة
            cur.execute('UPDATE stats SET total_volume = total_volume + ? WHERE id = 1', (cost,))
            
            # تسجيل في جدول التاريخ
            tx_id = f"TX-{int(datetime.datetime.now().timestamp()) % 100000}"
            cur.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)', (tx_id, sym, side, amt, price, now_str))
            
            conn.commit()
            conn.close()
            self._json({"status": "success", "message": f"تم تنفيذ عملية الـ {side} وتوثيقها في قاعدة البيانات!"})

        # 2. طلبات سحب الأرباح
        elif self.path == "/api/withdraw":
            addr = body.get("address")
            amt = float(body.get("amount", 0))
            
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT balance FROM users WHERE id = "USR-101"')
            cash = cur.fetchone()["balance"]
            
            if cash < amt:
                conn.close()
                return self._json({"status": "error", "message": "رصيدك المتاح أقل من المبلغ المطلوب سحبه!"})

            cur.execute('UPDATE users SET balance = balance - ? WHERE id = "USR-101"', (amt,))
            req_id = f"REQ-{int(datetime.datetime.now().timestamp()) % 100000}"
            cur.execute('INSERT INTO withdraw_requests VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (req_id, "USR-101", "USDT BEP20", addr, amt, now_str, "معلق"))
            
            tx_id = f"TX-{int(datetime.datetime.now().timestamp()) % 100000}"
            cur.execute('INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)',
                        (tx_id, "USDT BEP20", "WITHDRAW", amt, 1.0, now_str))
            
            conn.commit()
            conn.close()
            self._json({"status": "success"})

        # 3. إدارة السحوبات
        elif self.path == "/api/admin/action-withdraw":
            req_id = body.get("req_id")
            action = body.get("action")
            conn = get_db()
            cur = conn.cursor()
            
            new_status = "مكتمل" if action == "APPROVE" else "مرفوض"
            cur.execute('UPDATE withdraw_requests SET status = ? WHERE id = ?', (new_status, req_id))
            
            if action == "REJECT":
                cur.execute('SELECT user_id, amount FROM withdraw_requests WHERE id = ?', (req_id,))
                row = cur.fetchone()
                if row:
                    cur.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (row["amount"], row["user_id"]))
            
            conn.commit()
            conn.close()
            self._json({"status": "success"})

        # 4. تعديل رصيد مستخدم
        elif self.path == "/api/admin/adjust-balance":
            uid = body.get("user_id")
            amt = float(body.get("amount", 0))
            conn = get_db()
            cur = conn.cursor()
            cur.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amt, uid))
            conn.commit()
            conn.close()
            self._json({"status": "success"})

        # 5. ضبط الأسعار
        elif self.path == "/api/admin/set-price":
            sym = body.get("symbol")
            price = float(body.get("price"))
            MARKET_PRICES[sym] = price
            self._json({"status": "success"})

        # 6. مفتاح الطوارئ
        elif self.path == "/api/admin/toggle-engine":
            conn = get_db()
            cur = conn.cursor()
            cur.execute('UPDATE stats SET trading_status = CASE WHEN trading_status=1 THEN 0 ELSE 1 END WHERE id = 1')
            conn.commit()
            conn.close()
            self._json({"status": "success"})

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("🚀 تم تشغيل منصة الجود وربطها بقاعدة بيانات SQLite (platform.db)")
    print(f"🔹 رابط المنصة للمستخدمين:  http://localhost:{PORT}")
    print(f"🔸 رابط لوحة الإشراف:      http://localhost:{PORT}/admi1/")
    print("=" * 60)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), FullPlatformServer) as httpd:
        httpd.serve_forever()