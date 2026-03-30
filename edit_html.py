#!/usr/bin/env python3
import re

path = '/Users/wu/.openclaw/workspace/mid-east-exchange-web/index.html'
with open(path) as f:
    html = f.read()

# 1. Add position:relative to login-box
html = html.replace(
    'class="login-box"',
    'class="login-box" style="position:relative"'
)

# 2. Add id="siteTitle" to login-title
html = html.replace(
    '<div class="login-title">中东货币兑换</div>',
    '<div class="login-title" id="siteTitle">中东货币兑换</div>'
)

# 3. Add language selector after login-box div opening
# Find: <div class="login-box" style="position:relative">
# Insert language selector right after the opening div
html = html.replace(
    '<div class="login-box" style="position:relative">\n    <div class="login-title"',
    '''<div class="login-box" style="position:relative">
    <select id="langSel" onchange="setLang(this.value)" style="width:auto;padding:8px 12px;font-size:12px;background:rgba(0,0,0,.4);border:1px solid var(--border);color:#fff;border-radius:10px;cursor:pointer;position:absolute;top:16px;right:16px">
      <option value="zh">🇨🇳 中文</option>
      <option value="en">🇬🇧 English</option>
      <option value="ar">🇸🇦 العربية</option>
    </select>
    <div class="login-title"'''
)

# 4. Update login inputs with IDs and placeholders
html = html.replace(
    '<div class="field"><label>账号</label><input id="login_user" oninput="validateLogin()" placeholder="纯字母数字，不要带@"></div>',
    '<div class="field"><label id="l_lbl1">账号</label><input id="login_user" oninput="validateLogin()" placeholder="Username (letters+punctuation)"></div>'
)
html = html.replace(
    '<div class="field"><label>密码</label><input type="password" id="login_pwd" oninput="validateLogin()" placeholder="至少6位"></div>',
    '<div class="field"><label id="l_lbl2">密码</label><input type="password" id="login_pwd" oninput="validateLogin()" placeholder="Password (8+ letters+punctuation)"></div>'
)

# 5. Update reg inputs with IDs, regHint, and placeholders
# Add regHint before reg_user
html = html.replace(
    '<div class="field"><label>账号</label><input id="reg_user" oninput="validateReg()" placeholder="输入用户名（不用写邮箱）"></div>',
    '<div class="field"><div id="regHint" style="font-size:12px;color:var(--gold);margin-bottom:8px;display:none"></div><label id="r_lbl1">账号</label><input id="reg_user" oninput="validateReg()" placeholder="Username (letters+punctuation)"></div>'
)
html = html.replace(
    '<div class="field"><label>密码</label><input type="password" id="reg_pwd" oninput="validateReg()" placeholder="至少6位"></div>',
    '<div class="field"><label id="r_lbl2">密码</label><input type="password" id="reg_pwd" oninput="validateReg()" placeholder="Password (8+ letters+punctuation)"></div>'
)

# 6. Update validateLogin function
old_validateLogin = '''function validateLogin(){ btn_login.disabled=!(login_user.value.trim() && login_pwd.value.trim().length>=6); }'''
new_validateLogin = '''function validateLogin(){
  const u=login_user.value.trim(), p=login_pwd.value.trim();
  const uOk=/[A-Za-z]/.test(u) && /[!@#$%^&*(),.?":{}|<>]/.test(u) && u.length>=3;
  const pOk=/[A-Za-z]/.test(p) && /[!@#$%^&*(),.?":{}|<>]/.test(p) && p.length>=8;
  btn_login.disabled=!(uOk && pOk);
}'''
html = html.replace(old_validateLogin, new_validateLogin)

# 7. Update validateReg function
old_validateReg = '''function validateReg(){ btn_reg.disabled=!(reg_user.value.trim() && reg_pwd.value.trim().length>=6); }'''
new_validateReg = '''function validateReg(){
  const u=reg_user.value.trim().replace(/@.+$/,'').replace(/[^a-zA-Z0-9!@#$%^&*(),.?":{}|<>]/g,'');
  const p=reg_pwd.value.trim();
  const uOk=/[A-Za-z]/.test(u) && /[!@#$%^&*(),.?":{}|<>]/.test(u) && u.length>=3;
  const pOk=/[A-Za-z]/.test(p) && /[!@#$%^&*(),.?":{}|<>]/.test(p) && p.length>=8;
  btn_reg.disabled=!(uOk && pOk);
  regHint.style.display=uOk?'none':'block';
  regHint.innerText=u.length<3?'用户名至少3位':(!uOk?'用户名需字母+标点':'');
}'''
html = html.replace(old_validateReg, new_validateReg)

