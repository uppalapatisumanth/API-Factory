
HTML_REPORT_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report</title>
    <style>
        :root {
            --bg-color: #1e1e1e;
            --sidebar-bg: #252526;
            --text-color: #d4d4d4;
            --accent-color: #007acc;
            --success-color: #4caf50;
            --fail-color: #f44336;
            --border-color: #3e3e42;
            --code-bg: #1e1e1e;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 300px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
        }

        .header {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .header h1 {
            margin: 0;
            font-size: 1.2rem;
            color: var(--text-color);
        }

        .stats {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            font-size: 0.9rem;
        }

        .stat-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        .stat-total { background-color: #444; }
        .stat-pass { background-color: rgba(76, 175, 80, 0.2); color: #81c784; }
        .stat-fail { background-color: rgba(244, 67, 54, 0.2); color: #e57373; }

        .search-box {
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        .search-box input {
            width: 100%;
            padding: 8px;
            background-color: #333;
            border: 1px solid var(--border-color);
            color: white;
            border-radius: 4px;
            box-sizing: border-box;
        }

        .test-list {
            flex: 1;
            overflow-y: auto;
        }

        .test-item {
            padding: 10px 20px;
            border-bottom: 1px solid var(--border-color);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background-color 0.2s;
        }

        .test-item:hover {
            background-color: #333;
        }

        .test-item.active {
            background-color: #37373d;
            border-left: 3px solid var(--accent-color);
        }

        .method-badge {
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 8px;
            font-weight: bold;
            display: inline-block;
            width: 40px;
            text-align: center;
        }

        .method-GET { background-color: rgba(97, 175, 254, 0.2); color: #61affe; }
        .method-POST { background-color: rgba(73, 204, 144, 0.2); color: #49cc90; }
        .method-PUT { background-color: rgba(252, 161, 48, 0.2); color: #fca130; }
        .method-DELETE { background-color: rgba(249, 62, 62, 0.2); color: #f93e3e; }
        .method-PATCH { background-color: rgba(80, 227, 194, 0.2); color: #50e3c2; }

        .status-icon {
            font-size: 1.2rem;
        }
        .status-pass::after { content: '✓'; color: var(--success-color); }
        .status-fail::after { content: '✗'; color: var(--fail-color); }

        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .report-header {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-color);
        }

        .report-title-row {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .url-bar {
            background-color: #333;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
            display: flex;
            align-items: center;
            flex: 1;
        }

        .tabs {
            display: flex;
            background-color: var(--sidebar-bg);
            border-bottom: 1px solid var(--border-color);
        }

        .tab {
            padding: 10px 20px;
            cursor: pointer;
            opacity: 0.7;
            border-bottom: 2px solid transparent;
        }

        .tab:hover { opacity: 1; }
        .tab.active {
            opacity: 1;
            border-bottom: 2px solid var(--accent-color);
            color: white;
        }

        .tab-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: none;
        }

        .tab-content.active { display: block; }

        .section {
            margin-bottom: 20px;
        }
        
        .section h3 {
            font-size: 0.9rem;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 8px;
        }

        pre {
            background-color: #111;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            border: 1px solid #333;
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .kv-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .kv-table td {
            padding: 6px;
            border-bottom: 1px solid #333;
        }

        .kv-key { width: 30%; color: #888; }
        .kv-val { color: #ddd; font-family: monospace; }
        
        .empty-state {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #666;
            flex-direction: column;
        }

        .assertion-pass { color: var(--success-color); }
        .assertion-fail { color: var(--fail-color); }

        .error-log {
            color:  #e57373;
            background: rgba(244, 67, 54, 0.1);
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            white-space: pre-wrap;
        }

        /* Modal */
        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            overflow: auto; 
            background-color: rgba(0,0,0,0.5); 
        }

        .modal-content {
            background-color: var(--sidebar-bg);
            margin: 15% auto; 
            padding: 20px;
            border: 1px solid #888;
            width: 80%; 
            max-width: 500px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-align: center;
        }

        .close-btn {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }

        .close-btn:hover,
        .close-btn:focus {
            color: white;
            text-decoration: none;
            cursor: pointer;
        }

        .about-icon {
            cursor: pointer;
            font-size: 1.2rem;
            color: var(--text-color);
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        .about-icon:hover { opacity: 1; }

    </style>
</head>
<body>

<div class="sidebar">
    <div class="header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h1>API Test Report</h1>
            <span class="about-icon" onclick="showAbout()" title="About">ℹ️</span>
        </div>
        <div class="stats">

            <span class="stat-badge stat-total" id="total-count">0 Total</span>
            <span class="stat-badge stat-pass" id="pass-count">0 Pass</span>
            <span class="stat-badge stat-fail" id="fail-count">0 Fail</span>
        </div>
    </div>
    <div class="search-box">
        <input type="text" id="search-input" placeholder="Filter tests..." onkeyup="filterTests()">
    </div>
    <div class="test-list" id="test-list">
        <!-- populated by js -->
    </div>
</div>

<div class="main-content">
    <div id="initial-view" class="empty-state">
        <div style="font-size: 4rem; opacity: 0.2;">📊</div>
        <h2>Select a test to view details</h2>
    </div>

    <div id="detail-view" style="display: none; height: 100%; flex-direction: column;">
        <div class="report-header">
            <h2 id="detail-name" style="margin: 0 0 10px 0;">Test Name</h2>
            <div class="report-title-row">
                <span id="detail-method" class="method-badge">GET</span>
                <div class="url-bar" id="detail-url">https://api.example.com/v1/users</div>
                <span id="detail-status" style="margin-left: 10px; font-weight: bold; color: var(--success-color);">200 OK</span>
                <span id="detail-duration" style="margin-left: 15px; color: #888; font-size: 0.9rem;">120ms</span>
            </div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('request')">Request</div>
            <div class="tab" onclick="switchTab('response')">Response</div>
            <div class="tab" onclick="switchTab('errors')">Assertions & Errors</div>
            <div class="tab" onclick="switchTab('code')">Code</div>
        </div>

        <div id="tab-request" class="tab-content active">
            <div class="section">
                <h3>Headers</h3>
                <div id="req-headers"></div>
            </div>
            <div class="section">
                <h3>Body</h3>
                <pre id="req-body"></pre>
            </div>
        </div>

        <div id="tab-response" class="tab-content">
            <div class="section">
                <h3>Headers</h3>
                <div id="res-headers"></div>
            </div>
            <div class="section">
                <h3>Body</h3>
                <pre id="res-body"></pre>
            </div>
        </div>

        <div id="tab-errors" class="tab-content">
            <div id="assertions-list"></div>
            <br>
            <div class="section" id="error-section" style="display:none;">
                <h3>Traceback / Error Log</h3>
                <div class="error-log" id="error-log"></div>
            </div>
        </div>

        <div id="tab-code" class="tab-content">
            <div class="section">
                <h3>Python Test Source</h3>
                <pre id="test-code" style="color: #d4d4d4; background: #1e1e1e; padding: 10px; border-radius: 4px; border: 1px solid #333; overflow-x: auto;"></pre>
            </div>
        </div>
    </div>
</div>

    <div id="about-modal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeAbout()">&times;</span>
            <h2>About API Test Report</h2>
            <p>Generated by <strong>XLSX to API Generator</strong></p>
            <p>Version: 1.0.0</p>
            <p>This report provides a detailed breakdown of your API test execution, including request/response details, assertions, and error logs.</p>
            <div style="margin-top: 20px; text-align: right;">
                <button onclick="closeAbout()" style="padding: 8px 16px; background: var(--accent-color); color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
            </div>
        </div>
    </div>

    <script>
        // Data is injected here by Python
        const reportData = %%REPORT_DATA%%;
    
        const testListEl = document.getElementById('test-list');
        const searchInput = document.getElementById('search-input');
        let currentData = reportData.tests;
    
        // Initialize Stats
        document.getElementById('total-count').textContent = reportData.summary.total + ' Total';
        document.getElementById('pass-count').textContent = reportData.summary.passed + ' Pass';
        document.getElementById('fail-count').textContent = reportData.summary.failed + ' Fail';
    
        function renderList(items) {
            testListEl.innerHTML = '';
            items.forEach((test, index) => {
                const el = document.createElement('div');
                el.className = 'test-item';
                el.onclick = () => showDetail(test, el);
                
                const methodClass = 'method-' + (test.method || 'GET').toUpperCase();
                const statusClass = test.status === 'passed' ? 'status-pass' : 'status-fail';
                
                el.innerHTML = `
                    <div style="display:flex; align-items:center;">
                        <span class="method-badge ${methodClass}">${test.method || '?'}</span>
                        <span style="font-weight: 500;">${test.name}</span>
                    </div>
                    <div class="${statusClass}"></div>
                `;
                testListEl.appendChild(el);
            });
        }
    
        function filterTests() {
            const query = searchInput.value.toLowerCase();
            const filtered = reportData.tests.filter(t => 
                t.name.toLowerCase().includes(query) || 
                (t.url && t.url.toLowerCase().includes(query))
            );
            renderList(filtered);
        }
    
        function showDetail(test, listEl) {
            // Highlight active item
            document.querySelectorAll('.test-item').forEach(e => e.classList.remove('active'));
            if(listEl) listEl.classList.add('active');
    
            document.getElementById('initial-view').style.display = 'none';
            document.getElementById('detail-view').style.display = 'flex';
    
            // Header
            document.getElementById('detail-name').textContent = test.name;
            document.getElementById('detail-method').textContent = test.method || 'GET';
            document.getElementById('detail-method').className = 'method-badge method-' + (test.method || 'GET').toUpperCase();
            document.getElementById('detail-url').textContent = test.url;
            
            const statusSpan = document.getElementById('detail-status');
            if (test.response_status) {
                statusSpan.textContent = test.response_status + ' ' + (test.status === 'passed' ? 'OK' : 'FAIL');
                statusSpan.style.color = test.status === 'passed' ? 'var(--success-color)' : 'var(--fail-color)';
            } else {
                statusSpan.textContent = 'ERROR';
                statusSpan.style.color = 'var(--fail-color)';
            }
            
            document.getElementById('detail-duration').textContent = (test.duration || 0).toFixed(2) + 's';
    
            // Request
            renderKV(document.getElementById('req-headers'), test.request_headers);
            document.getElementById('req-body').textContent = formatJson(test.request_body);
    
            // Response
            renderKV(document.getElementById('res-headers'), test.response_headers);
            document.getElementById('res-body').textContent = formatJson(test.response_body);
    
            // Errors / Logs
            const errSection = document.getElementById('error-section');
            const errLog = document.getElementById('error-log');
            if (test.error_log) {
                errSection.style.display = 'block';
                errLog.textContent = test.error_log;
            } else {
                errSection.style.display = 'none';
            }
            
            // Code
            const codeEl = document.getElementById('test-code');
            if (test.source_code) {
                codeEl.textContent = test.source_code;
            } else {
                codeEl.textContent = "# Source code not available";
            }
        }
    
        function renderKV(container, obj) {
            if (!obj || Object.keys(obj).length === 0) {
                container.innerHTML = '<div style="color:#666; font-style:italic;">None</div>';
                return;
            }
            let html = '<table class="kv-table">';
            for (const [k, v] of Object.entries(obj)) {
                html += `<tr><td class="kv-key">${escapeHtml(k)}</td><td class="kv-val">${escapeHtml(String(v))}</td></tr>`;
            }
            html += '</table>';
            container.innerHTML = html;
        }
    
        function formatJson(data) {
            if (!data) return '';
            if (typeof data === 'string') {
                try {
                    return JSON.stringify(JSON.parse(data), null, 2);
                } catch (e) {
                    return data;
                }
            }
            return JSON.stringify(data, null, 2);
        }
    
        function switchTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            document.querySelector(`.tab[onclick="switchTab('${tabId}')"]`).classList.add('active');
            document.getElementById('tab-' + tabId).classList.add('active');
        }
    
        function escapeHtml(unsafe) {
            if (unsafe === undefined || unsafe === null) return '';
            return unsafe.replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }
        
        // About Modal Functions
        function showAbout() {
            document.getElementById('about-modal').style.display = 'block';
        }
        
        function closeAbout() {
            document.getElementById('about-modal').style.display = 'none';
        }
        
        // Click outside to close
        window.onclick = function(event) {
            if (event.target == document.getElementById('about-modal')) {
                closeAbout();
            }
        }
    
        // Init
        renderList(reportData.tests);
    
    </script>
    </body>
    </html>
    '''
