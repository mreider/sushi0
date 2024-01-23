from flask import Flask, jsonify, render_template, request
import requests
import os
import sys
import logging
import json
from opentelemetry import trace
from opentelemetry import propagate
from opentelemetry.context import Context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

auth = HTTPBasicAuth()

users = {
    "sushi": generate_password_hash("sushi")
}

merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json", "/var/lib/dynatrace/enrichment/dt_host_metadata.json"]:
  try:
    data = ''
    with open(name) as f:
      data = json.load(f if name.startswith("/var") else open(f.read()))
      merged.update(data)
  except:
    pass


# Logging and Tracer Configuration
logging.basicConfig(level=logging.INFO)
SERVICE_NAME = os.getenv('SERVICE_NAME', 'frontend')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'default-env')

merged.update({
    "service.name": SERVICE_NAME, 
    "service.version": SERVICE_VERSION,
    "environment": ENVIRONMENT
})

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(merged)
    )
)
endpoint = os.getenv('DYNATRACE_ENDPOINT') + "/api/v2/otlp/v1/traces"
token = os.getenv('DYNATRACE_TOKEN')
logger_provider = LoggerProvider(resource=Resource.create(merged))
set_logger_provider(logger_provider)


logger_provider.add_log_record_processor(
  BatchLogRecordProcessor(OTLPLogExporter(
    endpoint = os.getenv('DYNATRACE_ENDPOINT') + "/api/v2/otlp/v1/logs",
	headers = {"Authorization": "Api-Token " + token}
  ))
)
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)
tracer = trace.get_tracer(__name__)


headers = {
"Authorization": f"Api-Token {token}",
"Content-Type": "application/x-protobuf"
}

span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, headers=headers))
trace.get_tracer_provider().add_span_processor(span_processor)
FlaskInstrumentor().instrument_app(app)

# Route Definitions

@auth.verify_password
def verify_password(un, pw):
    if un in users and \
            check_password_hash(users.get(un), pw):
        return un


@app.route('/healthz')
def healthz():
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
@auth.login_required
def index():
    current_span = trace.get_current_span()
    current_span.set_attribute("span.name", "serve-menu")
    return render_template('index.html')

@app.route('/order', methods=['POST'])
@auth.login_required
def order():
    current_span = trace.get_current_span()
    current_span.set_attribute("span.name", "receive-order")
    headers = {}
    propagate.inject(headers, context=Context.current())
    response = requests.post(os.environ['BACKEND_URL'], headers=headers)

    if response.status_code == 200:
        logging.info("order successful")
        try:
            emoji = response.json()['emoji']
        except ValueError:
            # Handle JSON decode error
            emoji = "Error: Invalid response"
    else:
        # Handle non-200 responses
        logging.error(f"Error: Response code {response.status_code}")
        emoji = f"Error: Response code {response.status_code}"
    return render_template('index.html', emoji=emoji)


# Application Start
if __name__ == "__main__":
    port = 5000  # default port
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(debug=True, port=port, host='0.0.0.0')
