from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

PORT = 8000
DATA_FILE = "data.jshon"

PAGE_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم والإدارة الشاملة | SYRIA CARD</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg: #0b111e;
            --sidebar-bg: #0d1527;
            --surface: rgba(18, 26, 43, 0.85);
            --box-bg: #152238;
            --border: rgba(255, 255, 255, 0.08);
            --primary: #38bdf8;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --text-main: #f3f4f6;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        
        body {
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
        }

        .btn-menu-trigger {
            background: #1e293b;
            color: var(--primary);
            border: 1px solid var(--border);
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: 0.2s;
        }
        .btn-menu-trigger:hover {
            background: #334155;
            color: #fff;
        }

        .sidebar {
            width: 280px;
            background: var(--sidebar-bg);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0; bottom: 0; right: 0;
            z-index: 2000;
            transition: transform 0.3s ease-in-out;
        }

        .sidebar-brand {
            padding: 25px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--primary);
            font-size: 18px;
            font-weight: 900;
        }

        .close-sidebar-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 18px;
            cursor: pointer;
            padding: 4px;
        }
        .close-sidebar-btn:hover { color: var(--danger); }

        .sidebar-menu {
            list-style: none;
            padding: 20px 10px;
            overflow-y: auto;
            flex: 1;
        }

        .sidebar-menu li {
            padding: 12px 18px;
            border-radius: 10px;
            margin-bottom: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 700;
            color: var(--text-muted);
            transition: 0.2s;
        }

        .sidebar-menu li:hover, .sidebar-menu li.active {
            background: rgba(56, 189, 248, 0.12);
            color: var(--primary);
        }

        .sidebar-menu li i { font-size: 16px; width: 20px; text-align: center; }

        .sidebar-backdrop {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
            z-index: 1500;
            display: none;
        }
        .sidebar-backdrop.active { display: block; }

        .main-content {
            margin-right: 280px;
            flex: 1;
            padding: 30px 40px;
            max-width: calc(100% - 280px);
            transition: 0.3s;
        }

        @media (max-width: 992px) {
            .sidebar { transform: translateX(100%); }
            .sidebar.open { transform: translateX(0); }
            .main-content { margin-right: 0; max-width: 100%; padding: 20px 15px; }
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface);
            padding: 18px 25px;
            border-radius: 16px;
            border: 1px solid var(--border);
            margin-bottom: 25px;
            gap: 15px;
            flex-wrap: wrap;
        }

        .header h1 { font-size: 20px; font-weight: 900; color: var(--primary); }

        .btn-save-json {
            background: #10b981;
            color: #fff;
            padding: 10px 18px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-weight: 800;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: 0.2s;
        }
        .btn-save-json:hover { background: #059669; }

        .upload-card {
            background: var(--surface);
            border: 2px dashed rgba(56, 189, 248, 0.3);
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            margin-bottom: 25px;
            cursor: pointer;
        }

        .upload-btn {
            background: var(--primary);
            color: #04121d;
            font-weight: 800;
            padding: 10px 25px;
            border-radius: 8px;
            display: inline-block;
            margin-top: 12px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
        }

        .stat-card h3 { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
        .stat-card p { font-size: 24px; font-weight: 900; color: #fff; }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .table-container {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow-x: auto;
        }

        table { width: 100%; border-collapse: collapse; text-align: right; font-size: 13px; }
        th, td { padding: 15px 20px; border-bottom: 1px solid var(--border); white-space: nowrap; }
        th { background: #111a2e; color: var(--primary); font-weight: 700; }
        tbody tr { cursor: pointer; transition: 0.2s; }
        tbody tr:hover { background: rgba(56, 189, 248, 0.05); }

        .badge {
            padding: 4px 12px; border-radius: 15px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 5px;
        }
        .badge-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }
        .badge-danger { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; }
        .badge-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; }
        code { background: rgba(255, 255, 255, 0.06); padding: 2px 6px; border-radius: 4px; color: var(--primary); font-family: monospace; }

        .admin-box {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
        }

        .admin-box h2 { font-size: 17px; color: var(--primary); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }

        .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 220px; display: flex; flex-direction: column; gap: 6px; }
        .form-group label { font-size: 13px; color: var(--text-muted); font-weight: 600; }
        .form-control {
            background: var(--box-bg);
            border: 1px solid var(--border);
            color: #fff;
            padding: 10px 15px;
            border-radius: 8px;
            outline: none;
            font-size: 14px;
        }
        .form-control:focus { border-color: var(--primary); }

        .btn-action {
            background: var(--primary);
            color: #04121d;
            font-weight: 800;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            align-self: flex-end;
        }

        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(4, 7, 15, 0.85); backdrop-filter: blur(8px);
            display: none; justify-content: center; align-items: center; z-index: 9999; padding: 20px;
        }
        .modal-card {
            background: #0e1726; border: 1px solid var(--primary); box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9);
            width: 100%; max-width: 900px; border-radius: 20px; overflow: hidden;
        }
        .order-topbar {
            display: flex; justify-content: space-between; align-items: center; padding: 20px 30px;
            border-bottom: 1px solid var(--border); background: #131d31;
        }
        .order-content-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 25px 30px;
        }
        @media (max-width: 768px) { .order-content-grid { grid-template-columns: 1fr; } }
        .section-box { background: var(--box-bg); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
        .info-row { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px; }
        .info-row:last-child { margin-bottom: 0; }
        .info-row .fn { color: var(--text-muted); }
        .info-row .fv { color: #fff; font-weight: 700; }
        .input-display {
            background: #0d1524; border: 1px solid var(--border); padding: 10px 14px; border-radius: 8px;
            display: flex; justify-content: space-between; align-items: center; color: var(--primary); font-family: monospace; font-size: 13px; margin-bottom: 12px;
        }
        .response-terminal {
            background: #090e18; border: 1px solid var(--border); padding: 12px; border-radius: 8px;
            font-family: 'Courier New', monospace; font-size: 12px; color: #34d399; line-height: 1.5; white-space: pre-wrap;
        }
        .modal-footer { padding: 15px 30px; background: #111a2e; display: flex; justify-content: flex-end; }
        .close-btn { background: #1e293b; color: #fff; padding: 6px 20px; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; }
    </style>
</head>
<body>

<div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeSidebar()"></div>

<div class="sidebar" id="sidebar">
    <div class="sidebar-brand">
        <span><i class="fa-solid fa-bolt"></i> SYRIA CARD</span>
        <button class="close-sidebar-btn" onclick="closeSidebar()"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <ul class="sidebar-menu">
        <li class="active" onclick="switchTab('ordersTab', this)"><i class="fa-solid fa-list-check"></i> متابعة الطلبات</li>
        <li onclick="switchTab('productsTab', this)"><i class="fa-solid fa-box-archive"></i> إدارة المنتجات</li>
        <li onclick="switchTab('usersTab', this)"><i class="fa-solid fa-users-gear"></i> إدارة المستخدمين</li>
        <li onclick="switchTab('apiTab', this)"><i class="fa-solid fa-network-wired"></i> إعدادات الـ API</li>
        <li onclick="switchTab('settingsTab', this)"><i class="fa-solid fa-sliders"></i> إعدادات البوت والاشتراك</li>
        <li onclick="switchTab('depositsTab', this)"><i class="fa-solid fa-wallet"></i> طرق الإيداع</li>
    </ul>
</div>

<div class="main-content">
    <div class="header">
        <div style="display: flex; align-items: center; gap: 12px;">
            <button class="btn-menu-trigger" onclick="toggleSidebar()">
                <i class="fa-solid fa-bars"></i>
                <span>القائمة</span>
            </button>
            <h1 id="pageTitle">متابعة الطلبات</h1>
        </div>
        <div style="display: flex; gap: 10px;">
            <button class="btn-save-json" onclick="saveDataToServer()"><i class="fa-solid fa-cloud-arrow-up"></i> حفظ التعديلات بالسيرفر</button>
            <button class="btn-save-json" style="background:#0284c7;" onclick="exportUpdatedJson()"><i class="fa-solid fa-download"></i> تحميل نسخة</button>
        </div>
    </div>

    <div class="upload-card" onclick="document.getElementById('fileInput').click()">
        <h3><i class="fa-solid fa-file-arrow-up"></i> اضغط هنا لرفع ملف data.jshon جديد إلى السيرفر</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin-top: 5px;">يتم حفظه مباشرة على الجهاز ويحل محل القديم دائماً</p>
        <input type="file" id="fileInput" accept=".json,.jshon" style="display: none;" onchange="uploadFileToServer(event)">
        <span class="upload-btn"><i class="fa-solid fa-upload"></i> رفع واستبدال الملف</span>
    </div>

    <div class="stats-grid" id="statsArea" style="display: none;">
        <div class="stat-card"><h3>إجمالي الطلبات</h3><p id="stTotalOrders">0</p></div>
        <div class="stat-card"><h3>إجمالي المستخدمين</h3><p id="stTotalUsers">0</p></div>
        <div class="stat-card"><h3>إجمالي الإيداعات</h3><p id="stTotalDeposits">0</p></div>
        <div class="stat-card"><h3>أرصدة العملاء</h3><p id="stTotalBalances">$0.00</p></div>
    </div>

    <!-- تبويب 1: الطلبات -->
    <div id="ordersTab" class="tab-content active">
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <input type="text" id="searchInput" class="form-control" style="flex:1;" placeholder="بحث برقم الطلب، الآيدي، الكود، المنتج..." onkeyup="liveFilter()">
            <select id="statusSelect" class="form-control" style="width: 200px;" onchange="liveFilter()">
                <option value="all">كل الحالات</option>
                <option value="مقبول">المقبولة</option>
                <option value="مرفوض">المرفوضة</option>
                <option value="قيد المعالجة">قيد المعالجة</option>
            </select>
        </div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>رقم الطلب</th>
                        <th>آيدي المستخدم</th>
                        <th>المنتج</th>
                        <th>الفئة</th>
                        <th>المدخلات</th>
                        <th>السعر</th>
                        <th>الحالة</th>
                        <th>التاريخ</th>
                    </tr>
                </thead>
                <tbody id="ordersBody">
                    <tr><td colspan="8" style="text-align:center; color:var(--text-muted);">جاري تحميل البيانات من السيرفر...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- تبويب 2: المنتجات والأقسام -->
    <div id="productsTab" class="tab-content">
        <div class="admin-box">
            <h2><i class="fa-solid fa-layer-group"></i> الأقسام والمنتجات الحالية</h2>
            <div id="sectionsDisplay">لا توجد أقسام مسجلة.</div>
        </div>
        <div class="admin-box">
            <h2><i class="fa-solid fa-plus"></i> إضافة قسم جديد</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>اسم القسم:</label>
                    <input type="text" id="newSectionName" class="form-control" placeholder="مثلاً: شدات ببجي">
                </div>
                <div class="form-group">
                    <label>آيدي الإيموجي:</label>
                    <input type="text" id="newSectionEmoji" class="form-control" placeholder="4970134999584999825">
                </div>
                <button class="btn-action" onclick="addNewSection()"><i class="fa-solid fa-check"></i> حفظ القسم</button>
            </div>
        </div>
    </div>

    <!-- تبويب 3: المستخدمين -->
    <div id="usersTab" class="tab-content">
        <div class="admin-box">
            <h2><i class="fa-solid fa-coins"></i> شحن / خصم رصيد عميل</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>آيدي المستخدم:</label>
                    <input type="text" id="chargeUserId" class="form-control" placeholder="مثلاً: 123456789">
                </div>
                <div class="form-group">
                    <label>المبلغ ($):</label>
                    <input type="number" id="chargeAmount" step="0.01" class="form-control" placeholder="5.00">
                </div>
                <button class="btn-action" style="background:#10b981;" onclick="modifyBalance('add')"><i class="fa-solid fa-plus"></i> شحن رصيد</button>
                <button class="btn-action" style="background:#ef4444;" onclick="modifyBalance('deduct')"><i class="fa-solid fa-minus"></i> خصم رصيد</button>
            </div>
        </div>

        <div class="admin-box">
            <h2><i class="fa-solid fa-user-slash"></i> إدارة الحظر</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>آيدي العميل:</label>
                    <input type="text" id="banUserId" class="form-control" placeholder="آيدي المستخدم...">
                </div>
                <button class="btn-action" style="background:#ef4444;" onclick="toggleBan('ban')"><i class="fa-solid fa-ban"></i> حظر</button>
                <button class="btn-action" style="background:#10b981;" onclick="toggleBan('unban')"><i class="fa-solid fa-lock-open"></i> فك الحظر</button>
            </div>
        </div>
    </div>

    <!-- تبويب 4: إعدادات API -->
    <div id="apiTab" class="tab-content">
        <div class="admin-box">
            <h2><i class="fa-solid fa-chart-line"></i> نسبة ربح المنتجات المرتبطة بـ API</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>نسبة الربح المئوية (%):</label>
                    <input type="number" id="profitPercentageInput" class="form-control" placeholder="مثلاً: 10">
                </div>
                <button class="btn-action" onclick="updateProfit()"><i class="fa-solid fa-check"></i> تحديث النسبة</button>
            </div>
        </div>
    </div>

    <!-- تبويب 5: إعدادات البوت والاشتراك -->
    <div id="settingsTab" class="tab-content">
        <div class="admin-box">
            <h2><i class="fa-solid fa-bullhorn"></i> إعدادات الروابط والاشتراك الإجباري</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>قناة الاشتراك الإجباري (مع @):</label>
                    <input type="text" id="botChannelInput" class="form-control" placeholder="@SyriaCardbotS">
                </div>
                <div class="form-group">
                    <label>رابط قناة الأخبار:</label>
                    <input type="text" id="botNewsInput" class="form-control" placeholder="https://t.me/...">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>رابط الدعم الفني:</label>
                    <input type="text" id="botSupportInput" class="form-control" placeholder="https://t.me/...">
                </div>
            </div>
            <button class="btn-action" onclick="updateGeneralSettings()"><i class="fa-solid fa-check"></i> حفظ الروابط</button>
        </div>

        <div class="admin-box">
            <h2><i class="fa-solid fa-message"></i> رسالة الترحيب</h2>
            <div class="form-group" style="margin-bottom: 15px;">
                <label>نص الترحيب في البوت (يدعم HTML):</label>
                <textarea id="welcomeTextInput" class="form-control" rows="4"></textarea>
            </div>
            <button class="btn-action" onclick="updateWelcomeText()"><i class="fa-solid fa-check"></i> حفظ رسالة الترحيب</button>
        </div>
    </div>

    <!-- تبويب 6: طرق الإيداع -->
    <div id="depositsTab" class="tab-content">
        <div class="admin-box">
            <h2><i class="fa-solid fa-money-check-dollar"></i> طرق الإيداع الحالية</h2>
            <div id="depositsListDisplay">لا توجد طرق إيداع مضافة.</div>
        </div>
    </div>
</div>

<div class="modal-overlay" id="orderModal" onclick="closeModal(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
        <div class="order-topbar">
            <div>
                <span style="color:var(--text-muted);font-size:13px;">المنتج:</span>
                <span id="mProduct" style="font-weight:800;color:#fff;font-size:16px;">---</span>
            </div>
            <div>
                <span style="color:var(--text-muted);font-size:13px;">الآيدي:</span>
                <span id="mUserId" style="color:var(--primary);font-weight:800;font-size:16px;">---</span>
            </div>
            <div id="mStatusBadge">---</div>
        </div>
        <div class="order-content-grid">
            <div class="section-box">
                <div style="font-weight:800;color:var(--primary);margin-bottom:15px;"><i class="fa-solid fa-cube"></i> تفاصيل الطلب</div>
                <div class="info-row"><span class="fn">رقم الطلب:</span><span class="fv" id="mOrderNum">---</span></div>
                <div class="info-row"><span class="fn">الفئة:</span><span class="fv" id="mCategory">---</span></div>
                <div class="info-row"><span class="fn">السعر:</span><span class="fv" id="mPrice" style="color:#10b981;">$0</span></div>
                <div class="info-row"><span class="fn">التاريخ:</span><span class="fv" id="mDate">---</span></div>
            </div>
            <div class="section-box">
                <div style="font-weight:800;color:var(--primary);margin-bottom:15px;"><i class="fa-solid fa-circle-info"></i> المدخلات والرد</div>
                <div class="input-display">
                    <span id="mPlayerId">---</span>
                    <button style="background:none;border:none;color:#fff;cursor:pointer;" onclick="copyText('mPlayerId')"><i class="fa-regular fa-copy"></i></button>
                </div>
                <div class="response-terminal" id="mResponseTerminal">
: Activation Success
Status : Completed / Verified
ID     : <span id="mPlayerIdSub">---</span>
Code   : <span id="mCodeSub">---</span>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="close-btn" onclick="document.getElementById('orderModal').style.display='none'">إغلاق</button>
        </div>
    </div>
</div>

<script>
    let botData = null;
    let globalOrders = [];

    // تحميل البيانات من السيرفر مباشرة عند الفتح
    document.addEventListener("DOMContentLoaded", function() {
        fetchDataFromServer();
    });

    function fetchDataFromServer() {
        fetch('/get-data')
            .then(res => res.json())
            .then(data => {
                if (data && Object.keys(data).length > 0) {
                    botData = data;
                    renderAllData();
                } else {
                    document.getElementById('ordersBody').innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">الملف فارغ أو لم يتم رفعه بعد</td></tr>';
                }
            })
            .catch(err => {
                document.getElementById('ordersBody').innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--danger);">فشل جلب البيانات من السيرفر</td></tr>';
            });
    }

    // رفع ملف جديد ليحل محل القديم بالسيرفر
    function uploadFileToServer(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const parsed = JSON.parse(e.target.result);
                // إرسال كـ POST ليحفظه السيرفر بالملف الأساسي
                fetch('/save-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(parsed)
                })
                .then(res => res.text())
                .then(msg => {
                    botData = parsed;
                    renderAllData();
                    alert("تم حفظ الملف الجديد بالسيرفر بنجاح واستبدال القديم!");
                })
                .catch(err => alert("حدث خطأ أثناء الحفظ بالسيرفر"));
            } catch (err) {
                alert("الملف غير صالح! تأكد أنه بصيغة JSON صحيحة.");
            }
        };
        reader.readAsText(file);
    }

    // حفظ أي تعديل تجريه من اللوحة مباشرة إلى ملف السيرفر
    function saveDataToServer() {
        if (!botData) return alert("لا توجد بيانات لحفظها");
        fetch('/save-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(botData)
        })
        .then(res => res.text())
        .then(msg => alert("تم حفظ كل التعديلات داخل ملف السيرفر data.jshon مباشرة!"))
        .catch(err => alert("خطأ في الحفظ بالسيرفر"));
    }

    function toggleSidebar() {
        const sb = document.getElementById('sidebar');
        const bd = document.getElementById('sidebarBackdrop');
        sb.classList.toggle('open');
        bd.classList.toggle('active');
    }

    function closeSidebar() {
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('sidebarBackdrop').classList.remove('active');
    }

    function switchTab(tabId, element) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.sidebar-menu li').forEach(el => el.classList.remove('active'));
        
        document.getElementById(tabId).classList.add('active');
        if(element) element.classList.add('active');
        document.getElementById('pageTitle').innerText = element ? element.innerText.trim() : 'لوحة التحكم';

        if(window.innerWidth <= 992) {
            closeSidebar();
        }
    }

    function renderAllData() {
        if (!botData) return;

        const users = botData.users || {};
        const stats = botData.statistics || {};
        const userOrders = botData.user_orders || {};

        let totalBalances = 0;
        for (let u in users) {
            totalBalances += parseFloat(users[u].balance || 0);
        }

        document.getElementById('stTotalOrders').innerText = stats.total_orders || 0;
        document.getElementById('stTotalUsers').innerText = Object.keys(users).length;
        document.getElementById('stTotalDeposits').innerText = stats.total_deposits || 0;
        document.getElementById('stTotalBalances').innerText = '$' + totalBalances.toFixed(2);
        document.getElementById('statsArea').style.display = 'grid';

        document.getElementById('profitPercentageInput').value = botData.profit_percentage || 0;
        document.getElementById('botChannelInput').value = botData.required_channel || '';
        document.getElementById('botNewsInput').value = botData.bot_news_link || '';
        document.getElementById('botSupportInput').value = botData.bot_support_link || '';
        document.getElementById('welcomeTextInput').value = botData.welcome_text || '';

        // استخراج جميع الطلبات
        globalOrders = [];
        for (let uid in userOrders) {
            let ordersList = userOrders[uid];
            if (Array.isArray(ordersList)) {
                ordersList.forEach(o => {
                    let item = Object.assign({}, o);
                    item.user_id = uid;
                    if (!item.status || item.status.trim() === "") {
                        item.status = "قيد المعالجة";
                    }
                    globalOrders.push(item);
                });
            }
        }

        globalOrders.sort((a, b) => {
            let dateA = a.date ? String(a.date) : "";
            let dateB = b.date ? String(b.date) : "";
            return dateB.localeCompare(dateA);
        });

        const tbody = document.getElementById('ordersBody');
        tbody.innerHTML = '';

        if (globalOrders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">لا توجد أي طلبات مسجلة</td></tr>';
            return;
        }

        globalOrders.forEach((o, index) => {
            let status = (o.status || 'قيد المعالجة').trim();
            let badgeClass = 'badge-warning';
            let statusIcon = '<i class="fa-solid fa-clock"></i>';

            if (status === 'مقبول') {
                badgeClass = 'badge-success';
                statusIcon = '<i class="fa-solid fa-check"></i>';
            } else if (status === 'مرفوض') {
                badgeClass = 'badge-danger';
                statusIcon = '<i class="fa-solid fa-xmark"></i>';
            } else {
                badgeClass = 'badge-warning';
                statusIcon = '<i class="fa-solid fa-hourglass-half"></i>';
            }

            let tr = document.createElement('tr');
            tr.setAttribute('data-status', status);
            tr.setAttribute('onclick', 'openOrderModal(' + index + ')');
            tr.innerHTML = `
                <td><code>${o.order_number || '---'}</code></td>
                <td><code>${o.user_id || '---'}</code></td>
                <td><strong>${o.product_name || '---'}</strong></td>
                <td>${o.category_name || '---'}</td>
                <td><code>${o.player_id || '---'}</code></td>
                <td><strong style="color: #10b981;">$${o.price || 0}</strong></td>
                <td><span class="badge ${badgeClass}">${statusIcon} ${status}</span></td>
                <td style="color: #94a3b8; font-size: 12px;">${o.date || '---'}</td>
            `;
            tbody.appendChild(tr);
        });

        renderSections();
        renderDeposits();
    }

    function renderSections() {
        const sections = botData.sections || [];
        const box = document.getElementById('sectionsDisplay');
        if(sections.length === 0) {
            box.innerHTML = "لا يوجد أي أقسام مسجلة حالياً.";
            return;
        }
        let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:15px;">';
        sections.forEach((s, idx) => {
            let prodCount = (s.products || []).length;
            html += `
                <div style="background:var(--box-bg);padding:15px;border-radius:10px;border:1px solid var(--border);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong>${s.name}</strong>
                        <button style="background:none;border:none;color:#ef4444;cursor:pointer;" onclick="deleteSection(${idx})"><i class="fa-solid fa-trash"></i></button>
                    </div>
                    <p style="color:var(--text-muted);font-size:12px;margin-top:6px;">المنتجات: ${prodCount}</p>
                </div>
            `;
        });
        html += '</div>';
        box.innerHTML = html;
    }

    function deleteSection(idx) {
        if(confirm("هل أنت متأكد من حذف هذا القسم؟")) {
            botData.sections.splice(idx, 1);
            renderSections();
            saveDataToServer();
        }
    }

    function addNewSection() {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        let name = document.getElementById('newSectionName').value.trim();
        let emoji = document.getElementById('newSectionEmoji').value.trim() || "4970134999584999825";
        if(!name) return alert("اكتب اسم القسم");

        if(!botData.sections) botData.sections = [];
        botData.sections.push({ name: name, emoji_id: emoji, sub_categories: [], products: [] });
        document.getElementById('newSectionName').value = '';
        renderSections();
        saveDataToServer();
    }

    function renderDeposits() {
        const deps = botData.deposit_methods || [];
        const box = document.getElementById('depositsListDisplay');
        if(deps.length === 0) {
            box.innerHTML = "لا توجد طرق إيداع مضافة.";
            return;
        }
        let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:15px;">';
        deps.forEach((d, idx) => {
            html += `
                <div style="background:var(--box-bg);padding:15px;border-radius:10px;border:1px solid var(--border);">
                    <strong>${d.name}</strong>
                    <p style="color:var(--text-muted);font-size:12px;margin-top:4px;">العنوان: ${d.address || '---'}</p>
                    <p style="color:#10b981;font-size:12px;">الصرف: ${d.rate || '1'}</p>
                </div>
            `;
        });
        html += '</div>';
        box.innerHTML = html;
    }

    function modifyBalance(type) {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        let uid = document.getElementById('chargeUserId').value.trim();
        let amount = parseFloat(document.getElementById('chargeAmount').value);

        if(!uid || isNaN(amount) || amount <= 0) return alert("أدخل آيدي ومبلغ صحيح");

        if(!botData.users) botData.users = {};
        if(!botData.users[uid]) botData.users[uid] = { balance: 0, vip: "عادي", whatsapp_phone: "" };

        let cur = parseFloat(botData.users[uid].balance || 0);
        if(type === 'add') {
            botData.users[uid].balance = cur + amount;
        } else {
            if(cur < amount) return alert("رصيد العميل غير كافي للخصم");
            botData.users[uid].balance = cur - amount;
        }
        renderAllData();
        saveDataToServer();
    }

    function toggleBan(type) {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        let uid = parseInt(document.getElementById('banUserId').value.trim());
        if(!uid) return alert("أدخل آيدي العميل");

        if(!botData.banned_users) botData.banned_users = [];
        let idx = botData.banned_users.indexOf(uid);

        if(type === 'ban') {
            if(idx === -1) botData.banned_users.push(uid);
        } else {
            if(idx !== -1) botData.banned_users.splice(idx, 1);
        }
        saveDataToServer();
    }

    function updateProfit() {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        let p = parseFloat(document.getElementById('profitPercentageInput').value);
        botData.profit_percentage = isNaN(p) ? 0 : p;
        saveDataToServer();
    }

    function updateGeneralSettings() {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        botData.required_channel = document.getElementById('botChannelInput').value.trim();
        botData.bot_news_link = document.getElementById('botNewsInput').value.trim();
        botData.bot_support_link = document.getElementById('botSupportInput').value.trim();
        saveDataToServer();
    }

    function updateWelcomeText() {
        if (!botData) return alert("يرجى فتح ملف data.jshon أولاً");
        botData.welcome_text = document.getElementById('welcomeTextInput').value;
        saveDataToServer();
    }

    function exportUpdatedJson() {
        if (!botData) return alert("لا يوجد ملف مفتوح لتصديره");
        const str = JSON.stringify(botData, null, 2);
        const blob = new Blob([str], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "data.jshon";
        a.click();
        URL.revokeObjectURL(url);
    }

    function liveFilter() {
        let input = document.getElementById("searchInput").value.toLowerCase();
        let status = document.getElementById("statusSelect").value;
        let rows = document.querySelectorAll("#ordersBody tr");

        rows.forEach(row => {
            let text = row.innerText.toLowerCase();
            let rowStatus = row.getAttribute("data-status");
            let matchesSearch = text.includes(input);
            let matchesStatus = (status === "all") || (rowStatus === status);
            row.style.display = (matchesSearch && matchesStatus) ? "" : "none";
        });
    }

    function openOrderModal(index) {
        let data = globalOrders[index];
        if (!data) return;

        document.getElementById('mProduct').innerText = data.product_name || '---';
        document.getElementById('mUserId').innerText = data.user_id || '---';
        document.getElementById('mOrderNum').innerText = data.order_number || '---';
        document.getElementById('mCategory').innerText = data.category_name || '---';
        document.getElementById('mPrice').innerText = '$' + (data.price || 0);
        document.getElementById('mDate').innerText = data.date || '---';

        document.getElementById('mPlayerId').innerText = data.player_id || '---';
        document.getElementById('mPlayerIdSub').innerText = data.player_id || '---';
        document.getElementById('mCodeSub').innerText = (data.player_id && data.player_id.length > 8) ? data.player_id : 'SR-' + (data.order_number || 'OK');

        let status = data.status || 'قيد المعالجة';
        let badgeHtml = '';
        if(status === 'مقبول') {
            badgeHtml = '<span class="badge badge-success"><i class="fa-solid fa-check"></i> تم بنجاح</span>';
        } else if(status === 'مرفوض') {
            badgeHtml = '<span class="badge badge-danger"><i class="fa-solid fa-xmark"></i> مرفوض</span>';
        } else {
            badgeHtml = '<span class="badge badge-warning"><i class="fa-solid fa-hourglass-half"></i> قيد المعالجة</span>';
        }
        document.getElementById('mStatusBadge').innerHTML = badgeHtml;
        document.getElementById('orderModal').style.display = 'flex';
    }

    function closeModal(e) {
        if(e.target.id === 'orderModal') document.getElementById('orderModal').style.display = 'none';
    }

    function copyText(id) {
        let text = document.getElementById(id).innerText;
        navigator.clipboard.writeText(text);
        alert('تم النسخ: ' + text);
    }
</script>
</body>
</html>
"""

class BotServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b"{}")
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGE_HTML.encode('utf-8'))

    def do_POST(self):
        if self.path == '/save-data':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("OK".encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGE_HTML.encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), BotServer)
    print(f"🚀 السيرفر يعمل الآن بحفظ حقيقي على ملف {DATA_FILE} عبر المنفذ {PORT}...")
    server.serve_forever()