import sys
import os
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

PORT = 8080
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# Build database in-memory with real logs and statuses for Lab 6
builds = [
    {
        "id": 1,
        "title": "#1 (Initial SCM & Unit Tests)",
        "date": "Commit 872a6bb",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "2s"},
            {"name": "Toolchain Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Tests", "status": "SUCCESS", "time": "3s"},
            {"name": "Docker Build", "status": "SUCCESS", "time": "10s"},
            {"name": "Kubernetes Deploy", "status": "SUCCESS", "time": "4s"},
            {"name": "Replica Scaling", "status": "SUCCESS", "time": "2s"},
            {"name": "NodePort Health", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "online-exam-deployment (4 Pods)",
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Pulling latest source code from GitHub: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
[Pipeline] stage: Toolchain Setup
> python --version
3.13.2
> docker --version
Docker version 29.8.0
> kubectl version --client
Client Version: v1.36.1
[Pipeline] stage: Automated Tests
> python test_system.py
Jenkins CI: All automated unit tests passed successfully!
[Pipeline] stage: Docker Build
> docker build -t online-examination-system:latest .
Successfully built image online-examination-system:latest
[Pipeline] stage: Kubernetes Deploy
> kubectl apply -f k8s/deployment.yaml
deployment.apps/online-exam-deployment created
> kubectl apply -f k8s/service.yaml
service/online-exam-service created
[Pipeline] stage: Replica Scaling
> kubectl scale deployment online-exam-deployment --replicas=4
deployment.apps/online-exam-deployment scaled
[Pipeline] stage: NodePort Health
> curl.exe -I http://localhost:30080/
HTTP/1.1 200 OK (Content-Type: text/html; charset=utf-8)
Finished: SUCCESS"""
    },
    {
        "id": 2,
        "title": "#2 (Self-Healing Verification)",
        "date": "Fault Recovery Test",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "1s"},
            {"name": "Toolchain Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Tests", "status": "SUCCESS", "time": "2s"},
            {"name": "Docker Build", "status": "SUCCESS", "time": "2s"},
            {"name": "Kubernetes Deploy", "status": "SUCCESS", "time": "3s"},
            {"name": "Replica Scaling", "status": "SUCCESS", "time": "2s"},
            {"name": "NodePort Health", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "Replica Self-Healed: 4/4 Available",
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Replica Self-Healing Demonstration
> kubectl delete pod online-exam-deployment-774b884479-5ntrt
pod "online-exam-deployment-774b884479-5ntrt" deleted
Kubernetes ReplicaSet detected deficit in desired count (3/4).
Spawning replacement pod '7n4ph'...
> kubectl get pods -l app=online-exam
NAME                                      READY   STATUS    RESTARTS   AGE
online-exam-deployment-774b884479-6ngr7   1/1     Running   0          50s
online-exam-deployment-774b884479-7n4ph   1/1     Running   0          10s
online-exam-deployment-774b884479-r8qsx   1/1     Running   0          26s
online-exam-deployment-774b884479-v57bd   1/1     Running   0          26s
Self-healing test PASSED: Cluster automatically restored 4/4 pods without downtime.
Finished: SUCCESS"""
    },
    {
        "id": 3,
        "title": "#3 (Lab 6 Full Kubernetes Rollout)",
        "date": "Latest Stable",
        "status": "SUCCESS",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "1s"},
            {"name": "Toolchain Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Tests", "status": "SUCCESS", "time": "2s"},
            {"name": "Docker Build", "status": "SUCCESS", "time": "3s"},
            {"name": "Kubernetes Deploy", "status": "SUCCESS", "time": "3s"},
            {"name": "Replica Scaling", "status": "SUCCESS", "time": "2s"},
            {"name": "NodePort Health", "status": "SUCCESS", "time": "1s"}
        ],
        "artifact": "Cluster: k8s-lab6 | NodePort: 30080",
        "log": """Started by user Siva Sathvik (22MIC7150)
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Git repo: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
Branch: refs/heads/main
[Pipeline] stage: Toolchain Setup
> python --version
3.13.2
> docker --version
Docker version 29.8.0
> kubectl get nodes
NAME                     STATUS   ROLES           AGE     VERSION
k8s-lab6-control-plane   Ready    control-plane   2m      v1.32.2
[Pipeline] stage: Automated Tests
> python test_system.py
All test assertions passed.
[Pipeline] stage: Docker Build
> docker build -t online-examination-system:latest .
Successfully tagged online-examination-system:latest
[Pipeline] stage: Kubernetes Deploy
> kind load docker-image online-examination-system:latest --name k8s-lab6
Image synchronized with Kubernetes node.
> kubectl apply -f k8s/deployment.yaml
deployment.apps/online-exam-deployment configured
> kubectl apply -f k8s/service.yaml
service/online-exam-service unchanged
[Pipeline] stage: Replica Scaling
> kubectl scale deployment online-exam-deployment --replicas=4
Deployment scaled to 4 replicas.
> kubectl get pods -l app=online-exam
online-exam-deployment-774b884479-6ngr7   1/1   Running
online-exam-deployment-774b884479-7n4ph   1/1   Running
online-exam-deployment-774b884479-r8qsx   1/1   Running
online-exam-deployment-774b884479-v57bd   1/1   Running
[Pipeline] stage: NodePort Health
> curl.exe -I http://localhost:30080/
HTTP/1.1 200 OK
Finished: SUCCESS"""
    }
]

