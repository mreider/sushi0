from flask import Flask, jsonify, make_response, request
import os
import sys
import random
import time
import json
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics.export import (AggregationTemporality,PeriodicExportingMetricReader,)
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, ObservableUpDownCounter
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider
import mysql.connector
from opentelemetry.instrumentation.dbapi import trace_integration

db_user = 'sushi'
db_password = 'sushi'
db_host = 'sushi-db'
db_database = 'sushi'
trace_integration(mysql.connector, "connect", "mysql")


app = Flask(__name__)
merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json", "/var/lib/dynatrace/enrichment/dt_host_metadata.json"]:
  try:
    data = ''
    with open(name) as f:
      data = json.load(f if name.startswith("/var") else open(f.read()))
      merged.update(data)
  except:
    pass

logging.basicConfig(level=logging.INFO)
trace_endpoint = os.getenv('DYNATRACE_ENDPOINT') + "/api/v2/otlp/v1/traces"
metric_endpoint = os.getenv('DYNATRACE_ENDPOINT') + "/api/v2/otlp/v1/metrics"
token = os.getenv('DYNATRACE_TOKEN')
if not token:
    print("DYNATRACE_TOKEN environment variable is not set.")
trace_headers = {
"Authorization": f"Api-Token {token}",
"Content-Type": "application/x-protobuf"
}
metric_headers = {
"Authorization": f"Api-Token {token}"
}

SERVICE_NAME = os.getenv('SERVICE_NAME', 'backend')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'canary')
merged.update({
    "service.name": SERVICE_NAME, 
    "service.version": SERVICE_VERSION,
    "environment": ENVIRONMENT
})

logger_provider = LoggerProvider(resource=Resource.create(merged))
logger_provider.add_log_record_processor(
  BatchLogRecordProcessor(OTLPLogExporter(
    endpoint = os.getenv('DYNATRACE_ENDPOINT') + "/api/v2/otlp/v1/logs",
	headers = {"Authorization": "Api-Token " + token}
  ))
)
set_logger_provider(logger_provider)
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create(merged)
    )
)
logging.getLogger().addHandler(handler)
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=trace_endpoint, headers=trace_headers))
trace.get_tracer_provider().add_span_processor(span_processor)
FlaskInstrumentor().instrument_app(app)
metric_exporter = OTLPMetricExporter(
  endpoint = metric_endpoint,
  headers = metric_headers,
  preferred_temporality = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
  }
)
reader = PeriodicExportingMetricReader(metric_exporter)
provider = MeterProvider(metric_readers=[reader], resource=Resource.create(merged))
set_meter_provider(provider)
meter = get_meter_provider().get_meter("order-counter", "1.0.0")

orders_received_counter = meter.create_counter(
    "orders_received",
    description="Total number of orders received",
)
orders_fulfilled_counter = meter.create_counter(
    "orders_fulfilled",
    description="Total number of orders fulfilled",
)

def get_sushi_by_type(where_clause):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
        cursor = conn.cursor()
        query = "SELECT id FROM sushi WHERE " + where_clause
        cursor.execute(query)
        sushi_data = cursor.fetchall()
        return sushi_data
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/', methods=['POST'])
def index():
    orders_received_counter.add(1)
    current_span = trace.get_current_span()
    current_span.set_attribute("span.name", "process-order")
    current_span.set_attribute("order.received", "True")
    milliseconds = random.randint(100, 500)
    seconds = milliseconds / 1000.0
    time.sleep(seconds)
    # Check if a fix SHA exists in the version number - this represents a test, and always fails
    # The other (1.0.0 or 1.0.1) will send a 200 but with different results, thus the need for synthetic tests
    version_parts = os.environ['SERVICE_VERSION'].split('.')
    if len(version_parts) > 3:
        # If there's a fix SHA (1.0.0.fixsha), return a 500 Internal Server Error
        get_sushi_by_type("typo = 'miso'") # This will create a db error
        orders_fulfilled_counter.add(0)
        current_span.set_attribute("order.fulfilled", "False")
        current_span.set_attribute("span.status", "ERROR")
        logging.error("500 Internal Server Error")
        return make_response(jsonify(error="Internal Server Error"), 500)
    patch_digit = os.environ['SERVICE_VERSION'].split('.')[2][0]
    patch_number = int(patch_digit)
    if patch_number % 2 != 0:
        get_sushi_by_type("typo = 'miso'")
        current_span.set_attribute("order.fulfilled", "False")
        logging.info("Did not fulfill order")
        current_span.set_attribute("span.status", "OK")
        emoji = '<span id="no">❌</span>'
    else:
        get_sushi_by_type("type = 'nigiri'")
        current_span.set_attribute("order.fulfilled", "True")
        orders_fulfilled_counter.add(1)
        emoji = '<span id="yes">🍣</span>'
        logging.info("Order fulfilled")
        current_span.set_attribute("span.status", "OK")
    return jsonify(emoji=emoji)

if __name__ == "__main__":
    port = 5000  # default port
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(debug=True, port=port, host='0.0.0.0')