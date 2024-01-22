from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'foo-bar-bz'

@app.route('/')
def index():
    response = session.pop('response', '')
    return render_template('index.html', response=response)


@app.route('/healthz')
def healthz():
    # Perform any necessary health checks here
    # Example: Check database connection, external dependencies, etc.

    # If checks pass, return an HTTP 200 OK response
    return jsonify({'status': 'healthy'}), 200

@app.route('/run', methods=['POST'])
def order():
    version_number = request.form.get('version_number', '1.0.0')
    run_synthetic = 'true' if 'run_synthetic' in request.form else 'false'
    trigger_github_workflow(version_number, run_synthetic)
    session['response'] = f'Workflow triggered with version={version_number}, run_synthetic={run_synthetic}'
    return redirect(url_for('index'))

def trigger_github_workflow( version_number, run_synthetic):
    token = os.getenv('GITHUB_TOKEN')
    repo = 'mreider/sushi'
    event_type = 'deploy'

    url = f'https://api.github.com/repos/{repo}/dispatches'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'event_type': event_type,
        'client_payload': {
            'version_number': version_number,
            'run_synthetic': run_synthetic
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Workflow triggered, status code:", response.status_code)

# Application Start
if __name__ == "__main__":
    port = 5000  # default port
    app.run(debug=True, port=port, host='0.0.0.0')
