const jwt = require('jsonwebtoken');
const { createClient } = require('@supabase/supabase-js');

const JWT_SECRET = 'mid-east-exchange-secret-2026';
const SUPABASE_URL = 'https://mezvbnvfthnvzgpwjejq.supabase.co';
const SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lenZibnZmdGhudnpncHdqZWpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDUxMDEzNywiZXhwIjoyMDkwMDg2MTM3fQ.x-eaefov6tJfUQ86tgTS2OXO5jjCKEnEjOcpP_6ogj8';

const supabase = createClient(SUPABASE_URL, SERVICE_KEY);

// Plain Node.js response helpers
function json(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type,Authorization', 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS' });
  res.end(JSON.stringify(data));
}
function ok(res, data) { return json(res, 200, data); }
function err(res, code, msg) { return json(res, code, { error: msg }); }

// Supabase REST helpers (bypasses RLS)
async function sbUpdate(table, id, body) {
  return fetch(`${SUPABASE_URL}/rest/v1/${table}?id=eq.${id}`, {
    method: 'PATCH',
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}`, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
    body: JSON.stringify(body)
  });
}
async function sbGet(table, query) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}` }
  });
  return r.json();
}
async function sbInsert(table, data) {
  return fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
    method: 'POST',
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}`, 'Content-Type': 'application/json', Prefer: 'return=representation' },
    body: JSON.stringify(data)
  }).then(r => r.json());
}

// Auth
function authUser(req) {
  const t = req.headers.authorization?.replace('Bearer ', '');
  if (!t) return null;
  try { return jwt.verify(t, JWT_SECRET); } catch { return null; }
}

// Parse body
async function parseBody(req) {
  return new Promise((resolve) => {
    let d = '';
    req.on('data', c => d += c);
    req.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({}); } });
  });
}

// Main handler
module.exports = async function handler(req, res) {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type,Authorization', 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS' });
    return res.end();
  }

  const url = req.url.split('?')[0];
  const method = req.method;
  let body = {};
  if (method === 'POST') body = await parseBody(req);

  try {
    // ===== Health =====
    if (url === '/api/health' && method === 'GET') {
      return ok(res, { status: 'ok', time: new Date().toISOString() });
    }

    // ===== Login =====
    if (url === '/api/auth/login' && method === 'POST') {
      const { username, password } = body;
      if (!username || !password) return err(res, 400, '用户名和密码必填');

      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email: `${username}@mid-east-exchange.com`, password
      });
      if (authError || !authData?.user) return err(res, 401, '用户名或密码错误');

      const users = await sbGet('users', `id=eq.${authData.user.id}&select=*`);
      const user = users?.[0];
      if (!user) return err(res, 500, '用户信息获取失败');

      const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '7d' });
      return ok(res, {
        token,
        user: { id: user.id, username: user.username, usdt: user.usdt, irr: user.irr, sar: user.sar, aed: user.aed, kwd: user.kwd, qar: user.qar, egp: user.egp, iqd: user.iqd, jod: user.jod, omr: user.omr, is_admin: user.is_admin || false }
      });
    }

    // ===== Register =====
    if (url === '/api/auth/register' && method === 'POST') {
      const { username, password, phone, ref } = body;
      if (!username || !password) return err(res, 400, '用户名和密码必填');
      if (password.length < 6) return err(res, 400, '密码至少6位');

      const exist = await sbGet('users', `username=eq.${username}&select=id`);
      if (exist?.length) return err(res, 400, '用户名已存在');

      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: `${username}@mid-east-exchange.com`, password, options: { data: { username } }
      });
      if (authError) return err(res, 400, authError.message);

      await new Promise(r => setTimeout(r, 800));
      const token = jwt.sign({ id: authData.user.id, username }, JWT_SECRET, { expiresIn: '7d' });
      return ok(res, { token, user: { id: authData.user.id, username, usdt: 0 } });
    }

    // ===== Auth required below =====
    const user = authUser(req);
    if (!user) return err(res, 401, '请先登录');

    // ===== Balance =====
    if (url === '/api/users/balance' && method === 'GET') {
      const users = await sbGet('users', `id=eq.${user.id}&select=id,username,usdt,irr,sar,aed,kwd,qar,egp,iqd,jod,omr,total_reward,is_admin`);
      return ok(res, users?.[0] || { error: '用户不存在' });
    }

    // ===== User Orders =====
    if (url === '/api/users/orders' && method === 'GET') {
      const table = new URL(req.url, 'http://localhost').searchParams.get('table');
      const valid = ['topups', 'u2l_orders', 'l2u_orders', 'withdraws'];
      if (!valid.includes(table)) return err(res, 400, '无效的表名');
      const data = await sbGet(table, `user_id=eq.${user.id}&order=created_at.desc&limit=50`);
      return ok(res, data || []);
    }

    // ===== Submit Topup =====
    if (url === '/api/orders/topup' && method === 'POST') {
      const { amount } = body;
      if (!amount || amount < 1) return err(res, 400, '金额无效');
      await sbInsert('topups', { user_id: user.id, amount, status: '待审核', created_at: new Date().toISOString() });
      return ok(res, { success: true });
    }

    // ===== Submit U2L =====
    if (url === '/api/orders/u2l' && method === 'POST') {
      const { amount, currency, speed, submit_rate, fee } = body;
      if (!amount || amount < 100) return err(res, 400, '最低100U');
      const users = await sbGet('users', `id=eq.${user.id}&select=usdt`);
      if (!users?.[0] || users[0].usdt < amount) return err(res, 400, 'USDT不足');
      await sbInsert('u2l_orders', { user_id: user.id, amount, currency: currency || 'IRR', speed: speed || '24h', submit_rate: submit_rate || 435934.6, fee: fee || 0.03, status: '待审核', created_at: new Date().toISOString() });
      return ok(res, { success: true });
    }

    // ===== Submit L2U =====
    if (url === '/api/orders/l2u' && method === 'POST') {
      const { amount, currency, speed, submit_rate, fee } = body;
      if (!amount || amount < 100) return err(res, 400, '最低100');
      const fld = (currency || 'IRR').toLowerCase();
      const users = await sbGet('users', `id=eq.${user.id}&select=${fld}`);
      if (!users?.[0] || (users[0][fld] || 0) < amount) return err(res, 400, currency + '余额不足');
      await sbInsert('l2u_orders', { user_id: user.id, amount, currency: currency || 'IRR', speed: speed || '24h', submit_rate: submit_rate || 435934.6, fee: fee || 0.03, status: '待审核', created_at: new Date().toISOString() });
      return ok(res, { success: true });
    }

    // ===== Submit Withdraw =====
    if (url === '/api/orders/withdraw' && method === 'POST') {
      const { amount, address } = body;
      if (!amount || amount < 10) return err(res, 400, '最低10U');
      if (!address || !address.startsWith('T')) return err(res, 400, '地址无效');
      const users = await sbGet('users', `id=eq.${user.id}&select=usdt`);
      if (!users?.[0] || users[0].usdt < amount) return err(res, 400, 'USDT不足');
      const pending = await sbGet('withdraws', `user_id=eq.${user.id}&status=eq.待处理&select=id&limit=1`);
      if (pending?.length) return err(res, 400, '已有待处理提现');
      await sbInsert('withdraws', { user_id: user.id, amount, address, status: '待处理', created_at: new Date().toISOString() });
      return ok(res, { success: true });
    }

    // ===== Admin: Get Orders =====
    if (url.startsWith('/api/admin/orders/') && method === 'GET') {
      if (user.username !== 'a2022120') return err(res, 403, '无权限');
      const table = url.split('/api/admin/orders/')[1];
      const valid = ['topups', 'u2l_orders', 'l2u_orders', 'withdraws'];
      if (!valid.includes(table)) return err(res, 400, '无效的表名');
      const status = table === 'withdraws' ? '待处理' : '待审核';
      const orders = await sbGet(table, `status=eq.${status}&order=created_at.desc`);
      // Enrich with usernames
      if (orders?.length) {
        const userIds = [...new Set(orders.map(o => o.user_id))];
        const allUsers = await sbGet('users', `id=in.(${userIds.join(',')})&select=id,username`);
        const umap = {}; allUsers?.forEach(u => umap[u.id] = u.username);
        orders.forEach(o => o.users = { username: umap[o.user_id] || '--' });
      }
      return ok(res, orders || []);
    }

    // ===== Admin: Approve =====
    if (url === '/api/admin/approve' && method === 'POST') {
      if (user.username !== 'a2022120') return err(res, 403, '无权限');
      const { table, id } = body;
      const valid = ['topups', 'u2l_orders', 'l2u_orders', 'withdraws'];
      if (!valid.includes(table)) return err(res, 400, '无效的表名');

      const orders = await sbGet(table, `id=eq.${id}&select=*`);
      const order = orders?.[0];
      if (!order) return err(res, 404, '订单不存在');
      if (order.status !== '待审核' && order.status !== '待处理') return err(res, 400, '订单已处理');

      const upd = await sbUpdate(table, id, { status: '已通过' });
      if (!upd.ok) return err(res, 500, '更新失败');

      // Update balance
      const uid = order.user_id;
      const users = await sbGet('users', `id=eq.${uid}&select=*`);
      const u = users?.[0];
      if (u) {
        let bu = {};
        if (table === 'topups') {
          bu = { usdt: (u.usdt || 0) + Number(order.amount) };
        } else if (table === 'u2l_orders') {
          const fld = (order.currency || 'IRR').toLowerCase();
          const amt = Number(order.amount) * Number(order.submit_rate || 1) * (1 - Number(order.fee || 0));
          bu = { [fld]: Math.max(0, (u[fld] || 0) + amt) };
        } else if (table === 'l2u_orders') {
          const fld = (order.currency || 'IRR').toLowerCase();
          const amt = Number(order.amount) / Number(order.submit_rate || 1) * (1 - Number(order.fee || 0));
          bu = { usdt: (u.usdt || 0) + amt, [fld]: Math.max(0, (u[fld] || 0) - Number(order.amount)) };
        } else if (table === 'withdraws') {
          bu = { usdt: Math.max(0, (u.usdt || 0) - Number(order.amount)) };
        }
        if (Object.keys(bu).length) await sbUpdate('users', uid, bu);
      }
      return ok(res, { success: true });
    }

    // ===== Admin: Reject =====
    if (url === '/api/admin/reject' && method === 'POST') {
      if (user.username !== 'a2022120') return err(res, 403, '无权限');
      const { table, id } = body;
      await sbUpdate(table, id, { status: '已驳回' });
      return ok(res, { success: true });
    }

    return err(res, 404, 'Not found');
  } catch (e) {
    console.error('API Error:', e);
    return err(res, 500, e.message);
  }
};
