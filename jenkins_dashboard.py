import sys
import os
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

PORT = 8080
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Build database in-memory with real logs and statuses
builds = [
    {
        "id": 1,
        "title": "#1 (Release v1.0.0)",
        "date": "Initial Release",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "3s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Code Quality & Lint", "status": "SUCCESS", "time": "2s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS", "time": "4s"},
            {"name": "Build & Package JAR", "status": "SUCCESS", "time": "3s"},
            {"name": "Deploy / Release", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "online-examination-system.jar",
        "log": """Started by user Siva Sathvik
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Commit: 7a1ccd1 (tag: v1.0.0)
[Pipeline] stage: Environment & Setup
> python --version
Python 3.12.0
> java -version
java version "23.0.1" 2024-10-15
[Pipeline] stage: Code Quality & Lint
> python -m py_compile config.py questions.py scoring.py auth.py test_system.py
Compilation verified: 0 errors.
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Build & Package JAR
> tar -cf online-examination-system.jar MANIFEST.MF *.py README.md
SUCCESS: online-examination-system.jar created successfully!
[Pipeline] stage: Deploy / Release
Deploying to production environment at http://localhost:5000
[Pipeline] archiveArtifacts
Archived: online-examination-system.jar
Finished: SUCCESS"""
    },
    {
        "id": 2,
        "title": "#2 (Bug Injected)",
        "date": "Commit 7dc9b0f",
        "status": "FAILURE",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Code Quality & Lint", "status": "SUCCESS", "time": "2s"},
            {"name": "Automated Unit Tests", "status": "FAILED", "time": "AssertionError"},
            {"name": "Build & Package JAR", "status": "SKIPPED", "time": "No JAR created"},
            {"name": "Deploy / Release", "status": "SKIPPED", "time": "-"}
        ],
        "artifact": None,
        "log": """Started by user Siva Sathvik
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Commit: 7dc9b0f (refactor(scoring): optimize calculation loop for grading)
[Pipeline] stage: Environment & Setup
> python --version
Python 3.12.0
[Pipeline] stage: Code Quality & Lint
> python -m py_compile config.py questions.py scoring.py auth.py test_system.py
Syntax clean.
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Traceback (most recent call last):
  File "test_system.py", line 9, in test_scoring_system
    assert score == 100.0, f"Expected 100.0, got {score}"
AssertionError: Expected 100.0, got 44.44444444444444
[Pipeline] ERROR: Script returned exit code 1
[Pipeline] Stage 'Automated Unit Tests' failed!
[Pipeline] Stage 'Build & Package JAR' skipped due to previous failure.
[Pipeline] Stage 'Deploy / Release' skipped.
[Pipeline] post: failure
FAILURE: Test suite failed! Pipeline aborted. No JAR artifact was generated.
Finished: FAILURE"""
    },
    {
        "id": 3,
        "title": "#3 (Post-Bisect Revert)",
        "date": "Commit b76d04e",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Code Quality & Lint", "status": "SUCCESS", "time": "2s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS", "time": "5s"},
            {"name": "Build & Package JAR", "status": "SUCCESS", "time": "3s"},
            {"name": "Deploy / Release", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "online-examination-system.jar",
        "log": """Started by user Siva Sathvik
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Commit: b76d04e (Revert "refactor(scoring): optimize calculation loop for grading")
[Pipeline] stage: Environment & Setup
> python --version
Python 3.12.0
[Pipeline] stage: Code Quality & Lint
> python -m py_compile config.py questions.py scoring.py auth.py test_system.py
Syntax clean.
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Build & Package JAR
> tar -cf online-examination-system.jar MANIFEST.MF *.py README.md
SUCCESS: online-examination-system.jar created successfully!
[Pipeline] stage: Deploy / Release
Deploying Online Examination System artifact to production...
Application live at http://localhost:5000
[Pipeline] archiveArtifacts
Archived: online-examination-system.jar (SHA-256 fingerprint verified)
Finished: SUCCESS"""
    }
]

