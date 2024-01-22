# Sushi

Shows end-to-end observability using Dynatrace and OpenTelemetry 

## About the demo

This demo illustrates how valuable Dynatrace is for analyzing OpenTelemetry Traces, Metrics, and Logs. Like any good demo it tells a story, and illustrates some end-to-end use cases involving Kubernetes workloads, CI/CD pipelines, and canary deployments.

## The script

Since actual deployments take some time, a short video has been embedded below showing each scenario. To reproduce these scenarios, or to show someone how the application works, follow these instructions.

### Introduction

Browse https://deploy.sushi0.cc and explain that this page triggers a CI/CD pipeline on Github. The first scenario will deploy version 1.0.0 of the application, and trigger some tests. Run the scenario but do not reveal the situation yet.


## Setup

Fork this repo.

Create the following Github secrets.

```
DOCKER_USERNAME: Your Docker Hub username
DOCKER_PASSWORD: Your Docker Hub token or password
GCP_PROJECT_ID: The ID of your Google Cloud Platform project
GCP_SA_KEY: The JSON key for your GCP Service Account
GKE_CLUSTER_NAME: The Google cluster
GKE_CLUSTER_ZONE: The Availablity Zone of the cluster
FIRST_MONITOR_ID: The ID of a simple HTTP monitor (script below)
MONITOR_ID: The ID of a better synthetic monitor (script below)
DYNATRACE_ENDPOINT: The endpoint URL for your Dynatrace server
DYNATRACE_TOKEN: The API token for Dynatrace. Requires events.ingest,openTelemetryTrace.ingest, syntheticExecutions.read, syntheticExecutions.write
```

The first synthetic monitor script should look like this (replace the URL or IP)

```
{
	"version": "1.0",
	"requests": [
		{
			"description": "sushi0.cc/healthz",
			"url": "https://sushi0.cc/healthz",
			"method": "GET",
			"validation": {
				"rules": [
					{
						"type": "httpStatusesList",
						"value": ">=400",
						"passIfFound": false
					}
				]
			},
			"configuration": {
				"acceptAnyCertificate": true,
				"followRedirects": true,
				"shouldNotPersistSensitiveData": false
			}
		}
	]
}
```

The better synthetic monitor script should look like this (replace the URL or IP)

```
{
    "configuration": {
        "chromiumStartupFlags": {
            "disable-web-security": false
        },
        "device": {
            "orientation": "landscape",
            "deviceName": "Desktop"
        }
    },
    "type": "clickpath",
    "version": "1.0",
    "events": [{
        "type": "navigate",
        "authentication": {
            "type": "http_authentication",
            "credential": {
                "id": "CREDENTIALS_VAULT-0991E887F05B660C"
            }
        },
        "wait": {
            "waitFor": "page_complete"
        },
        "description": "Start",
        "url": "https://sushi0.cc"
    }, {
        "type": "click",
        "wait": {
            "waitFor": "page_complete"
        },
        "target": {
            "locators": [{
                "type": "css",
                "value": "button[type=\"submit\"]"
            }, {
                "type": "css",
                "value": "button:contains(\"Place Order\")"
            }, {
                "type": "css",
                "value": "html body:nth-child(2) div form button"
            }, {
                "type": "css",
                "value": "body div.container form button"
            }]
        },
        "button": 0,
        "description": "click on \"Place Order\""
    }, {
        "type": "click",
        "target": {
            "locators": [{
                "type": "css",
                "value": "#yes"
            }]
        },
        "button": 0,
        "description": "Click Order"
    }]
}
```