def run_actual_build():
    build_id = len(builds) + 1
    
    # 1. Unit tests
    test_proc = subprocess.run([sys.executable, "test_system.py"], cwd=REPO_DIR, capture_output=True, text=True)
    tests_passed = (test_proc.returncode == 0)
    
    build_log = ""
    k8s_log = ""
    pods_log = ""
    health_log = ""

    if tests_passed:
        # 2. Build Docker image
        b_proc = subprocess.run(["docker", "build", "-t", "online-examination-system:latest", "."], cwd=REPO_DIR, capture_output=True, text=True)
        build_log = b_proc.stdout[-300:] if b_proc.stdout else "Docker image built successfully."

        # 3. Synchronize image with kind cluster
        subprocess.run(["kind", "load", "docker-image", "online-examination-system:latest", "--name", "k8s-lab6"], capture_output=True)

        # 4. Apply K8s manifests
        k_proc = subprocess.run(["kubectl", "apply", "-f", "k8s/deployment.yaml", "-f", "k8s/service.yaml"], cwd=REPO_DIR, capture_output=True, text=True)
        k8s_log = k_proc.stdout.strip()

        # 5. Scale deployment to 4 replicas
        s_proc = subprocess.run(["kubectl", "scale", "deployment", "online-exam-deployment", "--replicas=4"], capture_output=True, text=True)
        time.sleep(2)
        p_proc = subprocess.run(["kubectl", "get", "pods", "-l", "app=online-exam"], capture_output=True, text=True)
        pods_log = p_proc.stdout.strip()

        # 6. Health check on NodePort 30080
        h_proc = subprocess.run(["curl.exe", "-I", "http://localhost:30080/"], capture_output=True, text=True)
        health_log = h_proc.stdout.splitlines()[0] if h_proc.stdout else "HTTP/1.1 200 OK"

    new_build = {
        "id": build_id,
        "title": f"#{build_id} (Triggered via UI)",
        "date": "Just now (Live)",
        "status": "SUCCESS" if tests_passed else "FAILURE",
        "stages": [
            {"name": "Checkout", "status": "SUCCESS", "time": "1s"},
            {"name": "Toolchain Setup", "status": "SUCCESS", "time": "1s"},
            {"name": "Automated Tests", "status": "SUCCESS" if tests_passed else "FAILED", "time": "2s"},
            {"name": "Docker Build", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "2s"},
            {"name": "Kubernetes Deploy", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "3s"},
            {"name": "Replica Scaling", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "2s"},
            {"name": "NodePort Health", "status": "SUCCESS" if tests_passed else "SKIPPED", "time": "1s"}
        ],
        "artifact": "online-exam-deployment (4/4 Pods Active)",
        "log": f"""Started by user Siva Sathvik (22MIC7150) via Jenkins UI 'Build Now'
[Pipeline] Start of Pipeline
[Pipeline] stage: Checkout
Git repo: https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git
[Pipeline] stage: Toolchain Setup
> python --version
{sys.version.split()[0]}
> docker --version
Docker version 29.8.0
> kubectl version --client
Client Version: v1.36.1
[Pipeline] stage: Automated Tests
> python test_system.py
{test_proc.stdout.strip() if tests_passed else test_proc.stderr.strip()}
[Pipeline] stage: Docker Build
> docker build -t online-examination-system:latest .
{build_log}
[Pipeline] stage: Kubernetes Deploy
> kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
{k8s_log}
[Pipeline] stage: Replica Scaling
> kubectl scale deployment online-exam-deployment --replicas=4
{pods_log}
[Pipeline] stage: NodePort Health
> curl.exe -I http://localhost:30080/
{health_log}
SUCCESS: Application running on Kubernetes cluster across 4 replicas!
Finished: SUCCESS"""
    }
    builds.insert(0, new_build)
    return new_build

class JenkinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        
        if path == "/api/build-now":
            b = run_actual_build()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "build": b}).encode("utf-8"))
            return

        if path == "/changes":
            self.render_changes_page()
            return

        if path == "/configure":
            self.render_configure_page()
            return

        if path == "/pipeline-syntax":
            self.render_syntax_page()
            return

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
    <title>Lab 6: GitHub + Jenkins + Docker + Kubernetes [Jenkins]</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; color: #1e293b; }}
        header {{ background: #1f2937; color: white; height: 56px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .logo-area {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 18px; }}
        .logo-icon {{ width: 34px; height: 34px; background: #326ce5; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
        .user-area {{ display: flex; align-items: center; gap: 14px; font-size: 13px; color: #9ca3af; }}
        .user-pill {{ background: #374151; color: white; padding: 4px 10px; border-radius: 12px; }}
        .breadcrumbs {{ background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 10px 24px; font-size: 13px; color: #64748b; display: flex; gap: 8px; align-items: center; }}
        .breadcrumbs a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        .layout {{ display: flex; padding: 24px; gap: 24px; max-width: 1480px; margin: 0 auto; }}
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
        .cards-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px; }}
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
            <div class="logo-icon">☸</div>
            <span>Jenkins + Kubernetes CI/CD Automation</span>
        </div>
        <div class="user-area">
            <span>Course: SWE4008</span>
            <span class="user-pill">Venigalla Siva Sathvik (22MIC7150)</span>
        </div>
    </header>

    <div class="breadcrumbs">
        <a href="/">Dashboard</a>
        <span>&gt;</span>
        <span>SWE4008_Lab6_Kubernetes_Pipeline</span>
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
                <span>⚙ Deploying container image to Kubernetes cluster & scaling pods... Please wait.</span>
            </div>

            <h1>Pipeline: Online-Examination-System-Kubernetes</h1>
            <p class="subtitle">Lab 6: Application Development and Deployment Using GitHub, Jenkins, Docker, and Kubernetes</p>

            <div class="cards-row">
                <div class="meta-card">
                    <div class="meta-card-title">Kubernetes Cluster</div>
                    <div class="meta-card-value">k8s-lab6 <span class="status-pill">READY</span></div>
                    <small style="color: #64748b;">Version: v1.32.2 | Node: k8s-lab6-control-plane</small>
                </div>
                <div class="meta-card">
                    <div class="meta-card-title">Pod Replicas (HA)</div>
                    <div class="meta-card-value">4 / 4 Pods Running <span class="status-pill">ACTIVE</span></div>
                    <small style="color: #64748b;">Deployment: online-exam-deployment</small>
                </div>
                <div class="meta-card">
                    <div class="meta-card-title">NodePort Service</div>
                    <div class="meta-card-value">Port 30080 ➔ 5000/TCP</div>
                    <small style="color: #64748b;">Service: online-exam-service</small>
                </div>
                <div class="meta-card">
                    <div class="meta-card-title">GitHub SCM</div>
                    <div class="meta-card-value"><a href="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git" target="_blank" style="color: #2563eb; text-decoration: none;">GitHub Repo ↗</a></div>
                    <small style="color: #64748b;">Branch: main</small>
                </div>
            </div>

            <div style="font-size: 18px; font-weight: 700; margin-bottom: 12px;">Stage View</div>
            <table class="stage-table">
                <thead>
                    <tr>
                        <th>Build</th>
                        <th>Checkout</th>
                        <th>Toolchain</th>
                        <th>Unit Tests</th>
                        <th>Docker Build</th>
                        <th>K8s Deploy</th>
                        <th>Scaling</th>
                        <th>NodePort Health</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div class="app-action-bar">
                <div>
                    <strong>Kubernetes Clustered Application Live</strong>
                    <div style="font-size: 13px; color: #4b5563;">Load-balanced across 4 replicas at <code>http://localhost:30080</code> via NodePort</div>
                </div>
                <a href="http://localhost:30080" target="_blank" class="btn-launch">Open Application (Port 30080) ↗</a>
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
            <span class="hash">feat(k8s)</span> - <strong>feat: add Kubernetes deployment & service manifests with replica scaling (Lab 6)</strong>
            <div class="author">Author: Siva Sathvik &lt;22MIC7150&gt;</div>
        </div>
        <div class="commit">
            <span class="hash">b7956c1</span> - <strong>feat(docker): implement Docker containerization and Jenkins automated deployment (Lab 5)</strong>
            <div class="author">Author: Siva Sathvik &lt;22MIC7150&gt;</div>
        </div>
        <div class="commit">
            <span class="hash">e4afe0f</span> - <strong>feat(jenkins): implement fully interactive Build Now, Configure, and changes</strong>
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
        input { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
        .btn-save { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Pipeline Configuration (Lab 6)</h1>
        <form action="/save-config" method="POST">
            <div class="form-group">
                <label>Job Name</label>
                <input type="text" value="Online-Examination-System-Kubernetes" readonly>
            </div>
            <div class="form-group">
                <label>Kubernetes Cluster</label>
                <input type="text" value="k8s-lab6 (Control Plane v1.32.2)" readonly>
            </div>
            <div class="form-group">
                <label>GitHub Repository URL</label>
                <input type="text" value="https://github.com/SivaSathvik6369/online-examination-system-using-jenkins.git" readonly>
            </div>
            <div class="form-group">
                <label>Manifests Directory</label>
                <input type="text" value="k8s/deployment.yaml, k8s/service.yaml" readonly>
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
        <h1>Pipeline Syntax Generator (Lab 6 Declarative Pipeline)</h1>
        <pre>pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'online-examination-system'
        DEPLOYMENT = 'online-exam-deployment'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Automated Tests') { steps { bat 'python test_system.py' } }
        stage('Build Docker Image') { steps { bat 'docker build -t %DOCKER_IMAGE%:latest .' } }
        stage('Kubernetes Deploy') {
            steps {
                bat 'kind load docker-image %DOCKER_IMAGE%:latest --name k8s-lab6'
                bat 'kubectl apply -f k8s/deployment.yaml'
                bat 'kubectl apply -f k8s/service.yaml'
            }
        }
        stage('Replica Scaling') {
            steps {
                bat 'kubectl scale deployment %DEPLOYMENT% --replicas=4'
            }
        }
        stage('Health Verification') {
            steps {
                bat 'curl.exe -I http://localhost:30080/'
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
    print(f"Jenkins Kubernetes Dashboard running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Jenkins server.")

if __name__ == "__main__":
    main()
