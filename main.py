import datetime
import http.server
import json
import socketserver

PORT = 8080

# -------------------------------------------------------------
# قاعدة بيانات المنصة الشاملة (Database Engine)
# -------------------------------------------------------------
platform_stats = {
    "total_volume": 4825900.0,
    "platform_revenue": 14250.0,
    "trading_status": True,
}

users_db = [
    {
        "id": "USR-101",
        "name": "أحمد الشمري",
        "email": "ahmed@example.com",
        "balance": 35000.0,
        "status": "نشط",
    },
    {
        "id": "USR-102",
        "name": "سارة القحطاني",
        "email": "sara.q@example.com",
        "balance": 18450.0,
        "status": "نشط",
    },
    {
        "id": "USR-103",
        "name": "محمود إبراهيم",
        "email": "m.ibrahim@example.com",
        "balance": 820.0,
        "status": "معلق",
    },
    {
        "id": "USR-104",
        "name": "خالد المنصور",
        "email": "khaled@example.com",
        "balance": 92400.0,
        "status": "نشط",
    },
]

portfolio = {
    "cash_balance": 35000.0,
    "assets": {
        "BTC": {"amount": 0.65, "avg_price": 63200.0},
        "ETH": {"amount": 5.20, "avg_price": 3100.0},
        "SOL": {"amount": 42.0, "avg_price": 140.0},
        "BNB": {"amount": 15.0, "avg_price": 575.0},
    },
    "history": [
        {
            "id": "TX-9011",
            "symbol": "BTC",
            "type": "BUY",
            "amount": 0.15,
            "price": 64100.0,
            "time": "2026-09-01 10:15",
        },
        {
            "id": "TX-9010",
            "symbol": "ETH",
            "type": "BUY",
            "amount": 2.50,
            "price": 3050.0,
            "time": "2026-08-31 18:40",
        },
    ],
}