# 8. Add LANG object and setLang before window.onload
lang_obj = '''const LANG={
  zh:{title:'中东货币兑换',sub:'USDT ↔ 中东本地货币 · 双向实时兑换',tabL:'登录',tabR:'注册',l1:'账号',l2:'密码',pU:'用户名(字母+标点)',pP:'密码(8位字母+标点)',btnL:'登录',btnR:'注册',w:'💰 钱包',t:'💵 充值',u2:'💱 购汇',l2:'💰 售汇',wd:'🏧 提现',o:'📋 订单',a:'⚙️ 管理',sdt:'USDT',addr:'0x2395d729411aF3a4D8f9FBe5ad76B8A052aeD2A8',min10:'充值金额(≥10)',submit:'提交',min100:'最低100U',uamt:'USDT数量',lamt:'当地货币数量',waddr:'TRC20地址(以T开头)',orders:'📋 我的订单',ok:'已通过',err:'操作失败',con:'已连接',out:'退出',refErr:'用户名需3位+字母+标点',pwdErr:'密码需8位+字母+标点'},
  en:{title:'Mid-East Exchange',sub:'USDT ↔ Middle East · Real-time',tabL:'Login',tabR:'Register',l1:'Account',l2:'Password',pU:'Username (letters+punctuation)',pP:'Password (8+ letters+punctuation)',btnL:'Login',btnR:'Register',w:'💰 Wallet',t:'💵 Top Up',u2:'💱 Buy',l2:'💰 Sell',wd:'🏧 Withdraw',o:'📋 Orders',a:'⚙️ Admin',sdt:'USDT',addr:'0x2395d729411aF3a4D8f9FBe5ad76B8A052aeD2A8',min10:'Amount (≥10)',submit:'Submit',min100:'Min 100U',uamt:'USDT Amount',lamt:'Local Amount',waddr:'TRC20 address (starts T)',orders:'📋 My Orders',ok:'Approved',err:'Failed',con:'Connected',out:'Logout',refErr:'Min 3 chars with letters+punctuation',pwdErr:'Min 8 chars with letters+punctuation'},
  ar:{title:'صرف العملات',sub:'USDT ↔ عملات محلية · وقت حقيقي',tabL:'تسجيل الدخول',tabR:'التسجيل',l1:'الحساب',l2:'كلمة المرور',pU:'اسم المستخدم',pP:'كلمة المرور (8+ حروف+رموز)',btnL:'تسجيل الدخول',btnR:'التسجيل',w:'💰 المحفظة',t:'💵 الإيداع',u2:'💱 الشراء',l2:'💰 البيع',wd:'🏧 السحب',o:'📋 الطلبات',a:'⚙️ الإدارة',sdt:'USDT',addr:'0x2395d729411aF3a4D8f9FBe5ad76B8A052aeD2A8',min10:'المبلغ (≥10)',submit:'إرسال',min100:'الحد الأدنى 100U',uamt:'مبلغ USDT',lamt:'المبلغ المحلي',waddr:'عنوان TRC20 (يبدأ T)',orders:'📋 طلباتي',ok:'تمت الموافقة',err:'فشل',con:'متصل',out:'خروج',refErr:'3 أحرف + حروف + رموز',pwdErr:'8 أحرف + حروف + رموز'}
};
let curLang='zh';
function setLang(l){
  curLang=l;
  const t=LANG[l];
  document.title=t.title;
  document.getElementById('siteTitle').innerText=t.title;
  document.getElementById('loginTab').innerText=t.tabL;
  document.getElementById('regTab').innerText=t.tabR;
  document.getElementById('l_lbl1').innerText=t.l1;
  document.getElementById('l_lbl2').innerText=t.l2;
  document.getElementById('r_lbl1').innerText=t.l1;
  document.getElementById('r_lbl2').innerText=t.l2;
  login_user.placeholder=t.pU;
  login_pwd.placeholder=t.pP;
  reg_user.placeholder=t.pU;
  reg_pwd.placeholder=t.pP;
  btn_login.innerText=t.btnL;
  btn_reg.innerText=t.btnR;
  btn_login.dataset.orig=t.btnL;
  btn_reg.dataset.orig=t.btnR;
  if(document.getElementById('tab_wallet')) document.getElementById('tab_wallet').innerText=t.w;
  if(document.getElementById('tab_topup')) document.getElementById('tab_topup').innerText=t.t;
  if(document.getElementById('tab_u2l')) document.getElementById('tab_u2l').innerText=t.u2;
  if(document.getElementById('tab_l2u')) document.getElementById('tab_l2u').innerText=t.l2;
  if(document.getElementById('tab_wd')) document.getElementById('tab_wd').innerText=t.wd;
  if(document.getElementById('tab_orders')) document.getElementById('tab_orders').innerText=t.o;
  if(document.getElementById('bal_lbl')) document.getElementById('bal_lbl').innerText=t.sdt;
  if(document.getElementById('topAddrDisplay')) document.getElementById('topAddrDisplay').innerText=t.addr;
  if(document.getElementById('top_amt')) document.getElementById('top_amt').placeholder=t.min10;
  if(document.getElementById('u2l_amt')) document.getElementById('u2l_amt').placeholder=t.uamt;
  if(document.getElementById('wd_addr')) document.getElementById('wd_addr').placeholder=t.waddr;
  if(document.getElementById('orderTitle')) document.getElementById('orderTitle').innerText=t.orders;
  document.documentElement.dir=l==='ar'?'rtl':'ltr';
  document.documentElement.lang=l;
}
'''

