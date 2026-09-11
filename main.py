from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import uuid

PORT = 8000
DATA_FILE = "data.jshon"

API_BASE = "https://api.tartousi-store1.com/client/api"
API_TOKEN = "hwooO_oNPFMF0Uw_sPwIs2YIG_MH2qoQiKdHFt76_AfBaxmzq1fdPcolzadwS43s"

PAGE_HTML = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SYRIA CARD - لوحة التحكم</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{--bg:#0b111e;--sidebar-bg:#0d1527;--surface:rgba(18,26,43,.85);--box-bg:#152238;--border:rgba(255,255,255,.08);--primary:#38bdf8;--success:#10b981;--danger:#ef4444;--warning:#f59e0b;--text-main:#f3f4f6;--text-muted:#94a3b8}
*{box-sizing:border-box;margin:0;padding:0;font-family:'Cairo',sans-serif}
body{background-color:var(--bg);color:var(--text-main);min-height:100vh;display:flex}
.btn-menu-trigger{background:#1e293b;color:var(--primary);border:1px solid var(--border);padding:8px 15px;border-radius:8px;font-size:14px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;gap:8px}
.btn-menu-trigger:hover{background:#334155;color:#fff}
.sidebar{width:280px;background:var(--sidebar-bg);border-left:1px solid var(--border);display:flex;flex-direction:column;position:fixed;top:0;bottom:0;right:0;z-index:2000;transition:transform .3s}
.sidebar-brand{padding:25px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;color:var(--primary);font-size:18px;font-weight:900}
.close-sidebar-btn{background:none;border:none;color:var(--text-muted);font-size:18px;cursor:pointer}
.sidebar-menu{list-style:none;padding:20px 10px;overflow-y:auto;flex:1}
.sidebar-menu li{padding:12px 18px;border-radius:10px;margin-bottom:8px;cursor:pointer;display:flex;align-items:center;gap:12px;font-size:14px;font-weight:700;color:var(--text-muted);transition:.2s}
.sidebar-menu li:hover,.sidebar-menu li.active{background:rgba(56,189,248,.12);color:var(--primary)}
.sidebar-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);z-index:1500;display:none}
.sidebar-backdrop.active{display:block}
.main-content{margin-right:280px;flex:1;padding:30px 40px;max-width:calc(100% - 280px)}
@media(max-width:992px){.sidebar{transform:translateX(100%)}.sidebar.open{transform:translateX(0)}.main-content{margin-right:0;max-width:100%;padding:20px 15px}}
.header{display:flex;justify-content:space-between;align-items:center;background:var(--surface);padding:18px 25px;border-radius:16px;border:1px solid var(--border);margin-bottom:25px;gap:15px;flex-wrap:wrap}
.header h1{font-size:20px;font-weight:900;color:var(--primary)}
.btn-save-json{background:#10b981;color:#fff;padding:10px 18px;border-radius:8px;border:none;cursor:pointer;font-weight:800;font-size:13px;display:inline-flex;align-items:center;gap:8px}
.upload-card{background:var(--surface);border:2px dashed rgba(56,189,248,.3);border-radius:16px;padding:30px 20px;text-align:center;margin-bottom:25px;cursor:pointer}
.upload-btn{background:var(--primary);color:#04121d;font-weight:800;padding:10px 25px;border-radius:8px;display:inline-block;margin-top:12px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px;margin-bottom:25px}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px}
.stat-card h3{font-size:13px;color:var(--text-muted);margin-bottom:6px}
.stat-card p{font-size:24px;font-weight:900;color:#fff}
.tab-content{display:none}
.tab-content.active{display:block}
.table-container{background:var(--surface);border:1px solid var(--border);border-radius:16px;overflow-x:auto}
table{width:100%;border-collapse:collapse;text-align:right;font-size:13px}
th,td{padding:15px 20px;border-bottom:1px solid var(--border);white-space:nowrap}
th{background:#111a2e;color:var(--primary);font-weight:700}
tbody tr{cursor:pointer}
tbody tr:hover{background:rgba(56,189,248,.05)}
.badge{padding:4px 12px;border-radius:15px;font-size:11px;font-weight:700;display:inline-flex;align-items:center;gap:5px}
.badge-success{background:rgba(16,185,129,.15);color:#10b981;border:1px solid #10b981}
.badge-danger{background:rgba(239,68,68,.15);color:#ef4444;border:1px solid #ef4444}
.badge-warning{background:rgba(245,158,11,.15);color:#f59e0b;border:1px solid #f59e0b}
.badge-info{background:rgba(56,189,248,.15);color:#38bdf8;border:1px solid #38bdf8}
code{background:rgba(255,255,255,.06);padding:2px 6px;border-radius:4px;color:var(--primary);font-family:monospace}
.admin-box{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:25px;margin-bottom:25px}
.admin-box h2{font-size:17px;color:var(--primary);margin-bottom:20px;display:flex;align-items:center;gap:10px}
.form-row{display:flex;gap:15px;margin-bottom:15px;flex-wrap:wrap}
.form-group{flex:1;min-width:220px;display:flex;flex-direction:column;gap:6px}
.form-group label{font-size:13px;color:var(--text-muted);font-weight:600}
.form-control{background:var(--box-bg);border:1px solid var(--border);color:#fff;padding:10px 15px;border-radius:8px;outline:none;font-size:14px}
.form-control:focus{border-color:var(--primary)}
.color-picker-box{background:#10b981;color:#fff;padding:10px 15px;border-radius:8px;font-weight:800;cursor:pointer;text-align:center;user-select:none}
.btn-action{background:var(--primary);color:#04121d;font-weight:800;padding:10px 20px;border-radius:8px;border:none;cursor:pointer;align-self:flex-end;display:inline-flex;align-items:center;gap:8px;font-size:14px}
.btn-action:hover{opacity:.9}
.modal-overlay{position:fixed;inset:0;background:rgba(4,7,15,.85);backdrop-filter:blur(8px);display:none;justify-content:center;align-items:center;z-index:9999;padding:20px}
.modal-card{background:#0e1726;border:1px solid var(--primary);width:100%;max-width:900px;border-radius:20px;overflow:hidden}
.api-fullscreen-modal{position:fixed;inset:0;background:var(--bg);z-index:10000;display:none;flex-direction:column;overflow:hidden}
.api-modal-header{background:var(--surface);padding:20px 30px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.api-modal-header h2{color:var(--primary);font-size:20px;font-weight:900;display:flex;align-items:center;gap:10px}
.btn-close-api{background:rgba(239,68,68,.2);color:var(--danger);border:1px solid var(--danger);padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:800;font-size:14px}
.btn-close-api:hover{background:var(--danger);color:#fff}
.api-modal-body{flex:1;padding:30px;overflow-y:auto}
.category-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:25px}
.category-box{background:var(--box-bg);border:1px solid var(--border);border-radius:14px;padding:25px 20px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;transition:.3s;box-shadow:0 4px 15px rgba(0,0,0,.2);position:relative}
.category-box:hover{border-color:var(--primary);transform:translateY(-5px);background:rgba(56,189,248,.05)}
.category-box i{font-size:2.2rem;margin-bottom:14px}
.cat-folder i{color:#f59e0b}
.cat-product i{color:#10b981}
.category-box .cat-title{font-size:1.05rem;font-weight:800;color:#fff;margin-bottom:6px;cursor:pointer}
.category-box .cat-subtitle{font-size:.82rem;color:var(--text-muted);margin-bottom:12px;word-break:break-word}
.btn-select-cat{background:#10b981;color:#fff;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:800;border:none;cursor:pointer}
.btn-select-cat:hover{background:#059669}
.btn-enter-cat{background:#38bdf8;color:#04121d;padding:6px 14px;border-radius:6px;font-size:12px;font-weight:800;border:none;cursor:pointer}
.vertical-products-list{display:flex;flex-direction:column;gap:12px;margin-top:15px}
.vertical-product-card{background:var(--box-bg);border:1px solid var(--border);border-radius:12px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.vertical-product-card:hover{border-color:var(--primary)}
.breadcrumb{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:15px;font-size:13px}
.breadcrumb-item{padding:5px 12px;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.3);border-radius:6px;color:var(--primary);cursor:pointer;font-weight:700}
.breadcrumb-item:hover{background:rgba(56,189,248,.2)}
.breadcrumb-item.active{background:var(--primary);color:#04121d;cursor:default}
.breadcrumb-sep{color:var(--text-muted)}
.order-topbar{display:flex;justify-content:space-between;align-items:center;padding:20px 30px;border-bottom:1px solid var(--border);background:#131d31}
.order-content-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:25px 30px}
.section-box{background:var(--box-bg);border:1px solid var(--border);border-radius:12px;padding:18px}
.info-row{display:flex;justify-content:space-between;margin-bottom:12px;font-size:13px}
.info-row .fn{color:var(--text-muted)}
.info-row .fv{color:#fff;font-weight:700}
.input-display{background:#0d1524;border:1px solid var(--border);padding:10px 14px;border-radius:8px;display:flex;justify-content:space-between;align-items:center;color:var(--primary);font-family:monospace;font-size:13px}
.response-terminal{background:#090e18;border:1px solid var(--border);padding:12px;border-radius:8px;font-family:'Courier New',monospace;font-size:12px;color:#34d399;line-height:1.5;white-space:pre-wrap;max-height:300px;overflow:auto}
.modal-footer{padding:15px 30px;background:#111a2e;display:flex;justify-content:flex-end}
.close-btn{background:#1e293b;color:#fff;padding:6px 20px;border-radius:6px;border:1px solid var(--border);cursor:pointer}
.sec-accordion-item{background:var(--box-bg);border:1px solid var(--border);border-radius:12px;margin-bottom:12px;overflow:hidden}
.sec-accordion-header{padding:16px 20px;background:rgba(255,255,255,.03);display:flex;justify-content:space-between;align-items:center;cursor:pointer;font-weight:800;color:#fff}
.sec-accordion-header:hover{background:rgba(56,189,248,.08)}
.sec-accordion-body{padding:15px 20px;border-top:1px solid var(--border);display:none}
.sec-accordion-item.active .sec-accordion-body{display:block}
.api-invoice-modal{position:fixed;inset:0;background:rgba(4,7,15,.9);backdrop-filter:blur(8px);z-index:11000;display:none;justify-content:center;align-items:center;padding:20px}
.api-invoice-card{background:#0e1726;border:1px solid var(--primary);border-radius:20px;width:100%;max-width:700px;max-height:90vh;overflow-y:auto}
.api-invoice-header{padding:20px 25px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;background:#131d31}
.api-invoice-header h2{color:var(--primary);font-size:18px;font-weight:900}
.api-invoice-body{padding:25px}
.api-invoice-row{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px dashed var(--border);font-size:14px;gap:15px}
.api-invoice-row .label{color:var(--text-muted);font-weight:600;flex-shrink:0}
.api-invoice-row .value{color:#fff;font-weight:800;text-align:left;word-break:break-word}
.param-input{width:100%;background:var(--box-bg);border:1px solid var(--border);color:#fff;padding:10px 15px;border-radius:8px;outline:none;font-size:14px;margin-top:6px}
.param-input:focus{border-color:var(--primary)}
.raw-json{background:#090e18;border:1px solid var(--border);padding:20px;border-radius:10px;text-align:left;direction:ltr;font-family:monospace;font-size:12px;color:#34d399;max-height:65vh;overflow:auto;white-space:pre-wrap;width:100%}
.loading{color:var(--primary);width:100%;text-align:center;padding:30px;font-size:14px}
.empty-msg{color:var(--warning);width:100%;text-align:center;padding:30px;font-size:14px;background:rgba(245,158,11,.05);border:1px dashed var(--warning);border-radius:12px}
.tree-stat{font-size:11px;background:rgba(255,255,255,.06);padding:2px 8px;border-radius:5px;color:var(--text-muted)}
.progress-bar{width:100%;height:8px;background:#0d1524;border-radius:4px;overflow:hidden;margin-top:10px}
.progress-fill{height:100%;background:linear-gradient(90deg,#10b981,#38bdf8);width:0%;transition:width .3s;border-radius:4px}
.edit-section-modal{position:fixed;inset:0;background:rgba(4,7,15,.9);backdrop-filter:blur(8px);z-index:12000;display:none;justify-content:center;align-items:center;padding:20px}
.edit-section-card{background:#0e1726;border:1px solid var(--primary);border-radius:20px;width:100%;max-width:600px;max-height:90vh;overflow-y:auto;box-shadow:0 0 40px rgba(56,189,248,.25)}
.edit-section-header{padding:20px 25px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;background:#131d31;border-radius:20px 20px 0 0}
.edit-section-header h2{color:var(--primary);font-size:18px;font-weight:900;display:flex;align-items:center;gap:10px}
.edit-section-body{padding:25px}
.edit-section-body .form-group{margin-bottom:18px}
.edit-section-body label{display:block;color:var(--text-muted);font-size:13px;font-weight:700;margin-bottom:8px}
.edit-section-body select.form-control,.edit-section-body input.form-control{width:100%;padding:12px 15px;font-size:14px}
.edit-section-footer{padding:15px 25px;background:#111a2e;display:flex;justify-content:flex-end;gap:10px;border-radius:0 0 20px 20px}
.btn-cancel{background:#1e293b;color:#fff;padding:10px 20px;border-radius:8px;border:1px solid var(--border);cursor:pointer;font-weight:800}
.btn-save-section{background:#10b981;color:#fff;padding:10px 25px;border-radius:8px;border:none;cursor:pointer;font-weight:800;display:inline-flex;align-items:center;gap:8px}
.btn-save-section:hover{background:#059669}
.btn-edit-section{background:#f59e0b;color:#fff;padding:10px 20px;border-radius:8px;border:none;cursor:pointer;font-weight:800;font-size:14px;display:inline-flex;align-items:center;gap:8px}
.btn-edit-section:hover{background:#d97706}
.section-preview{background:#090e18;border:1px dashed var(--primary);border-radius:10px;padding:15px;margin-top:15px;font-size:13px;color:var(--text-muted)}
.section-preview strong{color:var(--primary)}
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
<li onclick="switchTab('apiTab', this)"><i class="fa-solid fa-network-wired"></i> إدارة الـ API</li>
<li onclick="switchTab('settingsTab', this)"><i class="fa-solid fa-sliders"></i> إعدادات البوت</li>
<li onclick="switchTab('depositsTab', this)"><i class="fa-solid fa-wallet"></i> طرق الإيداع</li>
</ul>
</div>

<div class="main-content">
<div class="header">
<div style="display:flex;align-items:center;gap:12px">
<button class="btn-menu-trigger" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i> القائمة</button>
<h1 id="pageTitle">متابعة الطلبات</h1>
</div>
<div style="display:flex;gap:10px">
<button class="btn-save-json" onclick="saveDataToServer()"><i class="fa-solid fa-cloud-arrow-up"></i> حفظ بالسيرفر</button>
<button class="btn-save-json" style="background:#0284c7" onclick="exportUpdatedJson()"><i class="fa-solid fa-download"></i> تحميل نسخة</button>
</div>
</div>

<div class="upload-card" onclick="document.getElementById('fileInput').click()">
<h3><i class="fa-solid fa-file-arrow-up"></i> اضغط هنا لرفع ملف data.jshon</h3>
<input type="file" id="fileInput" accept=".json,.jshon" style="display:none" onchange="uploadFileToServer(event)">
<span class="upload-btn"><i class="fa-solid fa-upload"></i> رفع الملف</span>
</div>

<div class="stats-grid" id="statsArea" style="display:none">
<div class="stat-card"><h3>إجمالي الطلبات</h3><p id="stTotalOrders">0</p></div>
<div class="stat-card"><h3>المستخدمين</h3><p id="stTotalUsers">0</p></div>
<div class="stat-card"><h3>الإيداعات</h3><p id="stTotalDeposits">0</p></div>
<div class="stat-card"><h3>أرصدة العملاء</h3><p id="stTotalBalances">$0</p></div>
</div>

<div id="ordersTab" class="tab-content active">
<div style="display:flex;gap:10px;margin-bottom:20px">
<input type="text" id="searchInput" class="form-control" style="flex:1" placeholder="بحث..." onkeyup="liveFilter()">
<select id="statusSelect" class="form-control" style="width:200px" onchange="liveFilter()">
<option value="all">كل الحالات</option>
<option value="مقبول">المقبولة</option>
<option value="مرفوض">المرفوضة</option>
<option value="قيد المعالجة">قيد المعالجة</option>
</select>
</div>
<div class="table-container">
<table>
<thead><tr>
<th>رقم الطلب</th><th>آيدي</th><th>المنتج</th><th>الفئة</th><th>المدخلات</th><th>السعر</th><th>الحالة</th><th>التاريخ</th>
</tr></thead>
<tbody id="ordersBody"><tr><td colspan="8" style="text-align:center;color:var(--text-muted)">جاري التحميل...</td></tr></tbody>
</table>
</div>
</div>

<div id="productsTab" class="tab-content">
<div class="admin-box">
<h2><i class="fa-solid fa-layer-group"></i> الأقسام والفئات</h2>
<div id="sectionsDisplay">لا توجد أقسام.</div>
</div>

<div class="admin-box" style="border-color:rgba(245,158,11,.4)">
<h2><i class="fa-solid fa-pen-to-square"></i> أدوات تعديل الأقسام</h2>
<div style="display:flex;gap:10px;flex-wrap:wrap">
<button class="btn-edit-section" onclick="openEditSectionModal()"><i class="fa-solid fa-pen"></i> تعديل اسم قسم</button>
</div>
</div>

<div class="admin-box">
<h2><i class="fa-solid fa-plus"></i> إضافة قسم يدوي</h2>
<div class="form-row">
<div class="form-group"><label>اسم القسم:</label><input type="text" id="newSectionName" class="form-control"></div>
<div class="form-group"><label>آيدي الإيموجي:</label><input type="text" id="newSectionEmoji" class="form-control" value="5958451234032589521"></div>
</div>
<div class="form-group" style="margin-bottom:15px"><label>الوصف:</label><input type="text" id="newSectionDesc" class="form-control"></div>
<button class="btn-action" onclick="addNewSection()"><i class="fa-solid fa-check"></i> حفظ</button>
</div>
</div>

<div id="usersTab" class="tab-content">
<div class="admin-box">
<h2><i class="fa-solid fa-coins"></i> شحن/خصم</h2>
<div class="form-row">
<div class="form-group"><label>آيدي:</label><input type="text" id="chargeUserId" class="form-control"></div>
<div class="form-group"><label>المبلغ $:</label><input type="number" id="chargeAmount" step="0.01" class="form-control"></div>
<button class="btn-action" style="background:#10b981" onclick="modifyBalance('add')"><i class="fa-solid fa-plus"></i> شحن</button>
<button class="btn-action" style="background:#ef4444" onclick="modifyBalance('deduct')"><i class="fa-solid fa-minus"></i> خصم</button>
</div>
</div>
<div class="admin-box">
<h2><i class="fa-solid fa-user-slash"></i> حظر/فك</h2>
<div class="form-row">
<div class="form-group"><label>آيدي:</label><input type="text" id="banUserId" class="form-control"></div>
<button class="btn-action" style="background:#ef4444" onclick="toggleBan('ban')">حظر</button>
<button class="btn-action" style="background:#10b981" onclick="toggleBan('unban')">فك</button>
</div>
</div>
</div>

<div id="apiTab" class="tab-content">
<div class="admin-box">
<h2><i class="fa-solid fa-cloud-arrow-down"></i> مستعرض API</h2>
<p style="color:var(--text-muted);font-size:13px;margin-bottom:15px">افتح المستعرض لعرض الأقسام والفئات والمنتجات</p>
<button class="btn-action" style="background:#38bdf8;color:#0b111e" onclick="openApiFullscreen()"><i class="fa-solid fa-cloud-arrow-down"></i> فتح المستعرض</button>
</div>
<div class="admin-box">
<h2><i class="fa-solid fa-chart-line"></i> نسبة الربح %</h2>
<div class="form-row">
<div class="form-group"><input type="number" id="profitPercentageInput" class="form-control"></div>
<button class="btn-action" onclick="updateProfit()">تحديث</button>
</div>
</div>
</div>

<div id="settingsTab" class="tab-content">
<div class="admin-box">
<h2><i class="fa-solid fa-bullhorn"></i> الروابط</h2>
<div class="form-row">
<div class="form-group"><label>قناة الاشتراك:</label><input type="text" id="botChannelInput" class="form-control"></div>
<div class="form-group"><label>رابط الأخبار:</label><input type="text" id="botNewsInput" class="form-control"></div>
</div>
<div class="form-row">
<div class="form-group"><label>رابط الدعم:</label><input type="text" id="botSupportInput" class="form-control"></div>
</div>
<button class="btn-action" onclick="updateGeneralSettings()">حفظ</button>
</div>
<div class="admin-box">
<h2><i class="fa-solid fa-message"></i> رسالة الترحيب</h2>
<textarea id="welcomeTextInput" class="form-control" rows="4" style="width:100%;margin-bottom:15px"></textarea>
<button class="btn-action" onclick="updateWelcomeText()">حفظ</button>
</div>
</div>

<div id="depositsTab" class="tab-content">
<div class="admin-box">
<h2><i class="fa-solid fa-money-check-dollar"></i> طرق الإيداع</h2>
<div id="depositsListDisplay">لا توجد طرق إيداع.</div>
</div>
</div>
</div>

<div class="api-fullscreen-modal" id="apiFullscreenModal">
<div class="api-modal-header">
<h2><i class="fa-solid fa-network-wired"></i> مستعرض API - Tartousi Store</h2>
<button class="btn-close-api" onclick="closeApiFullscreen()"><i class="fa-solid fa-xmark"></i> إغلاق</button>
</div>
<div class="api-modal-body">

<div class="admin-box">
<h2><i class="fa-solid fa-key"></i> التوثيق</h2>
<div class="form-group" style="margin-bottom:15px">
<label>api-token</label>
<input type="text" class="form-control" value="hwooO_oNPFMF0Uw_sPwIs2YIG_MH2qoQiKdHFt76_AfBaxmzq1fdPcolzadwS43s" readonly style="background:#090e18;color:var(--primary);font-family:monospace">
</div>
<div style="display:flex;gap:10px;flex-wrap:wrap">
<button class="btn-action" style="background:#10b981;color:#fff" onclick="loadRootContent()"><i class="fa-solid fa-rotate"></i> تحميل الأقسام الرئيسية</button>
<button class="btn-action" style="background:#f59e0b;color:#fff" onclick="showRawCurrent()"><i class="fa-solid fa-code"></i> عرض الـ raw للمستوى الحالي</button>
<button class="btn-action" style="background:#ef4444;color:#fff" onclick="clearCache()"><i class="fa-solid fa-trash"></i> مسح الكاش</button>
</div>
</div>

<div class="admin-box" id="importConfigBox" style="display:none;border-color:#10b981">
<h2><i class="fa-solid fa-file-circle-plus"></i> استيراد: <span id="selectedCatName" style="color:#fff">---</span></h2>
<div class="form-row">
<div class="form-group"><label>آيدي الإيموجي:</label><input type="text" id="importEmojiInput" class="form-control" value="5958451234032589521"></div>
<div class="form-group"><label>اللون:</label><div id="colorPickerBtn" class="color-picker-box" onclick="cycleColor()">🟩 أخضر</div></div>
</div>
<div class="form-group" style="margin-bottom:15px"><label>الوصف:</label><input type="text" id="importDescriptionInput" class="form-control" value="شحن تلقائي ومباشر"></div>
<div id="importCountInfo" style="color:var(--primary);font-size:13px;margin-bottom:15px"></div>
<div class="progress-bar" id="importProgressBar" style="display:none"><div class="progress-fill" id="importProgressFill"></div></div>
<div style="display:flex;gap:10px;margin-top:15px">
<button class="btn-action" style="background:#10b981;color:#fff" id="confirmImportBtn" onclick="confirmImportCategory()"><i class="fa-solid fa-download"></i> تأكيد الاستيراد</button>
<button class="btn-action" style="background:#64748b;color:#fff" onclick="cancelImport()"><i class="fa-solid fa-xmark"></i> إلغاء</button>
</div>
</div>

<div style="margin-top:25px">
<div id="breadcrumbArea" class="breadcrumb" style="display:none"></div>
<div id="apiCurrentTitle" style="font-size:1.1rem;color:var(--primary);margin-bottom:15px;display:none">
<i class="fa-solid fa-folder-tree"></i> <span id="apiTitleText">الأقسام الرئيسية</span>
</div>
<div id="apiCategoriesContainer" class="category-grid">
<p class="loading">اضغط "تحميل الأقسام الرئيسية" للبدء...</p>
</div>
</div>

</div>
</div>

<div class="api-invoice-modal" id="apiInvoiceModal" onclick="closeInvoiceModal(event)">
<div class="api-invoice-card" onclick="event.stopPropagation()">
<div class="api-invoice-header">
<h2><i class="fa-solid fa-file-invoice-dollar"></i> فاتورة المنتج</h2>
<button class="btn-close-api" onclick="document.getElementById('apiInvoiceModal').style.display='none'"><i class="fa-solid fa-xmark"></i> إغلاق</button>
</div>
<div class="api-invoice-body" id="apiInvoiceBody"></div>
</div>
</div>

<div class="edit-section-modal" id="editSectionModal" onclick="closeEditSectionModal(event)">
<div class="edit-section-card" onclick="event.stopPropagation()">
<div class="edit-section-header">
<h2><i class="fa-solid fa-pen-to-square"></i> تعديل اسم قسم</h2>
<button class="btn-close-api" onclick="document.getElementById('editSectionModal').style.display='none'"><i class="fa-solid fa-xmark"></i> إغلاق</button>
</div>
<div class="edit-section-body">
<div class="form-group">
<label><i class="fa-solid fa-folder-tree"></i> اختر القسم المراد تعديله:</label>
<select id="editSectionSelect" class="form-control" onchange="onEditSectionSelectChange()">
<option value="">-- اختر القسم --</option>
</select>
</div>
<div class="form-group">
<label><i class="fa-solid fa-tag"></i> اسم القسم الجديد:</label>
<input type="text" id="editSectionNewName" class="form-control" placeholder="اكتب الاسم الجديد...">
</div>
<div class="form-group">
<label><i class="fa-solid fa-face-smile"></i> إيموجي البريميوم (Emoji ID):</label>
<input type="text" id="editSectionEmoji" class="form-control" placeholder="مثال: 5958451234032589521" value="5958451234032589521">
</div>
<div class="section-preview" id="editSectionPreview">
<i class="fa-solid fa-info-circle"></i> اختر قسماً لعرض معلوماته الحالية
</div>
</div>
<div class="edit-section-footer">
<button class="btn-cancel" onclick="document.getElementById('editSectionModal').style.display='none'"><i class="fa-solid fa-xmark"></i> إلغاء</button>
<button class="btn-save-section" onclick="saveEditedSection()"><i class="fa-solid fa-floppy-disk"></i> حفظ وتحديث</button>
</div>
</div>
</div>

<div class="modal-overlay" id="orderModal" onclick="closeModal(event)">
<div class="modal-card" onclick="event.stopPropagation()">
<div class="order-topbar">
<div><span style="color:var(--text-muted);font-size:13px">المنتج:</span> <span id="mProduct" style="font-weight:800;color:#fff">---</span></div>
<div><span style="color:var(--text-muted);font-size:13px">الآيدي:</span> <span id="mUserId" style="color:var(--primary);font-weight:800">---</span></div>
<div id="mStatusBadge">---</div>
</div>
<div class="order-content-grid">
<div class="section-box">
<div style="font-weight:800;color:var(--primary);margin-bottom:15px"><i class="fa-solid fa-cube"></i> تفاصيل</div>
<div class="info-row"><span class="fn">رقم الطلب:</span><span class="fv" id="mOrderNum">---</span></div>
<div class="info-row"><span class="fn">الفئة:</span><span class="fv" id="mCategory">---</span></div>
<div class="info-row"><span class="fn">السعر:</span><span class="fv" id="mPrice">$0</span></div>
<div class="info-row"><span class="fn">التاريخ:</span><span class="fv" id="mDate">---</span></div>
</div>
<div class="section-box">
<div style="font-weight:800;color:var(--primary);margin-bottom:15px"><i class="fa-solid fa-circle-info"></i> المدخلات</div>
<div class="input-display"><span id="mPlayerId">---</span><button style="background:none;border:none;color:#fff;cursor:pointer" onclick="copyText('mPlayerId')"><i class="fa-regular fa-copy"></i></button></div>
<div class="response-terminal" id="mResponseTerminal">Success</div>
</div>
</div>
<div class="modal-footer"><button class="close-btn" onclick="document.getElementById('orderModal').style.display='none'">إغلاق</button></div>
</div>
</div>

<script>
// ================== STATE ==================
let botData = null;
let globalOrders = [];

let contentCache = {};
let navigationStack = [];
let selectedImport = null;
let currentLevelData = null;
let allDescendantsCache = {};

const availableColors = [
    { label: "🟩 أخضر", bg: "#10b981", code: "green" },
    { label: "🟥 أحمر", bg: "#ef4444", code: "red" },
    { label: "🟦 أزرق", bg: "#0284c7", code: "blue" }
];
let currentColorIdx = 0;

document.addEventListener("DOMContentLoaded", fetchDataFromServer);

// ================== BOT DATA ==================
function fetchDataFromServer() {
    fetch('/get-data').then(r => r.json()).then(data => {
        if (data && Object.keys(data).length > 0) {
            botData = data;
            renderAllData();
        } else {
            document.getElementById('ordersBody').innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">الملف فارغ</td></tr>';
        }
    }).catch(() => {
        document.getElementById('ordersBody').innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--danger)">فشل</td></tr>';
    });
}

function uploadFileToServer(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        try {
            const parsed = JSON.parse(e.target.result);
            fetch('/save-data', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(parsed) })
                .then(() => { botData = parsed; renderAllData(); alert("تم!"); });
        } catch(err){ alert("ملف غير صالح!"); }
    };
    reader.readAsText(file);
}

function saveDataToServer() {
    if (!botData) return alert("لا بيانات");
    fetch('/save-data', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(botData) })
        .then(() => alert("تم الحفظ!"));
}

function saveDataToServerSilent() {
    if (!botData) return;
    fetch('/save-data', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(botData) });
}

function toggleSidebar(){document.getElementById('sidebar').classList.toggle('open');document.getElementById('sidebarBackdrop').classList.toggle('active')}
function closeSidebar(){document.getElementById('sidebar').classList.remove('open');document.getElementById('sidebarBackdrop').classList.remove('active')}
function switchTab(id, el){
    document.querySelectorAll('.tab-content').forEach(e => e.classList.remove('active'));
    document.querySelectorAll('.sidebar-menu li').forEach(e => e.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    if(el) el.classList.add('active');
    document.getElementById('pageTitle').innerText = el ? el.innerText.trim() : '';
    if(window.innerWidth<=992) closeSidebar();
}
function openApiFullscreen(){document.getElementById('apiFullscreenModal').style.display='flex'}
function closeApiFullscreen(){document.getElementById('apiFullscreenModal').style.display='none'}
function cycleColor(){currentColorIdx=(currentColorIdx+1)%availableColors.length;const b=document.getElementById('colorPickerBtn');b.innerText=availableColors[currentColorIdx].label;b.style.background=availableColors[currentColorIdx].bg}

// ================== fetch /content/{id} ==================
function fetchContent(id) {
    let key = String(id);
    if (contentCache[key]) return Promise.resolve(contentCache[key]);
    return fetch('/fetch-external-api?endpoint=content&id=' + encodeURIComponent(key))
        .then(r => r.json())
        .then(data => {
            contentCache[key] = data;
            return data;
        });
}

function clearCache(){contentCache={};allDescendantsCache={};alert("تم مسح الكاش")}

// ================== PARSER ==================
function parseContentResponse(data) {
    let categories = [];
    let products = [];
    if (!data) return { categories, products };
    if (Array.isArray(data)) {
        data.forEach(item => { if (item && typeof item === 'object') classifyItem(item, categories, products); });
        return { categories, products };
    }
    if (typeof data === 'object') {
        let keysToCheck = ['categories', 'subcategories', 'sub_categories', 'children', 'items', 'data', 'result', 'results', 'content'];
        let found = false;
        for (let k of keysToCheck) {
            if (Array.isArray(data[k])) {
                data[k].forEach(item => { if (item && typeof item === 'object') classifyItem(item, categories, products); });
                found = true;
            }
        }
        if (Array.isArray(data.products)) {
            data.products.forEach(p => { if (p && typeof p === 'object') classifyItem(p, categories, products); });
            found = true;
        }
        if (!found) {
            for (let k in data) {
                if (Array.isArray(data[k])) {
                    data[k].forEach(item => { if (item && typeof item === 'object') classifyItem(item, categories, products); });
                }
            }
        }
    }
    return { categories, products };
}

function classifyItem(item, categories, products) {
    let isProduct = (item.id !== undefined) &&
                    (item.price !== undefined || item.base_price !== undefined) &&
                    !item.products && !item.subcategories && !item.children && !item.categories;
    let hasChildren = !!(item.products || item.subcategories || item.children || item.categories);
    let isCategory = !isProduct && (item.id !== undefined || item.name !== undefined) && (hasChildren || item.price === undefined);
    if (isProduct) {
        products.push(item);
    } else if (isCategory) {
        categories.push(item);
        if (Array.isArray(item.products)) item.products.forEach(p => { if (p && typeof p === 'object') classifyItem(p, categories, products); });
        if (Array.isArray(item.subcategories)) item.subcategories.forEach(sc => { if (sc && typeof sc === 'object') classifyItem(sc, categories, products); });
    } else {
        if (item.id !== undefined && (item.price !== undefined || item.base_price !== undefined)) products.push(item);
        else if (item.id !== undefined || item.name !== undefined) categories.push(item);
    }
}

// ================== تحميل الجذر ==================
function loadRootContent() {
    const container = document.getElementById('apiCategoriesContainer');
    container.innerHTML = '<p class="loading"><i class="fa-solid fa-spinner fa-spin"></i> جاري تحميل الأقسام الرئيسية...</p>';
    navigationStack = [{ id: 0, name: 'الأقسام الرئيسية' }];
    fetchContent(0).then(data => { renderContentLevel(data); }).catch(err => {
        container.innerHTML = '<p class="loading" style="color:var(--danger)">خطأ: ' + escapeHtml(err.message) + '</p>';
    });
}

// ================== عرض مستوى ==================
function renderContentLevel(data) {
    currentLevelData = data;
    const container = document.getElementById('apiCategoriesContainer');
    const titleArea = document.getElementById('apiCurrentTitle');
    const titleText = document.getElementById('apiTitleText');
    const breadcrumbArea = document.getElementById('breadcrumbArea');
    container.innerHTML = '';
    titleArea.style.display = 'block';
    let current = navigationStack[navigationStack.length - 1];
    titleText.innerText = current.name;
    breadcrumbArea.style.display = 'flex';
    breadcrumbArea.innerHTML = navigationStack.map((item, i) => {
        let active = i === navigationStack.length - 1;
        return `<span class="breadcrumb-item ${active?'active':''}" onclick="jumpToLevel(${i})">${escapeHtml(item.name)}</span>`
            + (active ? '' : '<span class="breadcrumb-sep"><i class="fa-solid fa-chevron-left"></i></span>');
    }).join('');
    let parsed = parseContentResponse(data);
    let categories = parsed.categories;
    let products = parsed.products;
    let seenCats = new Set();
    categories = categories.filter(c => {
        let k = String(c.id);
        if (seenCats.has(k)) return false;
        seenCats.add(k);
        return true;
    });
    let seenProds = new Set();
    products = products.filter(p => {
        let k = String(p.id);
        if (seenProds.has(k)) return false;
        seenProds.add(k);
        return true;
    });
    if (!categories.length && !products.length) {
        container.innerHTML = `
            <div style="width:100%">
                <div class="empty-msg" style="margin-bottom:15px">
                    <i class="fa-solid fa-info-circle"></i> هذا القسم لا يحتوي على أقسام فرعية أو منتجات مباشرة — عرض الـ raw:
                </div>
                <div class="raw-json">${escapeHtml(JSON.stringify(data, null, 2))}</div>
            </div>
        `;
        return;
    }
    categories.forEach(c => {
        let cnt = 0;
        if (Array.isArray(c.products)) cnt += c.products.length;
        if (Array.isArray(c.subcategories)) cnt += c.subcategories.length;
        if (Array.isArray(c.children)) cnt += c.children.length;
        if (c.count !== undefined) cnt = c.count;
        let div = document.createElement('div');
        div.className = 'category-box cat-folder';
        let safeId = JSON.stringify(String(c.id));
        let safeName = JSON.stringify(String(c.name || 'بدون اسم'));
        div.innerHTML = `
            <i class="fa-solid fa-folder-open" onclick='enterCategory(${safeId}, ${safeName})'></i>
            <div class="cat-title" onclick='enterCategory(${safeId}, ${safeName})'>${escapeHtml(c.name || 'بدون اسم')}</div>
            <div class="cat-subtitle">${cnt ? 'عناصر: '+cnt : 'قسم فرعي'}</div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center">
                <button class="btn-enter-cat" onclick='enterCategory(${safeId}, ${safeName})'><i class="fa-solid fa-arrow-left"></i> فتح</button>
                <button class="btn-select-cat" onclick='selectCategoryForImport(${safeId}, ${safeName})'><i class="fa-solid fa-download"></i> استيراد كامل</button>
            </div>
        `;
        container.appendChild(div);
    });
    products.forEach(p => {
        let availB = p.available === false
            ? '<span class="badge badge-danger">غير متوفر</span>'
            : '<span class="badge badge-success">متوفر</span>';
        let div = document.createElement('div');
        div.className = 'category-box cat-product';
        let safeId = JSON.stringify(String(p.id));
        div.innerHTML = `
            <i class="fa-solid fa-bolt" onclick='openProductInvoiceFromCache(${safeId})'></i>
            <div class="cat-title" onclick='openProductInvoiceFromCache(${safeId})'>${escapeHtml(p.name || 'بدون اسم')}</div>
            <div class="cat-subtitle">${escapeHtml(p.category_name || '')}</div>
            <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">${availB}</div>
            <div style="color:#10b981;font-weight:900;font-size:18px;margin-bottom:10px">$${p.price !== undefined ? p.price : 0}</div>
            <button class="btn-select-cat" onclick='openProductInvoiceFromCache(${safeId})'><i class="fa-solid fa-file-invoice"></i> عرض/شراء</button>
        `;
        container.appendChild(div);
    });
}

// ================== دخول قسم ==================
function enterCategory(id, name) {
    const container = document.getElementById('apiCategoriesContainer');
    container.innerHTML = '<p class="loading"><i class="fa-solid fa-spinner fa-spin"></i> جاري تحميل أبناء القسم...</p>';
    let existingIdx = navigationStack.findIndex(x => String(x.id) === String(id));
    if (existingIdx !== -1) navigationStack = navigationStack.slice(0, existingIdx + 1);
    else navigationStack.push({ id: id, name: name });
    fetchContent(id).then(data => { renderContentLevel(data); }).catch(err => {
        container.innerHTML = '<p class="loading" style="color:var(--danger)">خطأ: ' + escapeHtml(err.message) + '</p>';
    });
}

function jumpToLevel(i) {
    navigationStack = navigationStack.slice(0, i + 1);
    let current = navigationStack[navigationStack.length - 1];
    const container = document.getElementById('apiCategoriesContainer');
    container.innerHTML = '<p class="loading"><i class="fa-solid fa-spinner fa-spin"></i> تحميل...</p>';
    fetchContent(current.id).then(data => { renderContentLevel(data); }).catch(err => {
        container.innerHTML = '<p class="loading" style="color:var(--danger)">خطأ: ' + escapeHtml(err.message) + '</p>';
    });
}

// ================== البحث عن منتج ==================
function findProductById(pid) {
    pid = String(pid);
    if (currentLevelData) {
        let parsed = parseContentResponse(currentLevelData);
        for (let p of parsed.products) { if (String(p.id) === pid) return p; }
    }
    for (let key in contentCache) {
        let data = contentCache[key];
        let parsed = parseContentResponse(data);
        for (let p of parsed.products) { if (String(p.id) === pid) return p; }
    }
    return null;
}

function openProductInvoiceFromCache(pid) {
    let p = findProductById(pid);
    if (!p) return alert("المنتج غير موجود في الكاش");
    renderInvoice(p);
}

// ================== فاتورة ==================
function renderInvoice(p) {
    let params = p.params || [];
    let qtyValues = p.qty_values;
    let price = p.price !== undefined ? p.price : 0;
    let basePrice = p.base_price !== undefined ? p.base_price : 0;
    let available = p.available !== false;
    let ptype = p.product_type || 'package';
    let inputs = '';
    if (params.length) {
        params.forEach((pr, i) => {
            inputs += `<div style="margin-bottom:14px"><label style="color:var(--text-muted);font-size:13px;font-weight:600;display:block"><i class="fa-solid fa-keyboard"></i> ${escapeHtml(pr)}</label><input type="text" class="param-input" id="api_param_${i}" placeholder="القيمة..."></div>`;
        });
    } else {
        inputs = '<p style="color:var(--text-muted);font-size:13px">لا توجد متطلبات إدخال.</p>';
    }
    let qtyHtml = '';
    if (qtyValues === null || qtyValues === undefined) {
        qtyHtml = '<input type="number" class="param-input" id="api_qty" value="1" min="1" readonly>';
    } else if (Array.isArray(qtyValues)) {
        qtyHtml = '<select class="param-input" id="api_qty">' + qtyValues.map(v=>`<option value="${v}">${v}</option>`).join('') + '</select>';
    } else if (typeof qtyValues === 'object' && qtyValues.min !== undefined) {
        qtyHtml = `<input type="number" class="param-input" id="api_qty" min="${qtyValues.min}" max="${qtyValues.max}" value="${qtyValues.min}">`;
    } else {
        qtyHtml = '<input type="number" class="param-input" id="api_qty" value="1" min="1">';
    }
    let availB = available ? '<span class="badge badge-success">متوفر</span>' : '<span class="badge badge-danger">غير متوفر</span>';
    let typeLabel = { 'amount':'كمية', 'package':'باكيج', 'service':'خدمة' }[ptype] || ptype;
    document.getElementById('apiInvoiceBody').innerHTML = `
        <div class="api-invoice-row"><span class="label">الاسم</span><span class="value">${escapeHtml(p.name)}</span></div>
        <div class="api-invoice-row"><span class="label">ID</span><span class="value"><code>${p.id}</code></span></div>
        <div class="api-invoice-row"><span class="label">القسم</span><span class="value">${escapeHtml(p.category_name||'-')}</span></div>
        <div class="api-invoice-row"><span class="label">parent_id</span><span class="value"><code>${p.parent_id||0}</code></span></div>
        <div class="api-invoice-row"><span class="label">النوع</span><span class="value">${typeLabel}</span></div>
        <div class="api-invoice-row"><span class="label">السعر</span><span class="value" style="color:#10b981;font-size:18px">$${price}</span></div>
        <div class="api-invoice-row"><span class="label">السعر الأساسي</span><span class="value">$${basePrice}</span></div>
        <div class="api-invoice-row"><span class="label">الحالة</span><span class="value">${availB}</span></div>
        <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--border)">
            <h3 style="color:var(--primary);margin-bottom:15px;font-size:15px"><i class="fa-solid fa-shopping-cart"></i> متطلبات الشراء</h3>
            ${inputs}
            <div style="margin-bottom:14px"><label style="color:var(--text-muted);font-size:13px;font-weight:600;display:block"><i class="fa-solid fa-hashtag"></i> الكمية</label>${qtyHtml}</div>
        </div>
        <div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap">
            <button class="btn-action" style="background:#10b981;color:#fff;flex:1" onclick="testCreateOrder('${p.id}')"><i class="fa-solid fa-paper-plane"></i> تجربة الطلب</button>
            <button class="btn-action" style="background:#38bdf8;color:#04121d" onclick="selectProductForImportFromRaw('${p.id}')"><i class="fa-solid fa-download"></i> استيراد المنتج</button>
        </div>
        <div id="api_order_result" style="margin-top:20px"></div>
    `;
    document.getElementById('apiInvoiceModal').style.display = 'flex';
}

function closeInvoiceModal(e) {
    if (e.target.id === 'apiInvoiceModal') document.getElementById('apiInvoiceModal').style.display = 'none';
}

function testCreateOrder(pid) {
    let p = findProductById(pid);
    if (!p) return alert("المنتج غير موجود");
    let params = p.params || [];
    let playerId = '';
    let extra = {};
    for (let i=0; i<params.length; i++) {
        let el = document.getElementById('api_param_'+i);
        if (!el) continue;
        let v = el.value.trim();
        if (!v) return alert("عبئ: "+params[i]);
        extra['param'+i] = v;
        if (i===0) playerId = v;
    }
    let qtyEl = document.getElementById('api_qty');
    let qty = qtyEl ? qtyEl.value : 1;
    let box = document.getElementById('api_order_result');
    box.innerHTML = '<p style="color:var(--primary)"><i class="fa-solid fa-spinner fa-spin"></i> إرسال...</p>';
    fetch('/create-api-order', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ product_id: pid, qty: qty, playerId: playerId, extra_params: extra }) })
        .then(r => r.json())
        .then(d => { box.innerHTML = '<div class="response-terminal">' + escapeHtml(JSON.stringify(d,null,2)) + '</div>'; })
        .catch(e => { box.innerHTML = '<p style="color:var(--danger)">فشل: '+escapeHtml(e.message)+'</p>'; });
}

// ================== تحميل كل الأبناء (BFS) ==================
async function loadAllDescendants(rootId) {
    let queue = [String(rootId)];
    let visited = new Set();
    let allCatsData = {};
    let allProdsList = [];
    
    let totalProcessed = 0;
    let progressFill = document.getElementById('importProgressFill');
    let progressBar = document.getElementById('importProgressBar');
    
    let rootData = await fetchContent(rootId);
    allCatsData[String(rootId)] = rootData;
    let rootParsed = parseContentResponse(rootData);
    rootParsed.categories.forEach(c => {
        if (!visited.has(String(c.id))) queue.push(String(c.id));
    });
    rootParsed.products.forEach(p => allProdsList.push(p));
    
    const MAX_PARALLEL = 8;
    
    while (queue.length > 0) {
        let batch = [];
        while (queue.length > 0 && batch.length < MAX_PARALLEL) {
            let id = queue.shift();
            if (visited.has(id)) continue;
            visited.add(id);
            batch.push(id);
        }
        
        if (batch.length === 0) break;
        
        let results = await Promise.all(batch.map(async (id) => {
            try {
                let data = await fetchContent(id);
                return { id, data, success: true };
            } catch (e) {
                return { id, data: null, success: false };
            }
        }));
        
        for (let r of results) {
            if (!r.success || !r.data) continue;
            allCatsData[r.id] = r.data;
            let parsed = parseContentResponse(r.data);
            parsed.products.forEach(p => allProdsList.push(p));
            parsed.categories.forEach(c => {
                if (!visited.has(String(c.id))) queue.push(String(c.id));
            });
            totalProcessed++;
        }
        
        if (progressBar && progressFill) {
            progressBar.style.display = 'block';
            progressFill.style.width = Math.min(90, (totalProcessed / (totalProcessed + queue.length + 1)) * 100) + '%';
        }
        
        let infoEl = document.getElementById('importCountInfo');
        if (infoEl) {
            infoEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> جاري التحميل... (${totalProcessed} قسم، ${allProdsList.length} منتج)`;
        }
    }
    
    if (progressFill) progressFill.style.width = '100%';
    
    return { allCatsData, allProdsList };
}

// ================== الاستيراد ==================
async function selectCategoryForImport(catId, catName) {
    let loadingMsg = document.getElementById('importCountInfo');
    document.getElementById('selectedCatName').innerText = catName;
    document.getElementById('importConfigBox').style.display = 'block';
    loadingMsg.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> جاري تحميل كل الأبناء من الـ API...';
    document.getElementById('importConfigBox').scrollIntoView({behavior:'smooth', block:'start'});
    
    let confirmBtn = document.getElementById('confirmImportBtn');
    if (confirmBtn) confirmBtn.disabled = true;

    try {
        let result = await loadAllDescendants(catId);
        let allProds = result.allProdsList;
        let allCatsData = result.allCatsData;
        
        let seenP = new Set();
        allProds = allProds.filter(p => {
            if (seenP.has(String(p.id))) return false;
            seenP.add(String(p.id));
            return true;
        });
        
        let totalSubs = Object.keys(allCatsData).length - 1;
        
        allDescendantsCache = {
            rootId: catId,
            allCatsData: allCatsData,
            allProducts: allProds
        };
        
        selectedImport = { 
            id: catId, 
            name: catName, 
            products: allProds, 
            categories: Object.values(allCatsData).filter((_, i) => i > 0)
        };
        
        loadingMsg.innerHTML = `<i class="fa-solid fa-check" style="color:#10b981"></i> اكتمل التحميل — المنتجات: <strong style="color:#fff">${allProds.length}</strong> — الأقسام الفرعية: <strong style="color:#fff">${totalSubs}</strong>`;
        
        if (confirmBtn) confirmBtn.disabled = false;
        
    } catch(err) {
        loadingMsg.innerHTML = `<span style="color:var(--danger)">خطأ: ${escapeHtml(err.message)}</span>`;
        if (confirmBtn) confirmBtn.disabled = false;
    }
}

function selectProductForImportFromRaw(pid) {
    let p = findProductById(pid);
    if (!p) return;
    selectedImport = { id: pid, name: p.name, products: [p], categories: [] };
    document.getElementById('apiInvoiceModal').style.display = 'none';
    document.getElementById('selectedCatName').innerText = p.name;
    document.getElementById('importCountInfo').innerHTML = '<i class="fa-solid fa-info-circle"></i> منتج واحد';
    document.getElementById('importConfigBox').style.display = 'block';
    document.getElementById('importConfigBox').scrollIntoView({behavior:'smooth', block:'start'});
}

function cancelImport() {
    selectedImport = null;
    allDescendantsCache = {};
    document.getElementById('importConfigBox').style.display = 'none';
    document.getElementById('importProgressBar').style.display = 'none';
    document.getElementById('importProgressFill').style.width = '0%';
}

// ================== بناء الشجرة الهرمية ==================
function buildTree(nodeId, nodeName, allCatsData, emojiId, color, desc, visited) {
    if (!visited) visited = new Set();
    let key = String(nodeId);
    if (visited.has(key)) {
        return null;
    }
    visited.add(key);
    
    let nodeData = allCatsData[key];
    if (!nodeData) return null;
    
    let parsed = parseContentResponse(nodeData);
    let products = parsed.products || [];
    let categories = parsed.categories || [];
    
    let sectionObj = {
        name: nodeName,
        emoji_id: emojiId,
        color: color,
        description: desc,
        is_api: true,
        api_category_id: nodeId,
        sub_categories: [],
        products: []
    };
    
    products.forEach(p => {
        let isCounterType = (p.product_type === "amount") && p.qty_values && typeof p.qty_values === 'object' && p.qty_values.min !== undefined;
        let prodEmoji = emojiId;
        
        let productObj = {
            id: p.id,
            api_product_id: p.id,
            is_api: true,
            name: p.name,
            price: p.price,
            base_price: p.base_price,
            available: p.available !== undefined ? p.available : true,
            description: desc,
            emoji_id: prodEmoji,
            premium_emoji: prodEmoji,
            params: p.params || [],
            qty_values: p.qty_values,
            product_type: p.product_type,
            parent_id: p.parent_id,
            category_name: p.category_name,
            categories: [],
            counter_categories: [],
            stock_categories: []
        };
        
        if (isCounterType) {
            productObj.counter_categories.push({
                name: p.name,
                min: parseInt(p.qty_values.min) || 1,
                max: parseInt(p.qty_values.max) || 99999,
                price_per_unit: parseFloat(p.price) || 0,
                emoji_id: prodEmoji,
                is_auto_api: true,
                api_product_id: p.id
            });
        } else {
            productObj.categories.push({
                name: p.name,
                price: String(p.price || 0),
                emoji_id: prodEmoji,
                is_auto_api: true,
                api_product_id: p.id
            });
        }
        
        sectionObj.products.push(productObj);
    });
    
    categories.forEach(c => {
        let childSection = buildTree(c.id, c.name, allCatsData, emojiId, color, desc, visited);
        if (childSection) {
            sectionObj.sub_categories.push(childSection);
        }
    });
    
    return sectionObj;
}

function confirmImportCategory() {
    if (!selectedImport) return alert("اختر عنصر أولاً");
    if (!botData) botData = {};
    if (!botData.sections) botData.sections = [];
    if (!botData.api_products) botData.api_products = [];

    let emojiId = document.getElementById('importEmojiInput').value.trim() || "5958451234032589521";
    let color = availableColors[currentColorIdx].code;
    let desc = document.getElementById('importDescriptionInput').value.trim() || "شحن تلقائي";
    
    if (!allDescendantsCache.rootId || !allDescendantsCache.allCatsData) {
        alert("ما في بيانات للقسم. جرب تعيد التحميل.");
        return;
    }
    
    let rootData = allDescendantsCache.allCatsData[String(allDescendantsCache.rootId)];
    if (!rootData) {
        alert("ما في بيانات الجذر!");
        return;
    }
    
    let rootSection = buildTree(
        allDescendantsCache.rootId,
        selectedImport.name,
        allDescendantsCache.allCatsData,
        emojiId,
        color,
        desc
    );
    
    if (!rootSection) {
        alert("فشل بناء الشجرة!");
        return;
    }
    
    let newSectionIndex = botData.sections.findIndex(s => s.name === selectedImport.name);
    if (newSectionIndex === -1) {
        newSectionIndex = botData.sections.length;
        botData.sections.push(rootSection);
    } else {
        botData.sections[newSectionIndex] = rootSection;
    }
    
    function linkProductsRecursive(section, path) {
        section.products = section.products || [];
        section.products.forEach((prod, p_idx) => {
            if (prod.api_product_id || prod.is_api) {
                (prod.categories || []).forEach((cat, c_idx) => {
                    let exists = botData.api_products.some(ap => 
                        JSON.stringify(ap.bot_path) === JSON.stringify(path) &&
                        ap.bot_product === p_idx &&
                        ap.bot_category_type === "normal" &&
                        ap.bot_category === c_idx
                    );
                    if (!exists) {
                        botData.api_products.push({
                            bot_section: path[0] !== undefined ? path[0] : 0,
                            bot_path: path,
                            bot_product: p_idx,
                            bot_category_type: "normal",
                            bot_category: c_idx,
                            api_product_id: prod.api_product_id || prod.id,
                            api_product_name: prod.name,
                            api_price: prod.price,
                            api_params: prod.params || []
                        });
                    }
                });
                (prod.counter_categories || []).forEach((cat, c_idx) => {
                    let exists = botData.api_products.some(ap => 
                        JSON.stringify(ap.bot_path) === JSON.stringify(path) &&
                        ap.bot_product === p_idx &&
                        ap.bot_category_type === "counter" &&
                        ap.bot_category === c_idx
                    );
                    if (!exists) {
                        botData.api_products.push({
                            bot_section: path[0] !== undefined ? path[0] : 0,
                            bot_path: path,
                            bot_product: p_idx,
                            bot_category_type: "counter",
                            bot_category: c_idx,
                            api_product_id: prod.api_product_id || prod.id,
                            api_product_name: prod.name,
                            api_price: prod.price,
                            api_params: prod.params || []
                        });
                    }
                });
            }
        });
        (section.sub_categories || []).forEach((sub, s_idx) => {
            linkProductsRecursive(sub, path.concat([s_idx]));
        });
    }
    
    linkProductsRecursive(rootSection, [newSectionIndex]);

    saveDataToServerSilent();
    renderSections();
    populateEditSectionSelect();
    
    let totalProducts = 0;
    let totalSubs = 0;
    function countAll(sec) {
        totalProducts += (sec.products || []).length;
        totalSubs += (sec.sub_categories || []).length;
        (sec.sub_categories || []).forEach(countAll);
    }
    countAll(rootSection);
    
    let linkedCount = botData.api_products.length;
    alert(`تم استيراد "${selectedImport.name}" كاملاً:\n• ${totalSubs} قسم فرعي\n• ${totalProducts} منتج\n• ${linkedCount} فئة مربوطة بـ API`);
    cancelImport();
}

// ================== عرض بيانات البوت ==================
function renderAllData() {
    if (!botData) return;
    const users = botData.users || {};
    const stats = botData.statistics || {};
    const orders = botData.user_orders || {};
    let totalBal = 0;
    for (let u in users) totalBal += parseFloat(users[u].balance || 0);
    document.getElementById('stTotalOrders').innerText = stats.total_orders || 0;
    document.getElementById('stTotalUsers').innerText = Object.keys(users).length;
    document.getElementById('stTotalDeposits').innerText = stats.total_deposits || 0;
    document.getElementById('stTotalBalances').innerText = '$' + totalBal.toFixed(2);
    document.getElementById('statsArea').style.display = 'grid';
    document.getElementById('profitPercentageInput').value = botData.profit_percentage || 0;
    document.getElementById('botChannelInput').value = botData.required_channel || '';
    document.getElementById('botNewsInput').value = botData.bot_news_link || '';
    document.getElementById('botSupportInput').value = botData.bot_support_link || '';
    document.getElementById('welcomeTextInput').value = botData.welcome_text || '';
    globalOrders = [];
    for (let uid in orders) {
        let arr = orders[uid];
        if (Array.isArray(arr)) {
            arr.forEach(o => {
                let it = Object.assign({}, o);
                it.user_id = uid;
                if (!it.status || !it.status.trim()) it.status = 'قيد المعالجة';
                globalOrders.push(it);
            });
        }
    }
    globalOrders.sort((a,b) => String(b.date||'').localeCompare(String(a.date||'')));
    const tb = document.getElementById('ordersBody');
    tb.innerHTML = '';
    if (!globalOrders.length) {
        tb.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">لا توجد طلبات</td></tr>';
    } else {
        globalOrders.forEach((o, i) => {
            let st = (o.status || 'قيد المعالجة').trim();
            let cls = 'badge-warning', ic = '<i class="fa-solid fa-hourglass-half"></i>';
            if (st === 'مقبول' || st === 'accept') { cls = 'badge-success'; ic = '<i class="fa-solid fa-check"></i>'; }
            else if (st === 'مرفوض' || st === 'reject') { cls = 'badge-danger'; ic = '<i class="fa-solid fa-xmark"></i>'; }
            let tr = document.createElement('tr');
            tr.setAttribute('data-status', st);
            tr.setAttribute('onclick', 'openOrderModal('+i+')');
            tr.innerHTML = `
                <td><code>${o.order_number||'---'}</code></td>
                <td><code>${o.user_id||'---'}</code></td>
                <td><strong>${escapeHtml(o.product_name||'---')}</strong></td>
                <td>${escapeHtml(o.category_name||'---')}</td>
                <td><code>${o.player_id||'---'}</code></td>
                <td><strong style="color:#10b981">$${o.price||0}</strong></td>
                <td><span class="badge ${cls}">${ic} ${st}</span></td>
                <td style="color:#94a3b8;font-size:12px">${o.date||'---'}</td>
            `;
            tb.appendChild(tr);
        });
    }
    renderSections();
    renderDeposits();
    populateEditSectionSelect();
}

// ================== عرض الأقسام بشكل هرمي ==================
function renderSections() {
    const secs = botData.sections || [];
    const box = document.getElementById('sectionsDisplay');
    if (!secs.length) { box.innerHTML = 'لا يوجد أقسام.'; return; }

    let html = '';
    
    function renderSectionRecursive(s, path, depth) {
        let prods = s.products || [];
        let subs = s.sub_categories || [];
        let colorD = s.color === 'red' ? '🟥' : s.color === 'blue' ? '🟦' : '🟩';
        let apiTag = s.is_api ? '<span class="badge badge-success">API</span>' : '<span class="badge badge-warning">يدوي</span>';
        let indent = depth > 0 ? `padding-right:${depth * 20}px;` : '';
        let icon = depth === 0 ? 'fa-folder-open' : 'fa-folder';
        let iconColor = depth === 0 ? 'var(--primary)' : 'var(--warning)';
        
        let itemId = 'accItem_' + path.replace(/\./g, '_');
        let totalNested = countNestedProds(s);
        
        html += `
            <div class="sec-accordion-item" id="${itemId}" style="${indent}">
                <div class="sec-accordion-header" onclick="toggleAccordion('${itemId}')">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                        <i class="fa-solid ${icon}" style="color:${iconColor}"></i>
                        <span>${escapeHtml(s.name)}</span>
                        <span class="tree-stat">${prods.length} منتج / ${subs.length} قسم فرعي${totalNested > prods.length ? ' (الإجمالي: '+totalNested+')' : ''}</span>
                        ${apiTag}
                    </div>
                    <div style="display:flex;align-items:center;gap:10px">
                        <span style="font-size:11px;background:rgba(255,255,255,.06);padding:3px 8px;border-radius:5px">${colorD}</span>
                        <button style="background:none;border:none;color:#ef4444;cursor:pointer" onclick="event.stopPropagation();deleteSectionByPath('${path}')"><i class="fa-solid fa-trash"></i></button>
                        <i class="fa-solid fa-chevron-down" style="font-size:12px"></i>
                    </div>
                </div>
                <div class="sec-accordion-body">
                    <div class="vertical-products-list">
        `;
        
        if (!prods.length && !subs.length) {
            html += '<p style="color:var(--text-muted);font-size:12px;padding:10px">لا توجد عناصر.</p>';
        } else {
            if (subs.length) {
                html += '<div style="margin-bottom:10px"><strong style="color:var(--primary);font-size:13px">الأقسام الفرعية:</strong></div>';
                subs.forEach((sc, sIdx) => {
                    renderSectionRecursive(sc, path + '.' + sIdx, depth + 1);
                });
                if (prods.length) {
                    html += '<div style="margin:15px 0 10px"><strong style="color:var(--primary);font-size:13px">المنتجات المباشرة:</strong></div>';
                }
            }
            prods.forEach((p, pi) => {
                let cats = (p.categories || []).length + (p.counter_categories || []).length + (p.stock_categories || []).length;
                html += `
                    <div class="vertical-product-card">
                        <div style="display:flex;align-items:center;gap:12px">
                            <i class="fa-solid fa-box" style="color:var(--primary)"></i>
                            <div>
                                <strong style="color:#fff;font-size:14px">${escapeHtml(p.name)}</strong>
                                <div style="font-size:11px;color:var(--text-muted)">ID: ${p.id} • ${cats} فئة</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:15px">
                            <strong style="color:#10b981">$${p.price||0}</strong>
                            <button style="background:none;border:none;color:#ef4444;cursor:pointer" onclick="deleteProductFromSectionByPath('${path}',${pi})"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    </div>
                `;
            });
        }
        html += '</div></div></div>';
    }
    
    function countNestedProds(s) {
        let c = (s.products || []).length;
        (s.sub_categories || []).forEach(sc => { c += countNestedProds(sc); });
        return c;
    }
    
    secs.forEach((s, i) => {
        renderSectionRecursive(s, String(i), 0);
    });
    box.innerHTML = html;
}

function toggleAccordion(itemId){
    let e = document.getElementById(itemId);
    if(e) e.classList.toggle('active');
}

function getSectionByPath(path) {
    let parts = path.split('.').map(x => parseInt(x));
    let current = botData.sections;
    let obj = null;
    for (let i = 0; i < parts.length; i++) {
        if (!current || !current[parts[i]]) return null;
        obj = current[parts[i]];
        current = obj.sub_categories;
    }
    return obj;
}

function deleteProductFromSectionByPath(path, pi) {
    if (!confirm("حذف المنتج؟")) return;
    let sec = getSectionByPath(path);
    if (!sec) return;
    sec.products.splice(pi, 1);
    renderSections();
    saveDataToServerSilent();
}

function deleteSectionByPath(path) {
    if (!confirm("حذف القسم بكل ما فيه؟")) return;
    let parts = path.split('.').map(x => parseInt(x));
    if (parts.length === 1) {
        botData.sections.splice(parts[0], 1);
    } else {
        let parentPath = parts.slice(0, -1).join('.');
        let lastIdx = parts[parts.length - 1];
        let parent = getSectionByPath(parentPath);
        if (parent && parent.sub_categories) {
            parent.sub_categories.splice(lastIdx, 1);
        }
    }
    renderSections();
    populateEditSectionSelect();
    saveDataToServerSilent();
}

function addNewSection() {
    if (!botData) return alert("حمّل الملف");
    let n = document.getElementById('newSectionName').value.trim();
    let e = document.getElementById('newSectionEmoji').value.trim() || "5958451234032589521";
    let d = document.getElementById('newSectionDesc').value.trim() || "شحن";
    if (!n) return alert("اكتب الاسم");
    if (!botData.sections) botData.sections = [];
    botData.sections.push({name:n, emoji_id:e, color:"green", description:d, sub_categories:[], products:[]});
    document.getElementById('newSectionName').value='';
    renderSections(); 
    populateEditSectionSelect();
    saveDataToServerSilent();
}

function renderDeposits() {
    const d = botData.deposit_methods || [];
    const b = document.getElementById('depositsListDisplay');
    if (!d.length) { b.innerHTML = 'لا توجد طرق إيداع.'; return; }
    let h = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:15px">';
    d.forEach(x => { h += `<div style="background:var(--box-bg);padding:15px;border-radius:10px;border:1px solid var(--border)"><strong>${escapeHtml(x.name)}</strong><p style="color:var(--text-muted);font-size:12px;margin-top:4px">${escapeHtml(x.address||'---')}</p><p style="color:#10b981;font-size:12px">الصرف: ${escapeHtml(x.rate||'1')}</p></div>`; });
    h += '</div>'; b.innerHTML = h;
}

function modifyBalance(t) {
    if (!botData) return alert("حمّل الملف");
    let u = document.getElementById('chargeUserId').value.trim();
    let a = parseFloat(document.getElementById('chargeAmount').value);
    if (!u || isNaN(a) || a <= 0) return alert("أدخل قيم");
    if (!botData.users) botData.users = {};
    if (!botData.users[u]) botData.users[u] = {balance:0, vip:"عادي", whatsapp_phone:""};
    let c = parseFloat(botData.users[u].balance || 0);
    if (t === 'add') botData.users[u].balance = c + a;
    else { if (c < a) return alert("رصيد غير كافي"); botData.users[u].balance = c - a; }
    renderAllData(); saveDataToServerSilent();
}

function toggleBan(t) {
    if (!botData) return alert("حمّل الملف");
    let u = parseInt(document.getElementById('banUserId').value.trim());
    if (!u) return alert("أدخل آيدي");
    if (!botData.banned_users) botData.banned_users = [];
    let i = botData.banned_users.indexOf(u);
    if (t === 'ban') { if (i === -1) botData.banned_users.push(u); }
    else { if (i !== -1) botData.banned_users.splice(i, 1); }
    saveDataToServerSilent();
}

function updateProfit(){if(!botData)return alert("حمّل الملف");botData.profit_percentage=parseFloat(document.getElementById('profitPercentageInput').value)||0;saveDataToServerSilent();alert("تم التحديث")}
function updateGeneralSettings(){if(!botData)return alert("حمّل");botData.required_channel=document.getElementById('botChannelInput').value.trim();botData.bot_news_link=document.getElementById('botNewsInput').value.trim();botData.bot_support_link=document.getElementById('botSupportInput').value.trim();saveDataToServerSilent();alert("تم الحفظ")}
function updateWelcomeText(){if(!botData)return alert("حمّل");botData.welcome_text=document.getElementById('welcomeTextInput').value;saveDataToServerSilent();alert("تم الحفظ")}

function exportUpdatedJson() {
    if (!botData) return alert("لا بيانات");
    const b = new Blob([JSON.stringify(botData,null,2)], {type:"application/json"});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = "data.jshon"; a.click();
}

function liveFilter() {
    let v = document.getElementById("searchInput").value.toLowerCase();
    let s = document.getElementById("statusSelect").value;
    document.querySelectorAll("#ordersBody tr").forEach(r => {
        let t = r.innerText.toLowerCase();
        let rs = r.getAttribute("data-status");
        r.style.display = (t.includes(v) && (s==="all" || rs===s)) ? "" : "none";
    });
}

function openOrderModal(i) {
    let d = globalOrders[i]; if (!d) return;
    document.getElementById('mProduct').innerText = d.product_name || '---';
    document.getElementById('mUserId').innerText = d.user_id || '---';
    document.getElementById('mOrderNum').innerText = d.order_number || '---';
    document.getElementById('mCategory').innerText = d.category_name || '---';
    document.getElementById('mPrice').innerText = '$' + (d.price||0);
    document.getElementById('mDate').innerText = d.date || '---';
    document.getElementById('mPlayerId').innerText = d.player_id || '---';
    let st = d.status || 'قيد المعالجة';
    let b = '<span class="badge badge-warning">قيد المعالجة</span>';
    if (st === 'مقبول' || st === 'accept') b = '<span class="badge badge-success">تم</span>';
    else if (st === 'مرفوض' || st === 'reject') b = '<span class="badge badge-danger">مرفوض</span>';
    document.getElementById('mStatusBadge').innerHTML = b;
    document.getElementById('orderModal').style.display = 'flex';
}

function closeModal(e){if(e.target.id==='orderModal')document.getElementById('orderModal').style.display='none'}
function copyText(id){navigator.clipboard.writeText(document.getElementById(id).innerText);alert('تم النسخ')}

function showRawCurrent() {
    let current = navigationStack[navigationStack.length - 1];
    if (!current) return alert("ما في مستوى محدد");
    const c = document.getElementById('apiCategoriesContainer');
    c.innerHTML = '<p class="loading"><i class="fa-solid fa-spinner fa-spin"></i> جاري تحميل /content/' + current.id + '...</p>';
    document.getElementById('apiCurrentTitle').style.display = 'none';
    document.getElementById('breadcrumbArea').style.display = 'none';
    fetchContent(current.id).then(d => {
        c.innerHTML = '<div class="raw-json">' + escapeHtml(JSON.stringify(d,null,2)) + '</div>';
    }).catch(e => {
        c.innerHTML = '<p class="loading" style="color:var(--danger)">' + escapeHtml(e.message) + '</p>';
    });
}

// ================== تعديل الأقسام (جديد) ==================
function collectAllSections() {
    let list = [];
    if (!botData || !botData.sections) return list;
    
    function walk(sections, basePath) {
        sections.forEach((s, i) => {
            let currentPath = basePath ? (basePath + '.' + i) : String(i);
            list.push({
                path: currentPath,
                name: s.name || 'بدون اسم',
                emoji_id: s.emoji_id || '5958451234032589521',
                depth: basePath ? basePath.split('.').length : 0,
                is_api: !!s.is_api
            });
            if (Array.isArray(s.sub_categories)) {
                walk(s.sub_categories, currentPath);
            }
        });
    }
    walk(botData.sections, '');
    return list;
}

function populateEditSectionSelect() {
    let sel = document.getElementById('editSectionSelect');
    if (!sel) return;
    let currentVal = sel.value;
    let sections = collectAllSections();
    let html = '<option value="">-- اختر القسم --</option>';
    sections.forEach(s => {
        let indent = '— '.repeat(s.depth);
        let apiTag = s.is_api ? ' [API]' : ' [يدوي]';
        html += `<option value="${s.path}">${indent}${escapeHtml(s.name)}${apiTag} (${s.path})</option>`;
    });
    sel.innerHTML = html;
    if (currentVal && sections.some(s => s.path === currentVal)) {
        sel.value = currentVal;
    }
}

function openEditSectionModal() {
    if (!botData) return alert("حمّل الملف أولاً");
    if (!botData.sections || !botData.sections.length) return alert("لا توجد أقسام لتعديلها");
    populateEditSectionSelect();
    document.getElementById('editSectionNewName').value = '';
    document.getElementById('editSectionEmoji').value = '5958451234032589521';
    document.getElementById('editSectionPreview').innerHTML = '<i class="fa-solid fa-info-circle"></i> اختر قسماً لعرض معلوماته الحالية';
    document.getElementById('editSectionModal').style.display = 'flex';
}

function closeEditSectionModal(e) {
    if (!e || e.target.id === 'editSectionModal') {
        document.getElementById('editSectionModal').style.display = 'none';
    }
}

function onEditSectionSelectChange() {
    let path = document.getElementById('editSectionSelect').value;
    let preview = document.getElementById('editSectionPreview');
    if (!path) {
        preview.innerHTML = '<i class="fa-solid fa-info-circle"></i> اختر قسماً لعرض معلوماته الحالية';
        return;
    }
    let sec = getSectionByPath(path);
    if (!sec) {
        preview.innerHTML = '<span style="color:#ef4444">القسم غير موجود</span>';
        return;
    }
    document.getElementById('editSectionNewName').value = sec.name || '';
    document.getElementById('editSectionEmoji').value = sec.emoji_id || '5958451234032589521';
    let subsCount = (sec.sub_categories || []).length;
    let prodsCount = (sec.products || []).length;
    let typeTag = sec.is_api ? '<span style="color:#10b981">API</span>' : '<span style="color:#f59e0b">يدوي</span>';
    let colorEmoji = sec.color === 'red' ? '🟥' : sec.color === 'blue' ? '🟦' : '🟩';
    preview.innerHTML = `
        <div style="margin-bottom:6px"><strong>الاسم الحالي:</strong> ${escapeHtml(sec.name || '-')}</div>
        <div style="margin-bottom:6px"><strong>الإيموجي الحالي:</strong> <code>${escapeHtml(sec.emoji_id || '-')}</code></div>
        <div style="margin-bottom:6px"><strong>النوع:</strong> ${typeTag} ${colorEmoji}</div>
        <div><strong>المحتوى:</strong> ${subsCount} قسم فرعي • ${prodsCount} منتج</div>
    `;
}

function saveEditedSection() {
    if (!botData) return alert("حمّل الملف أولاً");
    let path = document.getElementById('editSectionSelect').value;
    if (!path) return alert("اختر القسم أولاً");
    
    let newName = document.getElementById('editSectionNewName').value.trim();
    let newEmoji = document.getElementById('editSectionEmoji').value.trim();
    
    if (!newName) return alert("اكتب اسم القسم الجديد");
    if (!newEmoji) return alert("اكتب إيموجي البريميوم");
    
    let sec = getSectionByPath(path);
    if (!sec) return alert("القسم غير موجود");
    
    let oldName = sec.name;
    sec.name = newName;
    sec.emoji_id = newEmoji;
    
    // تحديث إيموجي المنتجات بداخل هذا القسم إن وجدت
    function updateProductsEmoji(section) {
        (section.products || []).forEach(p => {
            if (!p.emoji_id || p.emoji_id === '5958451234032589521') {
                p.emoji_id = newEmoji;
            }
            if (!p.premium_emoji || p.premium_emoji === '5958451234032589521') {
                p.premium_emoji = newEmoji;
            }
        });
        (section.sub_categories || []).forEach(updateProductsEmoji);
    }
    updateProductsEmoji(sec);
    
    renderSections();
    populateEditSectionSelect();
    saveDataToServerSilent();
    
    document.getElementById('editSectionPreview').innerHTML = `
        <i class="fa-solid fa-check" style="color:#10b981"></i> 
        تم التحديث بنجاح: <strong>${escapeHtml(oldName)}</strong> ← <strong>${escapeHtml(newName)}</strong>
    `;
    
    setTimeout(() => {
        alert(`✅ تم حفظ التعديلات بنجاح\nالاسم الجديد: ${newName}\nالإيموجي: ${newEmoji}`);
    }, 100);
}

function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
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

        if self.path.startswith('/fetch-external-api'):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            ep = qs.get('endpoint', ['products'])[0]
            if ep == 'content':
                cid = qs.get('id', ['0'])[0]
                url = f"{API_BASE}/content/{cid}"
            else:
                url = f"{API_BASE}/products"
            headers = {"api-token": API_TOKEN, "User-Agent": "Mozilla/5.0"}
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as r:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(r.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "code": e.code}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGE_HTML.encode('utf-8'))

    def do_POST(self):
        if self.path == '/save-data':
            cl = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(cl)
            try:
                j = json.loads(data.decode('utf-8'))
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(j, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"OK")
            except:
                self.send_response(500)
                self.end_headers()
            return

        if self.path == '/create-api-order':
            cl = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(cl)
            try:
                payload = json.loads(data.decode('utf-8'))
                pid = payload.get('product_id')
                qty = payload.get('qty', 1)
                player = payload.get('playerId', 'test')
                extra = payload.get('extra_params', {})
                order_uuid = str(uuid.uuid4())
                params = {'qty': qty, 'playerId': player, 'order_uuid': order_uuid}
                for k,v in extra.items():
                    if k not in params: params[k] = v
                url = f"{API_BASE}/newOrder/{pid}/params?" + urllib.parse.urlencode(params)
                headers = {"api-token": API_TOKEN, "User-Agent": "Mozilla/5.0"}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as r:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(r.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "code": e.code}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        self.send_response(200)
        self.end_headers()


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), BotServer)
    print(f"🚀 السيرفر يعمل على المنفذ {PORT}")
    server.serve_forever()