withdraw_requests = [
    {
        "id": "REQ-7701",
        "user_id": "USR-101",
        "network": "USDT BEP20",
        "address": "0x71C...98B2",
        "amount": 2500.0,
        "time": "2026-09-01 03:20",
        "status": "معلق",
    },
    {
        "id": "REQ-7700",
        "user_id": "USR-104",
        "network": "USDT BEP20",
        "address": "0x34A...21F4",
        "amount": 12000.0,
        "time": "2026-08-31 22:10",
        "status": "مكتمل",
    },
]

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
            --admin-bg: #05070c;
            --admin-panel: #0d121d;
            --admin-card: rgba(19, 26, 41, 0.85);
            --admin-border: rgba(255, 255, 255, 0.08);
            --gold: #ffb703;
            --green: #00f29b;
            --red: #ff3366;
            --blue: #00d2ff;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { margin:0; padding:0; box-sizing:border-box; font-family:'Cairo', sans-serif; }
        body { background: var(--admin-bg); color: var(--text-main); display:flex; min-height:100vh; overflow-x:hidden; }

        /* الشريط الجانبي Sidebar */
        aside {
            width: 280px;
            background: var(--admin-panel);
            border-left: 1px solid var(--admin-border);
            display: flex;
            flex-direction: column;
            padding: 24px 16px;
            position: fixed;
            height: 100vh;
            right: 0;
            top: 0;
            z-index: 100;
        }

        .side-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--admin-border);
            margin-bottom: 24px;
        }

        .side-brand-icon {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, var(--gold), #fb8500);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-size: 1.4rem;
            box-shadow: 0 0 20px rgba(255, 183, 3, 0.35);
        }

        .side-nav {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex-grow: 1;
        }

        .side-link {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 16px;
            color: var(--text-sub);
            text-decoration: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .side-link:hover, .side-link.active {
            background: rgba(255, 183, 3, 0.12);
            color: var(--gold);
            border: 1px solid rgba(255, 183, 3, 0.25);
        }

        .side-link i { font-size: 1.1rem; width: 22px; text-align: center; }

        /* منطقة المحتوى الرئيسي */
        main {
            margin-right: 280px;
            flex-grow: 1;
            padding: 30px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        @media (max-width: 992px) {
            aside { display: none; }
            main { margin-right: 0; }
        }

        .top-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }

        .stat-card {
            background: var(--admin-card);
            border: 1px solid var(--admin-border);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        }

        .stat-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--stat-color, var(--gold));
        }

        .stat-label { font-size: 0.8rem; color: var(--text-sub); margin-bottom: 6px; }
        .stat-num { font-size: 1.8rem; font-weight: 900; font-family: var(--font-mono); color: #fff; }

        /* البطاقات والجداول */
        .content-card {
            background: var(--admin-card);
            border: 1px solid var(--admin-border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(12px);
        }

        .card-header-box {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--admin-border);
            padding-bottom: 12px;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th { text-align: right; padding: 12px; color: var(--text-sub); border-bottom: 1px solid var(--admin-border); font-weight: 600; }
        td { padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.02); font-family: var(--font-mono); }

        .badge-status {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: bold;
            font-family: 'Cairo';
        }
        .badge-pending { background: rgba(255, 183, 3, 0.15); color: var(--gold); }
        .badge-done { background: rgba(0, 242, 155, 0.15); color: var(--green); }
        .badge-reject { background: rgba(255, 51, 102, 0.15); color: var(--red); }

        .btn-table-action {
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.75rem;
            margin-left: 4px;
        }
        .btn-approve { background: var(--green); color: #000; }
        .btn-reject { background: rgba(255, 51, 102, 0.2); color: var(--red); border: 1px solid var(--red); }

        .input-admin {
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--admin-border);
            padding: 8px 12px;
            border-radius: 8px;
            color: #fff;
            outline: none;
            font-family: var(--font-mono);
        }

        .tab-section { display: none; }
        .tab-section.active { display: block; }
    </style>
</head>
<body>

    <!-- القائمة الجانبية -->
    <aside>
        <div class="side-brand">
            <div class="side-brand-icon"><i class="fa-solid fa-crown"></i></div>
            <div>
                <h2 style="font-size: 1.1rem; font-weight:900;">إدارة الجود</h2>
                <span style="font-size: 0.7rem; color:var(--gold); font-weight:700;">SUPER ADMIN ENGINE</span>
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

    <!-- مساحة الإدارة المركزية -->
    <main>

        <!-- 1. الإحصائيات والمؤشرات العلوية -->
        <div class="top-stats-grid">
            <div class="stat-card" style="--stat-color: var(--blue);">
                <div class="stat-label"><i class="fa-solid fa-users"></i> إجمالي المستخدمين</div>
                <div class="stat-num" id="adm-user-count">4</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--green);">
                <div class="stat-label"><i class="fa-solid fa-vault"></i> السيولة الكلية في النظام</div>
                <div class="stat-num" id="adm-total-liquidity">$146,650</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--gold);">
                <div class="stat-label"><i class="fa-solid fa-chart-line"></i> حجم التداول الإجمالي</div>
                <div class="stat-num" id="adm-total-volume">$4,825,900</div>
            </div>
            <div class="stat-card" style="--stat-color: var(--red);">
                <div class="stat-label"><i class="fa-solid fa-clock"></i> طلبات السحب المعلقة</div>
                <div class="stat-num" id="adm-pending-withdraws" style="color:var(--gold);">1</div>
            </div>
        </div>

        <!-- تبويب 1: النظرة العامة -->
        <div id="tab-overview" class="tab-section active">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-list-check" style="color:var(--blue);"></i> آخر العمليات المالية والصفقات بالموقع</div>
                    <span style="font-size:0.8rem; color:var(--green);">● النظام متصل ويحدث لحظياً</span>
                </div>
                <table>
                    <thead>
                        <tr><th>المعرف</th><th>العملة/الرمز</th><th>نوع العملية</th><th>الكمية</th><th>السعر</th><th>الوقت والتاريخ</th></tr>
                    </thead>
                    <tbody id="adm-overview-history"></tbody>
                </table>
            </div>
        </div>

        <!-- تبويب 2: طلبات السحب -->
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

        <!-- تبويب 3: إدارة العملاء -->
        <div id="tab-users" class="tab-section">
            <div class="content-card">
                <div class="card-header-box">
                    <div class="card-title"><i class="fa-solid fa-users-gear" style="color:var(--green);"></i> حسابات العملاء وشحن الأرصدة</div>
                </div>
                <table>
                    <thead>
                        <tr><th>المعرف</th><th>الاسم الكامل</th><th>البريد الإلكتروني</th><th>الرصيد الكاش</th><th>الحالة</th><th>تعديل الرصيد</th></tr>
                    </thead>
                    <tbody id="adm-users-tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- تبويب 4: تعديل الأسعار -->
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
            const res = await fetch('/api/admin/all-data');
            const data = await res.json();

            // تحديث الإحصائيات العلوية
            document.getElementById('adm-user-count').innerText = data.users.length;
            document.getElementById('adm-total-volume').innerText = '$' + data.stats.total_volume.toLocaleString();
            
            let totalCash = data.users.reduce((acc, u) => acc + u.balance, 0);
            document.getElementById('adm-total-liquidity').innerText = '$' + totalCash.toLocaleString();

            let pendingCount = data.withdraws.filter(w => w.status === 'معلق').length;
            document.getElementById('adm-pending-withdraws').innerText = pendingCount;

            // زر حالة النظام
            const btnEng = document.getElementById('btn-engine-toggle');
            if(data.stats.trading_status) {
                btnEng.innerText = 'إيقاف التداول طارئاً';
                btnEng.style.background = 'var(--red)';
            } else {
                btnEng.innerText = 'استئناف التداول';
                btnEng.style.background = 'var(--green)';
                btnEng.style.color = '#000';
            }

            // جدول السجل العام
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

            // جدول طلبات السحب
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

            // جدول المستخدمين
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

            // جدول تعديل الأسعار
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
        }

        async function handleWithdraw(reqId, action) {
            await fetch('/api/admin/action-withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ req_id: reqId, action: action })
            });
            alert('تم تحديث حالة طلب السحب بنجاح');
            loadAdminData();
        }

        async function adjustUserBalance(userId) {
            const val = parseFloat(document.getElementById('usr-adj-' + userId).value);
            if(!val) return alert('أدخل قيمة صحيحة للزيادة أو الخصم');
            await fetch('/api/admin/adjust-balance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: userId, amount: val })
            });
            alert('تم تعديل رصيد العميل بنجاح');
            loadAdminData();
        }

        async function saveNewPrice(sym) {
            const p = parseFloat(document.getElementById('adm-p-' + sym).value);
            if(!p || p <= 0) return alert('أدخل سعراً صحيحاً');
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

        loadAdminData();
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
        .chart-box { height: 480px; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-glass); margin-bottom: 15px; }
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
        
        /* نافذة السحب */
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
            <div class="panel-heading"><span><i class="fa-solid fa-chart-pie" style="color:var(--accent-gold)"></i> المحفظة</span></div>
            <div class="balance-card">
                <div style="font-size:0.8rem; color:var(--text-muted)">إجمالي رصيد الحساب</div>
                <div class="val" id="net-worth-display">$0.00</div>
                <div style="font-size:0.8rem; margin-top: 5px;">كاش متاح: <b id="cash-balance-display" style="color:var(--accent-green);">$0.00</b></div>
            </div>
            <div id="assets-container"></div>
        </div>

        <!-- الشارت -->
        <div>
            <div class="chart-box"><div id="tv_chart" style="height:100%;width:100%;"></div></div>
            <div class="glass-panel">
                <div class="panel-heading"><span><i class="fa-solid fa-clock-rotate-left"></i> سجل الصفقات</span></div>
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
                <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:15px;">تم استلام طلب السحب بنجاح عبر شبكة BEP20 ويتم مراجعته وتأكيده.</p>
                <button class="btn-withdraw-header" onclick="document.getElementById('withdraw-modal').style.display='none'; document.getElementById('w-form').style.display='block'; document.getElementById('w-success').style.display='none';">حسناً</button>
            </div>
        </div>
    </div>

    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
        let curSide = 'BUY';
        let curSym = 'BTC';
        let marketPrices = {};

        function initChart(sym) {
            document.getElementById('tv_chart').innerHTML = '';
            new TradingView.widget({
                "autosize": true, "symbol": `BINANCE:${sym}USDT`, "interval": "15",
                "theme": "dark", "style": "1", "container_id": "tv_chart", "locale": "ar_AE"
            });
        }

        function setSide(side) {
            curSide = side;
            document.getElementById('tab-buy').classList.toggle('active', side==='BUY');
            document.getElementById('tab-sell').classList.toggle('active', side==='SELL');
            const btn = document.getElementById('submit-order-btn');
            btn.className = 'btn-order-submit ' + (side==='BUY'?'buy':'sell');
            btn.innerText = side==='BUY'?'تنفيذ الشراء':'تنفيذ البيع';
        }

        function onSymChange() {
            curSym = document.getElementById('symbol-selector').value;
            initChart(curSym);
            calcTotal();
        }

        async function loadData() {
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
            if(d.status==='success') { document.getElementById('order-quantity').value = ''; loadData(); }
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

        initChart('BTC');
        loadData();
    </script>
</body>
</html>
"""


# -------------------------------------------------------------
# 3. محرك الخادم والـ API الموحد (Unified HTTP Handler)
# -------------------------------------------------------------
class FullPlatformServer(http.server.BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        # توجيه صفحة الإشراف
        if self.path == "/admi1" or self.path == "/admi1/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ADMIN_PAGE.encode("utf-8"))

        # توجيه منصة التداول الرئيسية
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TRADING_PAGE.encode("utf-8"))

        # API بيانات التداول للعميل
        elif self.path == "/api/data":
            total_assets = sum(
                info["amount"] * MARKET_PRICES.get(sym, info["avg_price"])
                for sym, info in portfolio["assets"].items()
            )
            self._json(
                {
                    "cash_balance": round(portfolio["cash_balance"], 2),
                    "total_net_worth": round(
                        portfolio["cash_balance"] + total_assets, 2
                    ),
                    "assets": portfolio["assets"],
                    "history": portfolio["history"],
                    "market_prices": MARKET_PRICES,
                }
            )

        # API بيانات لوحة التحكم الكاملة
        elif self.path == "/api/admin/all-data":
            self._json(
                {
                    "stats": platform_stats,
                    "users": users_db,
                    "withdraws": withdraw_requests,
                    "history": portfolio["history"],
                    "market_prices": MARKET_PRICES,
                }
            )
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = (
            json.loads(self.rfile.read(length).decode("utf-8"))
            if length > 0
            else {}
        )
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # 1. أوامر التداول
        if self.path == "/api/trade":
            if not platform_stats["trading_status"]:
                return self._json(
                    {
                        "status": "error",
                        "message": "عذراً! محرك التداول معطل مؤقتاً لأعمال الصيانة من الإدارة.",
                    }
                )

            sym = body.get("symbol", "BTC").upper()
            side = body.get("order_type")
            amt = float(body.get("amount", 0))
            price = MARKET_PRICES.get(sym, 100.0)
            cost = amt * price

            if side == "BUY":
                if portfolio["cash_balance"] < cost:
                    return self._json(
                        {
                            "status": "error",
                            "message": "رصيدك غير كافٍ لإتمام الصفقة!",
                        }
                    )
                portfolio["cash_balance"] -= cost
                if sym in portfolio["assets"]:
                    cur = portfolio["assets"][sym]
                    new_amt = cur["amount"] + amt
                    cur["avg_price"] = (
                        (cur["amount"] * cur["avg_price"]) + cost
                    ) / new_amt
                    cur["amount"] = round(new_amt, 4)
                else:
                    portfolio["assets"][sym] = {
                        "amount": round(amt, 4),
                        "avg_price": price,
                    }
            elif side == "SELL":
                if (
                    sym not in portfolio["assets"]
                    or portfolio["assets"][sym]["amount"] < amt
                ):
                    return self._json(
                        {
                            "status": "error",
                            "message": "لا تمتلك كمية كافية من العملة للبيع!",
                        }
                    )
                portfolio["cash_balance"] += cost
                portfolio["assets"][sym]["amount"] -= amt
                if portfolio["assets"][sym]["amount"] <= 0.0001:
                    del portfolio["assets"][sym]

            platform_stats["total_volume"] += cost
            portfolio["history"].insert(
                0,
                {
                    "id": f"TX-{len(portfolio['history'])+9020}",
                    "symbol": sym,
                    "type": side,
                    "amount": amt,
                    "price": price,
                    "time": now_str,
                },
            )
            self._json(
                {
                    "status": "success",
                    "message": f"تم تنفيذ عملية الـ {side} بنجاح!",
                }
            )

        # 2. طلبات سحب الأرباح
        elif self.path == "/api/withdraw":
            addr = body.get("address")
            amt = float(body.get("amount", 0))
            if portfolio["cash_balance"] < amt:
                return self._json(
                    {
                        "status": "error",
                        "message": "رصيدك المتاح أقل من المبلغ المطلوب سحبه!",
                    }
                )

            portfolio["cash_balance"] -= amt
            req_id = f"REQ-{len(withdraw_requests) + 7701}"
            withdraw_requests.insert(
                0,
                {
                    "id": req_id,
                    "user_id": "USR-101",
                    "network": "USDT BEP20",
                    "address": addr,
                    "amount": amt,
                    "time": now_str,
                    "status": "معلق",
                },
            )
            portfolio["history"].insert(
                0,
                {
                    "id": f"TX-{len(portfolio['history'])+9020}",
                    "symbol": "USDT BEP20",
                    "type": "WITHDRAW",
                    "amount": amt,
                    "price": 1.0,
                    "time": now_str,
                },
            )
            self._json({"status": "success"})

        # 3. إجراءات الإدارة: قبول أو رفض السحب
        elif self.path == "/api/admin/action-withdraw":
            req_id = body.get("req_id")
            action = body.get("action")
            for req in withdraw_requests:
                if req["id"] == req_id:
                    req["status"] = (
                        "مكتمل" if action == "APPROVE" else "مرفوض"
                    )
                    if action == "REJECT":
                        portfolio["cash_balance"] += req["amount"]
                    break
            self._json({"status": "success"})

        # 4. إجراءات الإدارة: تعديل رصيد مستخدم
        elif self.path == "/api/admin/adjust-balance":
            uid = body.get("user_id")
            amt = float(body.get("amount", 0))
            for u in users_db:
                if u["id"] == uid:
                    u["balance"] += amt
                    if uid == "USR-101":
                        portfolio["cash_balance"] += amt
                    break
            self._json({"status": "success"})

        # 5. إجراءات الإدارة: ضبط الأسعار
        elif self.path == "/api/admin/set-price":
            sym = body.get("symbol")
            price = float(body.get("price"))
            MARKET_PRICES[sym] = price
            self._json({"status": "success"})

        # 6. إجراءات الإدارة: مفتاح طوارئ السوق
        elif self.path == "/api/admin/toggle-engine":
            platform_stats["trading_status"] = not platform_stats[
                "trading_status"
            ]
            self._json({"status": "success"})


if __name__ == "__main__":
    print("=" * 55)
    print("🚀 تم تشغيل منصة الجود للتداول ولوحة التحكم بنجاح!")
    print(f"🔹 منصة التداول للمستخدمين: http://localhost:{PORT}")
    print(f"🔸 لوحة الإشراف الشاملة:   http://localhost:{PORT}/admi1/")
    print("=" * 55)
    with socketserver.TCPServer(("", PORT), FullPlatformServer) as httpd:
        httpd.serve_forever()