# Insert before window.onload
html = html.replace(
    "window.onload=()=>{ init(); fetchRates();",
    lang_obj + "\nwindow.onload=()=>{ init(); fetchRates();"
)

# 9. Wrap main content cards in page sections
# Replace each card with id wrapper
# page_wallet
html = html.replace(
    '<!-- Wallet card -->\n    <div class="card" id="page_wallet"',
    '<!-- Wallet card -->\n    <div id="page_wallet" style="display:block">\n    <div class="card"'
)
# Fix the closing - add wrapper close after each card
# The wallet card ends before "<!-- Rate card -->" - need to close the div
html = html.replace(
    '''    </div>

    <!-- Rate card -->
    <div class="card" id="page_rates">''',
    '''    </div>
    </div>

    <!-- Rate card -->
    <div id="page_rates" style="display:block">
    <div class="card">'''
)

# Fix rate card closing
html = html.replace(
    '''    </div>

    <!-- Topup card -->
    <div class="card" id="page_topup"''',
    '''    </div>
    </div>

    <!-- Topup card -->
    <div id="page_topup" style="display:none">
    <div class="card">'''
)

# Fix topup card closing
html = html.replace(
    '''      <button class="btn-sm" onclick="safeSubmitTopup()">提交充值申请</button>
    </div>

    <!-- USD to Local card -->''',
    '''      <button class="btn-sm" onclick="safeSubmitTopup()">提交充值申请</button>
    </div>
    </div>

    <!-- USD to Local card -->'''
)

# Fix u2l card
html = html.replace(
    '''    <!-- USD to Local card -->
    <div class="card" id="page_u2l"''',
    '''    <!-- USD to Local card -->
    <div id="page_u2l" style="display:none">
    <div class="card"'''
)

html = html.replace(
    '''      <button class="btn-sm" onclick="safeSubmitU2L()">提交兑换</button>
    </div>

    <!-- Local to USD card -->''',
    '''      <button class="btn-sm" onclick="safeSubmitU2L()">提交兑换</button>
    </div>
    </div>

    <!-- Local to USD card -->'''
)

# Fix l2u card
html = html.replace(
    '''    <!-- Local to USD card -->
    <div class="card" id="page_l2u"''',
    '''    <!-- Local to USD card -->
    <div id="page_l2u" style="display:none">
    <div class="card"'''
)

html = html.replace(
    '''      <button class="btn-sm" onclick="safeSubmitL2U()">提交兑换</button>
    </div>

    <!-- Withdraw card -->''',
    '''      <button class="btn-sm" onclick="safeSubmitL2U()">提交兑换</button>
    </div>
    </div>

    <!-- Withdraw card -->'''
)

# Fix wd card
html = html.replace(
    '''    <!-- Withdraw card -->
    <div class="card" id="page_wd"''',
    '''    <!-- Withdraw card -->
    <div id="page_wd" style="display:none">
    <div class="card"'''
)

html = html.replace(
    '''      <button id="btn_wd" class="btn-sm" onclick="safeSubmitWD()" disabled>提交提现</button>
    </div>

    <!-- Orders card -->''',
    '''      <button id="btn_wd" class="btn-sm" onclick="safeSubmitWD()" disabled>提交提现</button>
    </div>
    </div>

    <!-- Orders card -->'''
)

# Fix orders card - it uses grid-column span
html = html.replace(
    '''    <!-- Orders card -->
    <div class="card" id="page_orders"''',
    '''    <!-- Orders card -->
    <div id="page_orders" style="display:none;grid-column:1/-1">
    <div class="card"'''
)

html = html.replace(
    '''      <div id="order_list" class="order-list"></div>
    </div>

    <!-- Admin card''',
    '''      <div id="order_list" class="order-list"></div>
    </div>
    </div>

    <!-- Admin card'''
)

# Fix admin card
html = html.replace(
    '''    <!-- Admin card (only visible to admin) -->
    <div id="page_admin" style="display:none">
    <div id="adminCard" class="card" style="grid-column:1 / -1">''',
    '''    <!-- Admin card (only visible to admin) -->
    <div id="page_admin" style="display:none;grid-column:1/-1">
    <div id="adminCard" class="card">'''
)

# Close the admin wrapper
html = html.replace(
    '''      <div id="admin_content" class="order-list"></div>
    </div>
    </div>
  </div>
</div>''',
    '''      <div id="admin_content" class="order-list"></div>
    </div>
    </div>
  </div>
</div>'''
)

with open(path, 'w') as f:
    f.write(html)

print(f"Done! Line count: {len(html.splitlines())}")