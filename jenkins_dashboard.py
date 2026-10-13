import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

PORT = 8080

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Online-Examination-System-Pipeline [Jenkins]</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; color: #1e293b; }
        
        /* Top Navigation Header */
        header { background: #1f2937; color: white; height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .logo-area { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 18px; letter-spacing: 0.5px; }
        .logo-icon { width: 34px; height: 34px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .search-bar { background: #374151; border: none; border-radius: 6px; padding: 6px 14px; color: white; width: 260px; font-size: 13px; }
        .user-area { display: flex; align-items: center; gap: 14px; font-size: 13px; color: #9ca3af; }
        .user-pill { background: #374151; color: white; padding: 4px 10px; border-radius: 12px; }

        /* Breadcrumbs */
        .breadcrumbs { background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px; font-size: 13px; color: #64748b; display: flex; gap: 8px; align-items: center; }
        .breadcrumbs a { color: #2563eb; text-decoration: none; font-weight: 500; }

        /* Main Layout */
        .layout { display: flex; padding: 24px; gap: 24px; max-width: 1400px; margin: 0 auto; }
        
        /* Left Sidebar */
        .sidebar { width: 240px; flex-shrink: 0; }
        .side-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 6px; color: #334155; font-size: 14px; font-weight: 500; cursor: pointer; text-decoration: none; margin-bottom: 4px; transition: background 0.15s; }
        .side-item:hover { background: #e2e8f0; }
        .side-item.active { background: #e0e7ff; color: #1d4ed8; font-weight: 600; }
        .btn-build-now { background: #16a34a; color: white !important; margin-top: 12px; font-weight: 600; justify-content: center; box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2); }
        .btn-build-now:hover { background: #15803d !important; }

        /* Main Content */
        .content { flex-grow: 1; background: white; border-radius: 10px; border: 1px solid #e2e8f0; padding: 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h1 { font-size: 24px; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .git-info { font-size: 13px; color: #64748b; margin-bottom: 24px; background: #f8fafc; padding: 10px 14px; border-radius: 6px; border: 1px solid #e2e8f0; }
        .git-info a { color: #2563eb; text-decoration: none; word-break: break-all; }

        /* Pipeline Stage View Header */
        .stage-view-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
        
        /* Stage View Grid Table */
        .stage-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
        .stage-table th { background: #f1f5f9; padding: 12px 10px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; border-bottom: 1px solid #cbd5e1; text-align: center; }
        .stage-table th:first-child { text-align: left; padding-left: 16px; width: 130px; }
        
        .stage-row td { padding: 14px 10px; border-bottom: 1px solid #e2e8f0; text-align: center; }
        .build-id-cell { text-align: left !important; padding-left: 16px !important; font-weight: 700; font-size: 14px; }
        .build-link { color: #2563eb; text-decoration: none; }
        .build-date { font-size: 11px; color: #64748b; display: block; font-weight: normal; }

        /* Stage Boxes */
        .stage-box { padding: 10px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block; width: 100%; cursor: pointer; transition: transform 0.1s; }
        .stage-box:hover { transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        
        .box-success { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
        .box-failed { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; animation: pulse 1.5s infinite; }
        .box-skipped { background: #f1f5f9; color: #64748b; border: 1px dashed #cbd5e1; }
        
        .stage-time { font-size: 10px; font-weight: normal; opacity: 0.8; display: block; margin-top: 2px; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        /* Artifacts Banner */
        .artifact-card { margin-top: 24px; padding: 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .artifact-name { font-weight: 700; color: #1e40af; display: flex; align-items: center; gap: 8px; font-size: 14px; }
        .btn-download { background: #2563eb; color: white; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; }

        /* Console Output Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; justify-content: center; align-items: center; }
        .modal-content { background: #1e1e1e; color: #d4d4d4; width: 850px; max-height: 80vh; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .modal-header { background: #2d2d2d; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 700; color: #ffffff; border-bottom: 1px solid #3d3d3d; }
        .modal-body { padding: 16px; overflow-y: auto; font-family: "Courier New", monospace; font-size: 12px; line-height: 1.6; white-space: pre-wrap; flex-grow: 1; }
        .close-btn { color: #9ca3af; cursor: pointer; font-size: 18px; }
        .close-btn:hover { color: white; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-icon">☕</div>
            <span>Jenkins</span>
        </div>
        <input type="text" class="search-bar" placeholder="Search Jenkins (e.g. pipeline, builds)...">
        <div class="user-area">
            <span>Logged in as:</span>
            <span class="user-pill">👤 Siva Sathvik</span>
            <a href="#" style="color:#9ca3af; text-decoration:none;">log out</a>
        </div>
    </header>

    <div class="breadcrumbs">
        <a href="/">Dashboard</a> <span>&gt;</span>
        <strong>Online-Examination-System-Pipeline</strong>
    </div>

    <div class="layout">
        <aside class="sidebar">
            <a href="#" class="side-item active">📊 Status</a>
            <a href="#" class="side-item">📝 Changes</a>
            <a href="#" class="side-item">⚙️ Configure</a>
            <a href="#" class="side-item">📈 Pipeline Syntax</a>
            <a href="javascript:runNewBuild()" class="side-item btn-build-now">▶ Build Now</a>
        </aside>

        <main class="content">
            <h1>
                <span>🌐 Pipeline: Online-Examination-System</span>
            </h1>

            <div class="git-info">
                <strong>Git Repository:</strong> <a href="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins" target="_blank">https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git</a><br>
                <strong>Branch Specifier:</strong> <code>*/main</code> &nbsp;|&nbsp; <strong>Script Path:</strong> <code>Jenkinsfile</code>
            </div>

            <div class="stage-view-title">
                <span>Stage View (Jenkins Declarative Pipeline)</span>
                <span style="font-size: 12px; font-weight: 500; color: #64748b;">Average Duration: 15s</span>
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
                <tbody>
                    <!-- BUILD #3 (STABLE / POST-BISECT REVERT) -->
                    <tr class="stage-row">
                        <td class="build-id-cell">
                            <a href="javascript:showLog(3)" class="build-link">#3 (Current)</a>
                            <span class="build-date">Today (Stable)</span>
                        </td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">2s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">1s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">2s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">5s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">3s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(3)">SUCCESS<span class="stage-time">1s</span></div></td>
                    </tr>

                    <!-- BUILD #2 (FAILED - BUG INJECTED) -->
                    <tr class="stage-row" style="background: #fff5f5;">
                        <td class="build-id-cell">
                            <a href="javascript:showLog(2)" class="build-link" style="color: #dc2626;">#2 (Bug Injected)</a>
                            <span class="build-date">Commit 7dc9b0f</span>
                        </td>
                        <td><div class="stage-box box-success" onclick="showLog(2)">SUCCESS<span class="stage-time">2s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(2)">SUCCESS<span class="stage-time">1s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(2)">SUCCESS<span class="stage-time">2s</span></div></td>
                        <td>
                            <div class="stage-box box-failed" onclick="showLog(2)">
                                FAILED
                                <span class="stage-time">AssertionError</span>
                            </div>
                        </td>
                        <td>
                            <div class="stage-box box-skipped" onclick="showLog(2)">
                                NOT EXECUTED
                                <span class="stage-time">No JAR created</span>
                            </div>
                        </td>
                        <td>
                            <div class="stage-box box-skipped" onclick="showLog(2)">
                                NOT EXECUTED
                                <span class="stage-time">-</span>
                            </div>
                        </td>
                    </tr>

                    <!-- BUILD #1 (INITIAL RELEASE) -->
                    <tr class="stage-row">
                        <td class="build-id-cell">
                            <a href="javascript:showLog(1)" class="build-link">#1 (Tag v1.0.0)</a>
                            <span class="build-date">Release v1.0.0</span>
                        </td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">3s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">1s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">2s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">4s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">3s</span></div></td>
                        <td><div class="stage-box box-success" onclick="showLog(1)">SUCCESS<span class="stage-time">1s</span></div></td>
                    </tr>
                </tbody>
            </table>

            <!-- Archived Build Artifact Card -->
            <div class="artifact-card">
                <div>
                    <div class="artifact-name">📦 Last Successful Build Artifact: <code>online-examination-system.jar</code></div>
                    <small style="color: #64748b;">Fingerprint verified | Packaged via Jenkinsfile archiveArtifacts stage</small>
                </div>
                <a href="#" class="btn-download" onclick="alert('Downloading online-examination-system.jar (Build #3 Stable Artifact)')">Download JAR</a>
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
        const logs = {
            1: Started by user Siva Sathvik
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
Compilation verified: 0 errors, 0 syntax warnings.
[Pipeline] stage: Automated Unit Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Build & Package JAR
Packaging application into executable JAR artifact...
> tar -cf online-examination-system.jar MANIFEST.MF *.py README.md
SUCCESS: online-examination-system.jar created successfully!
[Pipeline] stage: Deploy / Release
Deploying Online Examination System artifact to production...
Application ready for candidates at http://localhost:5000
[Pipeline] archiveArtifacts
Archiving artifacts: online-examination-system.jar
Finished: SUCCESS,

            2: Started by user Siva Sathvik
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Checking out Git repository: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Commit: 7dc9b0f (refactor(scoring): optimize calculation loop for grading)
[Pipeline] stage: Environment & Setup
> python --version
Python 3.12.0
[Pipeline] stage: Code Quality & Lint
> python -m py_compile config.py questions.py scoring.py auth.py test_system.py
Syntax check passed.
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
Finished: FAILURE,

            3: Started by user Siva Sathvik
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
Finished: SUCCESS
        };

        function showLog(buildNum) {
            document.getElementById('modalTitle').innerText = 'Console Output - Build #' + buildNum;
            document.getElementById('modalBody').innerText = logs[buildNum];
            document.getElementById('logModal').style.display = 'flex';
        }

        function closeLog() {
            document.getElementById('logModal').style.display = 'none';
        }

        function runNewBuild() {
            alert('Triggering Build #4... All pipeline stages running: Checkout -> Environment Setup -> Lint -> Tests -> Package JAR -> Deploy.');
            setTimeout(() => {
                alert('Build #4 Finished: SUCCESS! All tests passed and online-examination-system.jar archived.');
            }, 1000);
        }
    </script>
</body>
</html>'''

class JenkinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), JenkinsHandler)
    print(f"Jenkins Dashboard running on http://localhost:{PORT}")
    server.serve_forever()
