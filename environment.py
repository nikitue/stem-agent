import json
import random

class MockDevOpsEnvironment:
    """
    Simulates a deterministic DevOps ecosystem. 
    Returns consistent responses to ensure evaluation metrics reflect agent evolution, not environmental changes.
    """
    def __init__(self):
        # Simulated State
        self.active_alerts = [
            "ALERT: 502 Bad Gateway on /api/v1/auth",
            "WARNING: High CPU utilization on redis-cache-node-03"
        ]
        
        # Simulated Databases and Logs
        self.metrics_db = {
            "auth-service": {"cpu": "45%", "memory": "512MB", "db_connection": "TIMEOUT"},
            "redis-cache": {"cpu": "99%", "memory": "4GB", "cache_hits": "85%"}
        }
        
        self.logs_db = {
            "auth-service": ["INFO: Starting auth service", "ERROR: Postgres timeout connecting to 10.0.0.5"],
            "redis-cache": ["WARN: Max memory reached, evicting keys", "INFO: Saving dump.rdb"]
        }
        
        # The model needs more hand-holding to navigate
        self.runbooks = {
            "checkout": "Runbook [Checkout]: Use query_metrics on 'payment-db' and 'redis-cache'. If DB EXHAUSTED, check deployments for 'checkout-service' and rollback_deployment on 'checkout-service'. If Cache MAXED_OUT, scale up the cache.",
        }

    # Observability tools
    def query_metrics(self, service_name: str, metric_type: str = "all") -> str:
        """Queries Datadog/Prometheus for current service metrics."""
        if service_name in self.metrics_db:
            return json.dumps(self.metrics_db[service_name])
        return f"Error: Service '{service_name}' not found."

    def grep_recent_logs(self, service_name: str) -> str:
        """Searches Splunk/ElasticSearch for recent application logs."""
        if service_name in self.logs_db:
            return "\n".join(self.logs_db[service_name])
        return f"Error: No logs found for '{service_name}'."

   # Knowledge base
    def search_runbooks(self, query: str) -> str:
        """Searches Confluence for Standard Operating Procedures (SOPs)."""
        for key, text in self.runbooks.items():
            # Basic text matching simulation
            if any(word in query.lower() for word in key.split()):
                return text
        return "No runbook found matching your query."

   # ActuationTools
    def restart_kubernetes_pod(self, pod_name: str) -> str:
        """Executes a kubectl restart command."""
        return f"SUCCESS: Pod '{pod_name}' is terminating and will restart."

    def escalate_to_human(self, team: str, reason: str) -> str:
        """Pages a human via PagerDuty."""
        return f"PAGED: The {team} team has been alerted. Reason: {reason}"

    def resolve_ticket(self, summary: str) -> str:
        """Closes the ticket in Jira."""
        return f"TICKET CLOSED: {summary}"

class AdvancedDevOpsEnvironment:
    def __init__(self):
        self.dependencies = {
            "frontend-web": ["api-gateway"],
            "api-gateway": ["checkout-service"],
            "checkout-service": ["payment-db", "redis-cache"]
        }

        # Randomize the root cause for this run
        self.root_cause = random.choice(["db_lock", "cache_oom"])

        # The surface-level alert is always the same
        self.active_alerts = ["USER REPORT: Users cannot complete checkout."]

        # State changes based on the hidden root cause
        # The root cause is either cache issue or a db issue
        if self.root_cause == "db_lock":
            self.metrics = {
                "payment-db": {"cpu": "45%", "connections": "EXHAUSTED"},
                "redis-cache": {"memory": "2GB", "status": "HEALTHY"}
            }
            self.deployments = {"checkout-service": "v2.1.4 (Deployed 5 mins ago)"}
        else:
            self.metrics = {
                "payment-db": {"cpu": "10%", "connections": "NORMAL"},
                "redis-cache": {"memory": "MAXED_OUT", "status": "OOM_EVICTING"}
            }
            self.deployments = {"checkout-service": "v2.1.3 (Deployed 2 days ago)"}

        self.runbooks = {
            "checkout": "Runbook [Checkout]: 1. query_metrics on 'payment-db' and 'redis-cache'. 2. If DB EXHAUSTED, check_recent_deployments for 'checkout-service' and use rollback_deployment on 'checkout-service'. 3. If Cache MAXED_OUT, use scale_up_cache.",
        }

    def trace_dependencies(self, service_name: str) -> str:
        deps = self.dependencies.get(service_name, [])
        return f"Service '{service_name}' depends on: {', '.join(deps) if deps else 'None'}"

    # Observability tools
    def query_metrics(self, service_name: str) -> str:
        """Crucial diagnostic tool to determine the branching path."""
        if service_name in self.metrics:
            return json.dumps(self.metrics[service_name])
        return f"Error: No metrics for {service_name}"

    def check_recent_deployments(self, service_name: str) -> str:
        return self.deployments.get(service_name, "No recent deployments.")

    def search_runbooks(self, query: str) -> str:
        for key, text in self.runbooks.items():
            if any(word in query.lower() for word in key.split()):
                return text
        return "No runbook found."

    def rollback_deployment(self, service_name: str) -> str:
        if self.root_cause == "db_lock" and service_name == "checkout-service":
            return "SUCCESS TICKET CLOSED: checkout-service rolled back. DB locks cleared."
        return "CRITICAL FAILURE: Rolled back healthy service. Outage worsened."

    def scale_up_cache(self) -> str:
        if self.root_cause == "cache_oom":
            return "SUCCESS TICKET CLOSED: redis-cache scaled up. Memory cleared."
        return "CRITICAL FAILURE: Scaled up cache unnecessarily, wasting resources."

    def resolve_ticket(self, summary: str) -> str:
        return f"TICKET CLOSED: {summary}"