// === Section Toggle ===
function toggleSection(h2) {
  h2.closest('.section').classList.toggle('collapsed');
}

// === Try It Panel Toggle ===
function toggleTryIt(btn) {
  const panel = btn.nextElementSibling;
  const opening = !panel.classList.contains('open');
  panel.classList.toggle('open');
  btn.textContent = opening ? 'Close' : 'Try it';
  if (opening) updateUrl(panel.querySelector('input[data-param]') || panel);
}

// === Config ===
function getConfig() {
  return {
    baseUrl: document.getElementById('baseUrl').value.replace(/\/+$/, '')
  };
}

// === URL Builder ===
function buildUrl(panel) {
  const config = getConfig();
  let path = panel.dataset.path;

  // Replace path params {key} with input values
  panel.querySelectorAll('input[data-param="path"]').forEach(input => {
    const val = input.value.trim() || `{${input.dataset.key}}`;
    path = path.replace(`{${input.dataset.key}}`, val);
  });

  // Build query string from query param inputs
  const queryParts = [];
  panel.querySelectorAll('input[data-param="query"]').forEach(input => {
    const val = input.value.trim();
    if (val) queryParts.push(`${encodeURIComponent(input.dataset.key)}=${encodeURIComponent(val)}`);
  });
  const query = queryParts.length ? '?' + queryParts.join('&') : '';

  return { fullUrl: config.baseUrl + path + query, pathWithQuery: path + query };
}

function updateUrl(el) {
  const panel = el.closest('.try-it-panel');
  if (!panel) return;
  const { fullUrl } = buildUrl(panel);
  const urlText = panel.querySelector('.url-text');
  if (urlText) urlText.textContent = fullUrl;
}

// === Auth ===
function onAuthTypeChange() {
  const type = document.getElementById('authType').value;
  const input = document.getElementById('authToken');
  const placeholders = {
    bearer: 'paste token here...',
    jwt: 'paste JWT token here...',
    basic: 'username:password (or base64 encoded)',
    apikey: 'paste API key here...',
    none: ''
  };
  input.placeholder = placeholders[type] || '';
  input.disabled = type === 'none';
  if (type === 'none') input.value = '';
}

function getHeaders(panel) {
  const token = document.getElementById('authToken').value.trim();
  const authType = document.getElementById('authType').value;
  const headers = { 'Content-Type': 'application/json' };
  if (!token || authType === 'none') return headers;
  switch (authType) {
    case 'bearer':
    case 'jwt':
      headers['Authorization'] = 'Bearer ' + token;
      break;
    case 'basic':
      const val = token.includes(':') ? btoa(token) : token;
      headers['Authorization'] = 'Basic ' + val;
      break;
    case 'apikey':
      headers['X-API-Key'] = token;
      break;
  }
  return headers;
}

// === Send Request ===
async function sendRequest(btn) {
  const panel = btn.closest('.try-it-panel');
  const method = panel.dataset.method;
  const { fullUrl } = buildUrl(panel);
  const headers = getHeaders(panel);
  const bodyEl = panel.querySelector('.try-body');
  const body = bodyEl ? bodyEl.value.trim() : null;
  const responseDiv = panel.querySelector('.try-it-response');

  btn.disabled = true;
  btn.textContent = 'Sending...';
  responseDiv.innerHTML = '';

  const t0 = performance.now();
  try {
    const opts = { method, headers };
    if (body && !['GET','HEAD'].includes(method)) opts.body = body;
    const res = await fetch(fullUrl, opts);
    const ms = Math.round(performance.now() - t0);
    const ct = res.headers.get('content-type') || '';
    let text = await res.text();
    if (ct.includes('json')) { try { text = JSON.stringify(JSON.parse(text), null, 2); } catch {} }
    const bg = res.status < 300 ? '#bbf7d0' : res.status < 500 ? '#fecaca' : '#fed7aa';
    const fg = res.status < 300 ? '#166534' : res.status < 500 ? '#991b1b' : '#7c2d12';
    responseDiv.innerHTML = `
      <div class="try-it-response-header">
        <span class="try-it-response-status" style="background:${bg};color:${fg}">${res.status} ${res.statusText}</span>
        <span class="try-it-response-time">${ms}ms</span>
      </div>
      <div class="try-it-response-body">${esc(text)}</div>`;
  } catch (err) {
    const ms = Math.round(performance.now() - t0);
    responseDiv.innerHTML = `
      <div class="try-it-response-header">
        <span class="try-it-response-status" style="background:#fecaca;color:#991b1b">Error</span>
        <span class="try-it-response-time">${ms}ms</span>
      </div>
      <div class="try-it-response-body">${esc(err.message)}\n\nCheck CORS settings or if the server is running.</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Send';
  }
}

// === Copy as curl ===
function copyCurl(btn) {
  const panel = btn.closest('.try-it-panel');
  const method = panel.dataset.method;
  const { fullUrl } = buildUrl(panel);
  const headers = getHeaders(panel);
  const bodyEl = panel.querySelector('.try-body');
  const body = bodyEl ? bodyEl.value.trim() : null;

  let curl = `curl -X ${method} '${fullUrl}'`;
  Object.entries(headers).forEach(([k, v]) => { curl += ` \\\n  -H '${k}: ${v}'`; });
  if (body && !['GET','HEAD'].includes(method)) {
    curl += ` \\\n  -d '${body.replace(/'/g, "'\\''")}'`;
  }
  navigator.clipboard.writeText(curl).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy as curl', 1500);
  });
}

// === Util ===
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// === Init ===
document.getElementById('baseUrl').addEventListener('input', () => {
  document.querySelectorAll('.try-it-panel.open').forEach(p => updateUrl(p));
});
