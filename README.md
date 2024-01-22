# Sushi

Shows end-to-end observability using Dynatrace and OpenTelemetry 

## About the demo

- A Github workflow will be triggered when a change is committed
- The workflow will deploy the app to Canary namespace
- A deploy event will be sent to Dynatrace for the canary deploy
- Dynatrace will run a synthetic test to see if the app is running properly
- If it's running properly the workflow will push to prod
- If it's not running the workflow rolls the canary version back
- There are slack integrations triggered in Dynatrace for the test and result
- There is an OTel trace created for the each workflow to see how it went

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
MONITOR_ID: The ID of a Synthetic Monitor in Dynatrace
DYNATRACE_ENDPOINT: The endpoint URL for your Dynatrace server
DYNATRACE_TOKEN: The API token for Dynatrace. Requires events.ingest,openTelemetryTrace.ingest, syntheticExecutions.read, syntheticExecutions.write
```

The Synthetic monitor script should look like this (replace the IP address of your Load Balancer)

```
{
  "version": "2.0",
  "type": "clickpath",
  "configuration": {
    "userAgent": "",
    "isMobile": false,
    "touchEnabled": false,
    "width": 1920,
    "height": 1080,
    "deviceScale": 1.0,
    "emulateNetworkConditions": false,
    "offline": false,
    "latency": 0,
    "downloadThroughput": -1,
    "uploadThroughput": -1,
    "deviceName": "Desktop",
    "bypassCSP": false,
    "syntheticFlags": {
      "mf": false
    },
    "chromiumStartupFlags": {
      "disable-web-security": false
    },
    "useIESupportedAgent": false,
    "customDevice": false
  },
  "actions": [
    {
      "index": 1,
      "type": "navigate",
      "description": "Loading of \"http://35.231.112.144.nip.io/\"",
      "url": "http://35.231.112.144.nip.io/",
      "target": {
        "targetWindow": "window[0]",
        "locators": {
          "rules": []
        }
      },
      "validate": [],
      "wait": {
        "type": "wait",
        "criteria": "page_complete"
      }
    },
    {
      "index": 2,
      "type": "click",
      "description": "click on \"Place Order\"",
      "button": 0,
      "target": {
        "targetWindow": "window[0]",
        "locators": {
          "rules": [
            {
              "type": "css",
              "value": "button[type\u003d\"submit\"]"
            },
            {
              "type": "css",
              "value": "button:contains(\"Place Order\")"
            },
            {
              "type": "css",
              "value": "html body:nth-child(7) div form button"
            },
            {
              "type": "css",
              "value": "body div.container form button"
            }
          ]
        }
      },
      "validate": [
        {
          "type": "validate",
          "criteria": "element_match",
          "match": "🍣",
          "isRegex": true,
          "failureIfFound": false,
          "target": {
            "targetWindow": "window[0]",
            "locators": {
              "rules": [
                {
                  "type": "css",
                  "value": "div[class\u003d\"emoji\"]"
                }
              ]
            }
          }
        }
      ],
      "wait": {
        "type": "wait",
        "criteria": "page_complete"
      }
    }
  ],
  "internalConfiguration": {
    "enablePlaceholders": true
  }
}
```





