"""
Autonomous Command Center Dashboard Backend
Provides a web interface for Governing Officer Tarwater to monitor ecosystem health,
view pending PRs, and trigger manual governance actions.
Governing Authority: Governing Officer Tarwater
"""

import os
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

GITHUB_API_URL = "https://api.github.com"
MANAGED_REPOS = [
    "Pat333-ux/autonomous-governance-core",
    "Pat333-ux/autonomous-agent-swarm",
    "Pat333-ux/autonomous-sandbox-runner",
    "Pat333-ux/autonomous-memory-vault"
]


def get_github_headers() -> dict:
    token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


@app.route("/")
def index():
    """Renders the main command center dashboard."""
    return render_template("index.html", repos=MANAGED_REPOS)


@app.route("/api/health")
def api_health():
    """Fetches live status and open PR counts for all managed repositories."""
    headers = get_github_headers()
    repo_statuses = []

    for repo in MANAGED_REPOS:
        url = f"{GITHUB_API_URL}/repos/{repo}"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            # Fetch open PRs count
            pr_resp = requests.get(f"{GITHUB_API_URL}/repos/{repo}/pulls", headers=headers, timeout=10)
            open_prs = len(pr_resp.json()) if pr_resp.status_code == 200 else 0

            repo_statuses.append({
                "name": repo,
                "stars": data.get("stargazers_count", 0),
                "open_prs": open_prs,
                "status": "ONLINE"
            })
        else:
            repo_statuses.append({
                "name": repo,
                "stars": 0,
                "open_prs": 0,
                "status": "ERROR / UNREACHABLE"
            })

    return jsonify({"ecosystem_status": "GOVERNED", "repositories": repo_statuses})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