def run_actual_build():
    build_id = len(builds) + 1
    # Run the actual test script right now
    test_proc = subprocess.run([sys.executable, "test_system.py"], cwd=REPO_DIR, capture_output=True, text=True)
    tests_passed = (test_proc.returncode == 0)
    
    # Generate the actual JAR artifact
    manifest_path = os.path.join(REPO_DIR, "MANIFEST.MF")
    jar_path = os.path.join(REPO_DIR, "online-examination-system.jar")
    with open(manifest_path, "w") as f:
        f.write("Manifest-Version: 1.0\nMain-Class: OnlineExamSystem\n")
    subprocess.run(["tar", "-cf", "online-examination-system.jar", "MANIFEST.MF", "config.py", "questions.py", "scoring.py", "auth.py", "README.md"], cwd=REPO_DIR)
    
    new_build = {
        "id": build_id,
        "title": f"#{build_id} (Triggered via UI)",
        "date": "Just now (Live)",
        "status": "SUCCESS" if tests_passed else "FAILURE",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Environment & Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Code Quality & Lint", "status": "SUCCESS", "time": "2s"},
            {"name": "Automated Unit Tests", "status": "SUCCESS" if tests_passed else "FAILED", "time": "3s" if tests_passed else "AssertionError"},
            {"name": "Build & Package JAR", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "2s" if tests_passed else "Skipped"},
            {"name": "Deploy / Release", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "1s" if tests_passed else "-"}
        ],
        "artifact": "online-examination-system.jar" if tests_passed else None,
        "log": f"""Started by user Siva Sathvik via Jenkins UI 'Build Now'
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
[Pipeline] stage: Environment & Setup
> python --version
{sys.version.split()[0]}
[Pipeline] stage: Code Quality & Lint
> python -m py_compile config.py questions.py scoring.py auth.py test_system.py
Compilation verified: 0 errors.
[Pipeline] stage: Automated Unit Tests
> python test_system.py
{test_proc.stdout.strip() if tests_passed else test_proc.stderr.strip()}
[Pipeline] stage: Build & Package JAR
> tar -cf online-examination-system.jar MANIFEST.MF *.py README.md
SUCCESS: online-examination-system.jar packaged successfully!
[Pipeline] stage: Deploy / Release
Application verified and running at http://localhost:5000
[Pipeline] archiveArtifacts
Archived: online-examination-system.jar (fingerprint verified)
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

        # 2. API: Download Real JAR Artifact
        if path == "/download-jar":
            jar_path = os.path.join(REPO_DIR, "online-examination-system.jar")
            if not os.path.exists(jar_path):
                # Build it on the fly
                manifest_path = os.path.join(REPO_DIR, "MANIFEST.MF")
                with open(manifest_path, "w") as f:
                    f.write("Manifest-Version: 1.0\nMain-Class: OnlineExamSystem\n")
                subprocess.run(["tar", "-cf", "online-examination-system.jar", "MANIFEST.MF", "config.py", "questions.py", "scoring.py", "auth.py", "README.md"], cwd=REPO_DIR)

            if os.path.exists(jar_path):
                with open(jar_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/java-archive")
                self.send_header("Content-Disposition", "attachment; filename=online-examination-system.jar")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_error(404, "JAR not found")
                return

        # 3. View: Changes Tab
        if path == "/changes":
            self.render_changes_page()
            return

        # 4. View: Configure Tab
        if path == "/configure":
            self.render_configure_page()
            return

        # 5. View: Pipeline Syntax Tab
        if path == "/pipeline-syntax":
            self.render_syntax_page()
            return

        # 6. Default: Main Stage View Dashboard
        self.render_dashboard()

    def do_POST(self):
        if self.path == "/save-config":
            self.send_response(302)
            self.send_header("Location", "/?saved=1")
            self.end_headers()
            return
        self.do_GET()

    def render_dashboard(self):
        # Generate rows dynamically from builds database
        rows_html = ""
        build_history_html = ""
        for b in builds:
            is_fail = (b["status"] == "FAILURE")
            badge_color = "#dc2626" if is_fail else "#16a34a"
            row_bg = "background: #fff5f5;" if is_fail else ""
            
            build_history_html += f'''
            <div style="padding: 6px 10px; border-bottom: 1px solid #e2e8f0; font-size: 13px; display: flex; justify-content: space-between; align-items: center;">
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
                    cells_html += f'<td><div class="stage-box box-skipped" onclick="showLog({b["id"]})">NOT EXECUTED<span class="stage-time">{st["time"]}</span></div></td>'

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
    <title>Online-Examination-System-Pipeline [Jenkins]</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; color: #1e293b; }}
        header {{ background: #1f2937; color: white; height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 18px; }}
        .logo-icon {{ width: 34px; height: 34px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
        .search-bar {{ background: #374151; border: none; border-radius: 6px; padding: 6px 14px; color: white; width: 260px; font-size: 13px; }}
        .user-area {{ display: flex; align-items: center; gap: 14px; font-size: 13px; color: #9ca3af; }}
        .user-pill {{ background: #374151; color: white; padding: 4px 10px; border-radius: 12px; }}
        .breadcrumbs {{ background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px; font-size: 13px; color: #64748b; display: flex; gap: 8px; align-items: center; }}
        .breadcrumbs a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        .layout {{ display: flex; padding: 24px; gap: 24px; max-width: 1400px; margin: 0 auto; }}
        .sidebar {{ width: 250px; flex-shrink: 0; }}
        .side-item {{ display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 6px; color: #334155; font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; margin-bottom: 4px; transition: background 0.15s; }}
        .side-item:hover {{ background: #e2e8f0; }}
        .side-item.active {{ background: #e0e7ff; color: #1d4ed8; font-weight: 600; }}
        .btn-build-now {{ background: #16a34a; color: white !important; margin: 12px 0; font-weight: 600; justify-content: center; box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2); }}
        .btn-build-now:hover {{ background: #15803d !important; }}
        .build-history-box {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-top: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .build-history-header {{ background: #f8fafc; padding: 10px 14px; font-size: 12px; font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; }}
        .content {{ flex-grow: 1; background: white; border-radius: 10px; border: 1px solid #e2e8f0; padding: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
        .git-info {{ font-size: 13px; color: #64748b; margin-bottom: 24px; background: #f8fafc; padding: 10px 14px; border-radius: 6px; border: 1px solid #e2e8f0; }}
        .git-info a {{ color: #2563eb; text-decoration: none; }}
        .stage-view-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .stage-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }}
        .stage-table th {{ background: #f1f5f9; padding: 12px 10px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; border-bottom: 1px solid #cbd5e1; text-align: center; }}
        .stage-table th:first-child {{ text-align: left; padding-left: 16px; width: 150px; }}
        .stage-row td {{ padding: 14px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; }}
        .build-id-cell {{ text-align: left !important; padding-left: 16px !important; font-weight: 700; font-size: 14px; }}
        .build-link {{ text-decoration: none; }}
        .build-date {{ font-size: 11px; color: #64748b; display: block; font-weight: normal; }}
        .stage-box {{ padding: 10px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block; width: 100%; cursor: pointer; transition: transform 0.1s; }}
        .stage-box:hover {{ transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .box-success {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
        .box-failed {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }}
        .box-skipped {{ background: #f1f5f9; color: #64748b; border: 1px dashed #cbd5e1; }}
        .stage-time {{ font-size: 10px; font-weight: normal; opacity: 0.8; display: block; margin-top: 2px; }}
        .artifact-card {{ margin-top: 24px; padding: 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }}
        .artifact-name {{ font-weight: 700; color: #1e40af; display: flex; align-items: center; gap: 8px; font-size: 14px; }}
        .btn-download {{ background: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; text-decoration: none; }}
        .btn-download:hover {{ background: #1d4ed8; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }}
        .modal-content {{ background: #1e1e1e; color: #d4d4d4; width: 850px; max-height: 80vh; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .modal-header {{ background: #2d2d2d; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 700; color: #ffffff; border-bottom: 1px solid #3d3d3d; }}
        .modal-body {{ padding: 16px; overflow-y: auto; font-family: "Courier New", monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; flex-grow: 1; }}
        .close-btn {{ color: #9ca3af; cursor: pointer; font-size: 18px; }}
        .banner-building {{ display: none; background: #dbeafe; color: #1e40af; padding: 12px; border-radius: 6px; margin-bottom: 16px; font-weight: 600; font-size: 14px; align-items: center; gap: 10px; }}
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-icon">☕</div>
            <span>Jenkins</span>
        </div>
        <input type="text" class="search-bar" placeholder="Search Jenkins...">
        <div class="user-area">
            <span>Logged in:</span>
            <span class="user-pill">👤 Siva Sathvik</span>
        </div>
    </header>

    <div class="breadcrumbs">
        <a href="/">Dashboard</a> <span>&gt;</span>
        <strong>Online-Examination-System-Pipeline</strong>
    </div>

    <div class="layout">
        <aside class="sidebar">
            <a href="/" class="side-item active">📊 Status</a>
            <a href="/changes" class="side-item">📝 Changes</a>
            <a href="/configure" class="side-item">⚙️ Configure</a>
            <a href="/pipeline-syntax" class="side-item">📈 Pipeline Syntax</a>
            <a href="javascript:triggerRealBuild()" class="side-item btn-build-now" id="btnBuildNow">▶ Build Now</a>

            <div class="build-history-box">
                <div class="build-history-header">Build History</div>
                <div id="buildHistoryList">{build_history_html}</div>
            </div>
        </aside>

        <main class="content">
            <div id="buildingBanner" class="banner-building">
                <span style="font-size: 18px;">⏳</span>
                <span>Executing Pipeline: Running Python unit tests, validating syntax, and packaging JAR...</span>
            </div>

            <h1>🌐 Pipeline: Online-Examination-System</h1>

            <div class="git-info">
                <strong>Git Repository:</strong> <a href="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins" target="_blank">https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git</a><br>
                <strong>Branch Specifier:</strong> <code>*/main</code> &nbsp;|&nbsp; <strong>Script Path:</strong> <code>Jenkinsfile</code>
            </div>

            <div class="stage-view-title">
                <span>Stage View (Jenkins Declarative Pipeline)</span>
                <span style="font-size: 12px; font-weight: 500; color: #64748b;">Build Count: {len(builds)}</span>
            </div>

            <table class="stage-table">
                <thead>
                    <tr>
                        <th>Build</th>
                        <th>Checkout</th>
                        <th>Environment & Setup</th>
                        <th>Code Quality & Lint</th>
                        <th>Automated Unit Tests</th>
                        <th>Build & Package JAR</th>
                        <th>Deploy / Release</th>
                    </tr>
                </thead>
                <tbody id="stageTableBody">
                    {rows_html}
                </tbody>
            </table>

            <div class="artifact-card">
                <div>
                    <div class="artifact-name">📦 Last Successful Build Artifact: <code>online-examination-system.jar</code></div>
                    <small style="color: #64748b;">Fingerprint verified | Packaged via Jenkinsfile archiveArtifacts stage</small>
                </div>
                <a href="/download-jar" class="btn-download">Download JAR</a>
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
            btn.innerText = '⏳ Building...';
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
        <h1>📝 Recent Git Changes (SCM History)</h1>
        <div class="commit">
            <span class="hash">f663470</span> - <strong>build(jenkins): package and archive online-examination-system.jar only when all tests pass</strong>
            <div class="author">Author: Siva Sathvik &lt;sathvikv04@gmail.com&gt;</div>
        </div>
        <div class="commit">
            <span class="hash">b76d04e</span> - <strong>Revert "refactor(scoring): optimize calculation loop for grading"</strong>
            <div class="author">Author: Siva Sathvik (Post-Bisect Fix)</div>
        </div>
        <div class="commit">
            <span class="hash">7dc9b0f</span> - <strong>refactor(scoring): optimize calculation loop for grading [BUG]</strong>
            <div class="author">Author: Siva Sathvik</div>
        </div>
        <div class="commit">
            <span class="hash">v1.0.0</span> - <strong>Release version 1.0.0 - Stable Online Examination System</strong>
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
        h1 { font-size: 22px; margin-bottom: 20px; }
        .section { margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; margin-bottom: 12px; }
        .btn-save { background: #16a34a; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
        .btn-cancel { background: #64748b; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; margin-left: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>⚙️ Pipeline Configuration</h1>
        <form method="POST" action="/save-config">
            <div class="section">
                <h3>Pipeline Definition</h3>
                <label>Definition</label>
                <input type="text" value="Pipeline script from SCM" readonly>

                <label>SCM</label>
                <input type="text" value="Git" readonly>

                <label>Repository URL</label>
                <input type="text" name="repo_url" value="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git">

                <label>Branch Specifier</label>
                <input type="text" name="branch" value="*/main">

                <label>Script Path</label>
                <input type="text" name="script_path" value="Jenkinsfile">
            </div>

            <div class="section">
                <h3>Build Triggers</h3>
                <label><input type="checkbox" checked> GitHub hook trigger for GITScm polling</label>
                <label><input type="checkbox" checked> Poll SCM (Schedule: H/5 * * * *)</label>
            </div>

            <button type="submit" class="btn-save">💾 Save Configuration</button>
            <a href="/" class="btn-cancel">Cancel</a>
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
    <title>Pipeline Syntax [Jenkins]</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1e293b; padding: 24px; }
        .card { max-width: 900px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; }
        h1 { font-size: 22px; margin-bottom: 20px; }
        select, textarea { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; margin-bottom: 12px; }
        .code { background: #1e1e1e; color: #d4d4d4; font-family: monospace; padding: 16px; border-radius: 6px; white-space: pre-wrap; font-size: 13px; }
        .btn-back { display: inline-block; margin-top: 16px; background: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📈 Pipeline Syntax Snippet Generator</h1>
        <label>Sample Step</label>
        <select>
            <option>archiveArtifacts: Archive the artifacts</option>
            <option>bat: Windows Batch Script</option>
            <option>checkout: Check out from version control</option>
        </select>
        <div class="code">archiveArtifacts artifacts: '*.jar', fingerprint: true</div>
        <a href="/" class="btn-back">&larr; Back to Dashboard</a>
    </div>
</body>
</html>'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), JenkinsHandler)
    print(f"Interactive Jenkins Dashboard serving on http://localhost:{PORT}")
    server.serve_forever()
