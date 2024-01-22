from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import requests
import os
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()
app.secret_key = 'foo-bar-bz'
users = {"sushi": generate_password_hash("sushi")}

@auth.verify_password
def verify_password(un, pw):
    if un in users and check_password_hash(users.get(un), pw):
        return un

@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def index():
    scenario = request.args.get('scenario', '1')
    response = session.pop('response', '')
    return render_template('index.html', scenario=scenario, response=response)

@app.route('/healthz')
def healthz():
    return jsonify({'status': 'healthy'}), 200

@app.route('/run', methods=['POST'])
@auth.login_required
def order():
    scenario = request.form.get('scenario')
    version_map = {'1': '1.0.1', '2': '1.0.1', '3': '1.0.0', '4': '1.0.0'}
    test_map = {'1': '1', '2': '2', '3': '1', '4': '2'}
    version_number = version_map.get(scenario, '1.0.0')
    run_synthetic = test_map.get(scenario, '1')
    trigger_github_workflow(version_number, run_synthetic)
    session['response'] = f'<ul><li>Version deployed: {version_number}</li><li>Test triggered: {run_synthetic}</li></ul>'
    return redirect(url_for('index', scenario=scenario))

def trigger_github_workflow(version_number, run_synthetic):
    token = os.getenv('GITHUB_TOKEN')
    repo = 'mreider/sushi0'
    event_type = 'deploy'
    url = f'https://api.github.com/repos/{repo}/dispatches'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    data = {'event_type': event_type, 'client_payload': {'version_number': version_number, 'run_synthetic': run_synthetic}}
    response = requests.post(url, headers=headers, json=data)
    print("Workflow triggered, status code:", response.status_code)

if __name__ == "__main__":
    port = 5000
    app.run(debug=True, port=port, host='0.0.0.0')
