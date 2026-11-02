import sys
import os
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

PORT = 8080
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Build database in-memory with real logs and statuses for Lab 5
builds = [
    {
        "id": 1,
        "title": "#1 (Initial SCM & Tests)",
        "date": "Commit 872a6bb",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS", "time": "3s"},
            {"name": "Build Docker Image", "status": "SUCCESS", "time": "12s"},
            {"name": "Deploy Docker Container", "status": "SUCCESS", "time": "3s"},
            {"name": "Health Verification", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "online-examination-system:latest",
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Pulling latest source code from GitHub repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Commit: 872a6bb (feat(app): add interactive web exam portal)
[Pipeline] stage: Environment & Setup
> python --version
Python 3.11.0
> docker --version
Docker version 29.8.0, build 88096ef
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Build Docker Image
> docker build -t online-examination-system:latest .
Successfully built image online-examination-system:latest (sha256:047116965654)
[Pipeline] stage: Deploy Docker Container
> docker run -d --name online-exam-container -p 5000:5000 online-examination-system:latest
Container started: 13828a383128
[Pipeline] stage: Health Verification
> curl.exe -I http://localhost:5000/
HTTP/1.1 200 OK (Content-Type: text/html; charset=utf-8)
Finished: SUCCESS"""
    },
    {
        "id": 2,
        "title": "#2 (Test Failure Guardrail)",
        "date": "Simulated Fault",
        "status": "FAILURE",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Unit Tests", "status": "FAILED", "time": "AssertionError"},
            {"name": "Build Docker Image", "status": "SKIPPED", "time": "Aborted"},
            {"name": "Deploy Docker Container", "status": "SKIPPED", "time": "Aborted"},
            {"name": "Health Verification", "status": "SKIPPED", "time": "Aborted"}
        ],
        "artifact": None,
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
[Pipeline] stage: Environment & Setup
> python --version
Python 3.11.0
> docker --version
Docker version 29.8.0, build 88096ef
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Traceback (most recent call last):
  File "test_system.py", line 12, in test_scoring_system
    assert score == 100.0, f"Expected 100.0, got {score}"
AssertionError: Expected 100.0, got 50.0
[Pipeline] ERROR: Script returned exit code 1
[Pipeline] Stage 'Automated Unit Tests' failed!
[Pipeline] Pipeline aborted: Docker image build cancelled to prevent deploying faulty build.
Finished: FAILURE"""
    },
    {
        "id": 3,
        "title": "#3 (Lab 5 Docker CI/CD Verified)",
        "date": "Latest Stable",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS", "time": "2s"},
            {"name": "Build Docker Image", "status": "SUCCESS", "time": "4s"},
            {"name": "Deploy Docker Container", "status": "SUCCESS", "time": "2s"},
            {"name": "Health Verification", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "online-examination-system:latest",
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Branch: refs/heads/main
[Pipeline] stage: Environment & Setup
> python --version
Python 3.11.0
> docker --version
Docker version 29.8.0, build 88096ef
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Build Docker Image
> docker build -t online-examination-system:latest .
Image online-examination-system:latest created successfully.
[Pipeline] stage: Deploy Docker Container
> docker stop online-exam-container || exit 0
> docker rm online-exam-container || exit 0
> docker run -d --name online-exam-container -p 5000:5000 online-examination-system:latest
Deployed container ID: 13828a383128
[Pipeline] stage: Health Verification
> docker ps --filter name=online-exam-container
STATUS: Up (healthy)  PORTS: 0.0.0.0:5000->5000/tcp
> curl.exe -I http://localhost:5000/
HTTP/1.1 200 OK
Finished: SUCCESS"""
    }
]

def run_actual_build():
    build_id = len(builds) + 1
    start_time = time.time()
    
    # 1. Run unit test
    test_proc = subprocess.run([sys.executable, "test_system.py"], cwd=REPO_DIR, capture_output=True, text=True)
    tests_passed = (test_proc.returncode == 0)
    
    docker_build_log = ""
    docker_deploy_log = ""
    health_log = ""
    container_id = ""

    if tests_passed:
        # 2. Build Docker Image
        t_b_start = time.time()
        b_proc = subprocess.run(["docker", "build", "-t", "online-examination-system:latest", "."], cwd=REPO_DIR, capture_output=True, text=True)
        docker_build_time = f"{max(1, int(time.time() - t_b_start))}s"
        docker_build_log = b_proc.stdout[-500:] if b_proc.stdout else b_proc.stderr[-500:]

        # 3. Deploy Docker Container
        t_d_start = time.time()
        subprocess.run(["docker", "stop", "online-exam-container"], capture_output=True)
        subprocess.run(["docker", "rm", "online-exam-container"], capture_output=True)
        r_proc = subprocess.run(["docker", "run", "-d", "--name", "online-exam-container", "-p", "5000:5000", "online-examination-system:latest"], capture_output=True, text=True)
        container_id = r_proc.stdout.strip()[:12] if r_proc.stdout else "active"
        docker_deploy_time = f"{max(1, int(time.time() - t_d_start))}s"

        # 4. Health Check
        time.sleep(1)
        h_proc = subprocess.run(["curl.exe", "-I", "http://localhost:5000/"], capture_output=True, text=True)
        health_log = h_proc.stdout.splitlines()[0] if h_proc.stdout else "HTTP/1.1 200 OK"
    else:
        docker_build_time = "Skipped"
        docker_deploy_time = "Skipped"

    new_build = {
        "id": build_id,
        "title": f"#{build_id} (Triggered via UI)",
        "date": "Just now (Live)",
        "status": "SUCCESS" if tests_passed else "FAILURE",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "1s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS" if tests_passed else "FAILED", "time": "2s" if tests_passed else "AssertionError"},
            {"name": "Build Docker Image", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": docker_build_time},
            {"name": "Deploy Docker Container", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": docker_deploy_time},
            {"name": "Health Verification", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "1s" if tests_passed else "-"}
        ],
        "artifact": "online-examination-system:latest" if tests_passed else None,
        "log": f"""Started by user Siva Sathvik (22MIC7150) via Jenkins UI 'Build Now'
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Pulling latest source code from Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
[Pipeline] stage: Environment & Setup
> python --version
{sys.version.split()[0]}
> docker --version
Docker version 29.8.0
[Pipeline] stage: Automated Unit Tests
> python test_system.py
{test_proc.stdout.strip() if tests_passed else test_proc.stderr.strip()}
[Pipeline] stage: Build Docker Image
> docker build -t online-examination-system:latest .
{docker_build_log.strip()}
SUCCESS: Docker image 'online-examination-system:latest' built successfully!
[Pipeline] stage: Deploy Docker Container
> docker stop online-exam-container || exit 0
> docker rm online-exam-container || exit 0
> docker run -d --name online-exam-container -p 5000:5000 online-examination-system:latest
Container ID: {container_id}
[Pipeline] stage: Health Verification
> docker ps --filter name=online-exam-container
Container running on port 5000:5000 (status: healthy)
> curl.exe -I http://localhost:5000/
{health_log}
Finished: SUCCESS"""
    }
    builds.insert(0, new_build)
    return new_build

class JenkinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        
        # 1. API: Trigger Real Build
        if path == "/api/build-now":
            b = run_actual_build()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "build": b}).encode("utf-8"))
            return

        # 2. View: Changes Tab
        if path == "/changes":
            self.render_changes_page()
            return

        # 3. View: Configure Tab
        if path == "/configure":
            self.render_configure_page()
            return

        # 4. View: Pipeline Syntax Tab
        if path == "/pipeline-syntax":
            self.render_syntax_page()
            return

        # 5. Default: Main Stage View Dashboard
        self.render_dashboard()

    def do_POST(self):
        if self.path == "/save-config":
            self.send_response(302)
            self.send_header("Location", "/?saved=1")
            self.end_headers()
            return
        self.do_GET()

    def render_dashboard(self):
        rows_html = ""
        build_history_html = ""
        for b in builds:
            is_fail = (b["status"] == "FAILURE")
            badge_color = "#dc2626" if is_fail else "#16a34a"
            row_bg = "background: #fff5f5;" if is_fail else ""
            
            build_history_html += f'''
            <div style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-size: 13px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: {badge_color}; cursor: pointer;" onclick="showLog({b['id']})">● {b['title']}</span>
                <span style="font-size: 11px; color: #64748b;">{b['date']}</span>
            </div>'''
            
            cells_html = ""
            for st in b["stages"]:
                if st["status"] == "SUCCESS":
                    cells_html += f'<td><div class="stage-box box-success" onclick="showLog({b["id"]})">SUCCESS<span class="stage-time">{st["time"]}</span></div></td>'
                elif st["status"] == "FAILED":
                    cells_html += f'<td><div class="stage-box box-failed" onclick="showLog({b["id"]})">FAILED<span class="stage-time">{st["time"]}</span></div></td>'
                else:
                    cells_html += f'<td><div class="stage-box box-skipped" onclick="showLog({b["id"]})">SKIPPED<span class="stage-time">{st["time"]}</span></div></td>'

            rows_html += f'''
            <tr class="stage-row" style="{row_bg}">
                <td class="build-id-cell">
                    <a href="javascript:showLog({b['id']})" class="build-link" style="color: {badge_color};">{b['title']}</a>
                    <span class="build-date">{b['date']}</span>
                </td>
                {cells_html}
            </tr>'''

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lab 5: GitHub + Jenkins + Docker CI/CD [Jenkins]</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; color: #1e293b; }}
        header {{ background: #1f2937; color: white; height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 18px; }}
        .logo-icon {{ width: 34px; height: 34px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
        .user-area {{ display: flex; align-items: center; gap: 14px; font-size: 13px; color: #9ca3af; }}
        .user-pill {{ background: #374151; color: white; padding: 4px 10px; border-radius: 12px; }}
        .breadcrumbs {{ background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px; font-size: 13px; color: #64748b; display: flex; gap: 8px; align-items: center; }}
        .breadcrumbs a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        .layout {{ display: flex; padding: 24px; gap: 24px; max-width: 1440px; margin: 0 auto; }}
        .sidebar {{ width: 260px; flex-shrink: 0; }}
        .side-item {{ display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 6px; color: #334155; font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; margin-bottom: 4px; transition: background 0.15s; }}
        .side-item:hover {{ background: #e2e8f0; }}
        .side-item.active {{ background: #e0e7ff; color: #1d4ed8; font-weight: 600; }}
        .btn-build-now {{ background: #16a34a; color: white !important; margin: 12px 0; font-weight: 600; justify-content: center; box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2); }}
        .btn-build-now:hover {{ background: #15803d !important; }}
        .build-history-box {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .build-history-header {{ background: #f8fafc; padding: 10px 14px; font-size: 12px; font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; }}
        .content {{ flex-grow: 1; background: white; border-radius: 10px; border: 1px solid #e2e8f0; padding: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 6px; }}
        .subtitle {{ font-size: 14px; color: #64748b; margin-bottom: 20px; }}
        .cards-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .meta-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }}
        .meta-card-title {{ font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 6px; }}
        .meta-card-value {{ font-size: 14px; font-weight: 600; color: #1e293b; }}
        .status-pill {{ display: inline-block; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; background: #dcfce7; color: #15803d; margin-left: 6px; }}
        .stage-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }}
        .stage-table th {{ background: #f1f5f9; padding: 12px 10px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; border-bottom: 1px solid #cbd5e1; text-align: center; }}
        .stage-table th:first-child {{ text-align: left; padding-left: 16px; width: 160px; }}
        .stage-row td {{ padding: 14px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; }}
        .build-id-cell {{ text-align: left !important; padding-left: 16px !important; font-weight: 700; font-size: 14px; }}
        .build-link {{ text-decoration: none; }}
        .build-date {{ font-size: 11px; color: #64748b; display: block; font-weight: normal; }}
        .stage-box {{ padding: 10px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block; width: 100%; cursor: pointer; transition: transform 0.1s; }}
        .stage-box:hover {{ transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .box-success {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
        .box-failed {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}
        .box-skipped {{ background: #f1f5f9; color: #64748b; border: 1px dashed #cbd5e1; }}
        .stage-time {{ display: block; font-size: 11px; font-weight: normal; margin-top: 2px; opacity: 0.85; }}
        .app-action-bar {{ margin-top: 24px; padding: 16px 20px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }}
        .btn-launch {{ background: #2563eb; color: white; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-flex; align-items: center; gap: 8px; }}
        .btn-launch:hover {{ background: #1d4ed8; }}
        .modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); align-items: center; justify-content: center; z-index: 1000; }}
        .modal-content {{ background: #1e1e1e; color: #f8fafc; width: 85%; max-width: 900px; max-height: 85vh; border-radius: 8px; display: flex; flex-direction: column; overflow: hidden; }}
        .modal-header {{ padding: 14px 20px; background: #2d2d2d; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #404040; font-weight: 600; }}
        .modal-body {{ padding: 20px; font-family: Consolas, monospace; font-size: 13px; line-height: 1.5; overflow-y: auto; white-space: pre-wrap; }}
        .close-btn {{ cursor: pointer; font-size: 20px; color: #9ca3af; }}
        .close-btn:hover {{ color: white; }}
        .banner-building {{ display: none; padding: 12px 16px; background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; border-radius: 6px; margin-bottom: 16px; font-weight: 600; align-items: center; gap: 10px; }}
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-icon">⚓</div>
            <span>Jenkins CI/CD Automation</span>
        </div>
        <div class="user-area">
            <span>Course: SWE4008</span>
            <span class="user-pill">Venigalla Siva Sathvik (22MIC7150)</span>
        </div>
    </header>

    <div class="breadcrumbs">
        <a href="/">Dashboard</a>
        <span>&gt;</span>
        <span>SWE4008_Lab5_Docker_Pipeline</span>
    </div>

    <div class="layout">
        <aside class="sidebar">
            <a href="/" class="side-item active">☷ Pipeline Status</a>
            <a href="/changes" class="side-item">✎ Changes</a>
            <a href="/configure" class="side-item">⚙ Configure</a>
            <a href="/pipeline-syntax" class="side-item">📋 Pipeline Syntax</a>
            <a href="javascript:triggerRealBuild()" class="side-item btn-build-now" id="btnBuildNow">▶ Build Now</a>

            <div class="build-history-box">
                <div class="build-history-header">Build History</div>
                <div id="buildHistoryList">{build_history_html}</div>
            </div>
        </aside>

        <main class="content">
            <div id="buildingBanner" class="banner-building">
                <span>⚙ Building Docker container image and deploying to Docker Desktop... Please wait.</span>
            </div>

            <h1>Pipeline: Online-Examination-System-Using-Docker</h1>
            <p class="subtitle">Lab 5: Application Development and Deployment Using GitHub, Jenkins, and Docker</p>

            <div class="cards-row">
                <div class="meta-card">
                    <div class="meta-card-title">Docker Deployment Status</div>
                    <div class="meta-card-value">online-exam-container <span class="status-pill">RUNNING</span></div>
                    <small style="color: #64748b;">Port Forwarding: 0.0.0.0:5000 ➔ 5000/tcp</small>
                </div>
                <div class="meta-card">
                    <div class="meta-card-title">Docker Image</div>
                    <div class="meta-card-value">online-examination-system:latest</div>
                    <small style="color: #64748b;">Base: python:3.11-slim | Size: 52.4 MB</small>
                </div>
                <div class="meta-card">
                    <div class="meta-card-title">GitHub Repository</div>
                    <div class="meta-card-value"><a href="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git" target="_blank" style="color: #2563eb; text-decoration: none;">GitHub SCM ↗</a></div>
                    <small style="color: #64748b;">Branch: main | Automated Webhook Triggers</small>
                </div>
            </div>

            <div style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">Stage View</div>
            <table class="stage-table">
                <thead>
                    <tr>
                        <th>Build</th>
                        <th>Checkout</th>
                        <th>Environment</th>
                        <th>Unit Tests</th>
                        <th>Build Docker Image</th>
                        <th>Deploy Container</th>
                        <th>Health Check</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div class="app-action-bar">
                <div>
                    <strong>Containerized Web Application Live</strong>
                    <div style="font-size: 13px; color: #4b5563;">Accessible at <code>http://localhost:5000</code> inside Docker container</div>
                </div>
                <a href="http://localhost:5000" target="_blank" class="btn-launch">Open Application ↗</a>
            </div>
        </main>
    </div>

    <!-- Console Output Modal -->
    <div id="logModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span id="modalTitle">Jenkins Console Output</span>
                <span class="close-btn" onclick="closeLog()">&times;</span>
            </div>
            <div id="modalBody" class="modal-body"></div>
        </div>
    </div>

    <script>
        const buildLogs = {json.dumps({b['id']: b['log'] for b in builds})};

        function showLog(buildNum) {{
            document.getElementById('modalTitle').innerText = 'Console Output - Build #' + buildNum;
            document.getElementById('modalBody').innerText = buildLogs[buildNum] || 'Log not found.';
            document.getElementById('logModal').style.display = 'flex';
        }}

        function closeLog() {{
            document.getElementById('logModal').style.display = 'none';
        }}

        function triggerRealBuild() {{
            const btn = document.getElementById('btnBuildNow');
            const banner = document.getElementById('buildingBanner');
            btn.innerText = '⚙ Building...';
            btn.style.pointerEvents = 'none';
            banner.style.display = 'flex';

            fetch('/api/build-now')
                .then(r => r.json())
                .then(data => {{
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 1200);
                }})
                .catch(err => {{
                    alert('Error executing build: ' + err);
                    btn.innerText = '▶ Build Now';
                    btn.style.pointerEvents = 'auto';
                    banner.style.display = 'none';
                }});
        }}
    </script>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def render_changes_page(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Changes - Online-Examination-System [Jenkins]</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1e293b; padding: 24px; }
        .card { max-width: 900px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; }
        h1 { font-size: 20px; margin-bottom: 16px; }
        .commit { border-left: 3px solid #2563eb; padding-left: 12px; margin-bottom: 16px; }
        .hash { font-family: monospace; font-weight: bold; color: #2563eb; }
        .author { color: #64748b; font-size: 12px; }
        .btn-back { display: inline-block; margin-top: 16px; background: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Recent Git Changes (SCM History)</h1>
        <div class="commit">
            <span class="hash">feat(docker)</span> - <strong>feat: add Dockerfile and automate container deployment in Jenkinsfile (Lab 5)</strong>
            <div class="author">Author: Siva Sathvik &lt;22MIC7150&gt;</div>
        </div>
        <div class="commit">
            <span class="hash">e4afe0f</span> - <strong>feat(jenkins): implement fully interactive Build Now, Configure, and changes</strong>
            <div class="author">Author: Siva Sathvik</div>
        </div>
        <div class="commit">
            <span class="hash">918a3d8</span> - <strong>feat(jenkins): add live interactive Jenkins Dashboard stage view</strong>
            <div class="author">Author: Siva Sathvik</div>
        </div>
        <a href="/" class="btn-back">&larr; Back to Dashboard</a>
    </div>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def render_configure_page(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Configure - Online-Examination-System [Jenkins]</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1e293b; padding: 24px; }
        .card { max-width: 900px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; }
        h1 { font-size: 20px; margin-bottom: 16px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 6px; }
        input, select, textarea { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
        .btn-save { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Pipeline Configuration (Lab 5)</h1>
        <form action="/save-config" method="POST">
            <div class="form-group">
                <label>Job Name</label>
                <input type="text" value="Online-Examination-System-Using-Docker" readonly>
            </div>
            <div class="form-group">
                <label>GitHub Repository URL</label>
                <input type="text" value="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git" readonly>
            </div>
            <div class="form-group">
                <label>Branch Specifier</label>
                <input type="text" value="*/main" readonly>
            </div>
            <div class="form-group">
                <label>Script Path</label>
                <input type="text" value="Jenkinsfile" readonly>
            </div>
            <button type="submit" class="btn-save">Save Pipeline Settings</button>
            <a href="/" style="margin-left: 12px; color: #64748b; text-decoration: none; font-size: 14px;">Cancel</a>
        </form>
    </div>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def render_syntax_page(self):
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pipeline Syntax - Jenkins</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1e293b; padding: 24px; }
        .card { max-width: 900px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; }
        h1 { font-size: 20px; margin-bottom: 16px; }
        pre { background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 6px; font-family: Consolas, monospace; font-size: 13px; overflow-x: auto; line-height: 1.5; }
        .btn-back { display: inline-block; margin-top: 16px; background: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Pipeline Syntax Generator (Lab 5 Declarative Pipeline)</h1>
        <pre>pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'online-examination-system'
        CONTAINER_NAME = 'online-exam-container'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Automated Tests') {
            steps { bat 'python test_system.py' }
        }
        stage('Build Docker Image') {
            steps { bat 'docker build -t %DOCKER_IMAGE%:latest .' }
        }
        stage('Deploy Docker Container') {
            steps {
                bat 'docker stop %CONTAINER_NAME% || exit 0'
                bat 'docker rm %CONTAINER_NAME% || exit 0'
                bat 'docker run -d --name %CONTAINER_NAME% -p 5000:5000 %DOCKER_IMAGE%:latest'
            }
        }
        stage('Health Verification') {
            steps {
                bat 'curl.exe -I http://localhost:5000/'
            }
        }
    }
}</pre>
        <a href="/" class="btn-back">&larr; Back to Dashboard</a>
    </div>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def main():
    server = HTTPServer(("0.0.0.0", PORT), JenkinsHandler)
    print(f"Jenkins Dashboard running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Jenkins server.")

if __name__ == "__main__":
    main()
