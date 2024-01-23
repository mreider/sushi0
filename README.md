# Sushi

Shows end-to-end observability using Dynatrace and OpenTelemetry 

## Table of Contents

[About the demo](#About-the-demo)
[Scenario 1](#Scenario-1)

## About the demo

This demo illustrates how valuable Dynatrace is for analyzing OpenTelemetry Traces, Metrics, and Logs. Like any good demo it tells a story, and illustrates some end-to-end use cases involving Kubernetes workloads, CI/CD pipelines, and canary deployments.

Since actual deployments take some time, a short video has been embedded below showing each scenario. There are links to the Dynatrace Perform environment for specific notebooks and screens in each section below.

### Scenario 1

#### Deployment

| App         | Test         |
|-------------|--------------|
| 1.0.0       | HTTP Check   |

- Browse https://deploy.sushi0.cc and explain that this page triggers a CI/CD pipeline on Github
- Explain that the **Deploy** button pushed 1.0.0 of the application and trigger some tests
- No need to deploy anything - since that takes time - the results are what matters
- Don't reveal the scenario until after the analysis

#### Analysis

It makes sense to begin with classic screens and end with the latest-greatest. Start with the Unified Services screen for the sushi-backend. This shows everything in context. 

Begin by going to the new [Distributed Tracing view](https://inx16596.sprint.apps.dynatracelabs.com/ui/apps/dynatrace.distributedtracing) and taking a brief tour of the sushi application. Add the Open Telemetry resource attribute Environment to the list of facets, and narrow down the environments to PROD, TEST, and CANARY. The Histogram will show a nice distribution of the response times and failures.

![scenario1-histogram-overview](scenario1-histogram-overview.png)

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



