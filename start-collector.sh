docker run --rm -p 4317:4317 -p 4318:4318 -v "${PWD}/otel-collector-config.yaml":/otel-collector-config.yaml --name otelcol otel/opentelemetry-collector --config otel-collector-config.yaml
