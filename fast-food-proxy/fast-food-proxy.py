import time
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (OTLPSpanExporter,)
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,)
import logging
import random
import json
import os


merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json", "/var/lib/dynatrace/enrichment/dt_host_metadata.json"]:
  try:
    data = ''
    with open(name) as f:
      data = json.load(f if name.startswith("/var") else open(f.read()))
      merged.update(data)
  except:
    pass

SERVICE_NAME = os.getenv('SERVICE_NAME', 'proxy')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'canary')

merged.update({
    "service.name": SERVICE_NAME,
    "service.version": SERVICE_VERSION,
    "environment": ENVIRONMENT
})

endpoint = "https://bmm59542.dev.dynatracelabs.com/api/v2/otlp/v1/traces"
resource = Resource.create(merged)
token_string = "Api-Token " + os.getenv('DYNATRACE_TOKEN')
format = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
tracer_provider = TracerProvider(resource=resource)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint,headers={ "Authorization": token_string}))
tracer_provider.add_span_processor(span_processor)
RequestsInstrumentor().instrument()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s")
logger = logging.getLogger(__name__)

def do_constantly():
    with tracer.start_as_current_span("post-order"):
        headers = {'Accept': 'text/plain'}
        resp = requests.post(url="http://thumbs-up-frontend-service-internal:5000/order", headers=headers)
        logger.info(resp.status_code)

while True:
    do_constantly()
    frequency = float(os.getenv('FREQUENCY', 1)) 
    seconds = random.uniform(frequency, 11)
    time.sleep(seconds)