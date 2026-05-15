import json

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
        
        self.runbooks = {
            "502 auth": "Runbook [Auth 502]: Check database connection metrics. If TIMEOUT, restart the auth-db-pool pod.",
            "high cpu redis": "Runbook [Redis CPU]: Check logs for 'evicting keys'. If present, escalate to Database team to scale up."
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
    
import json

class AdvancedDevOpsEnvironment:
    def __init__(self):
        # Services depend on each other
        self.dependencies = {
            "frontend-web": ["api-gateway"],
            "api-gateway": ["auth-service", "checkout-service"],
            "checkout-service": ["payment-db", "redis-cache"],
            "auth-service": ["user-db"]
        }

        # A cascading failure scenario
        # A bad deployment on checkout-service is causing the payment-db to lock up.
        self.active_alerts = [
            "CRITICAL: High error rate on frontend-web",
            "WARNING: 504 Gateway Timeout on api-gateway",
            "CRITICAL: DB Connection Pool Exhausted on checkout-service"
        ]

        self.deployments = {
            "checkout-service": "v2.1.4 (Deployed 5 mins ago)",
            "frontend-web": "v1.9.0 (Deployed 2 days ago)"
        }

        self.logs_db = {
            "frontend-web": [
                "INFO: User clicked checkout", 
                "ERROR: Request to api-gateway timed out after 30s"
            ],
            "api-gateway": [
                "INFO: Routing request to checkout-service", 
                "ERROR: Upstream connection refused: checkout-service"
            ],
            "checkout-service": [
                "INFO: Starting migration script v2.1.4",
                "FATAL: Deadlock detected in payment-db transaction",
                "WARN: Connection pool exhausted"
            ]
        }

        self.runbooks = {
            "gateway timeout": "Runbook [504 Timeout]: Trace dependencies to find the failing upstream service. Check its recent deployments.",
            "db pool exhausted": "Runbook [DB Exhaustion]: If a recent deployment caused a DB lock, IMMEDIATELY rollback the deployment. Do not attempt to restart the database."
        }

    # Diagnostic tools
    def trace_dependencies(self, service_name: str) -> str:
        """Returns the downstream services this service relies on."""
        deps = self.dependencies.get(service_name, [])
        return f"Service '{service_name}' depends on: {', '.join(deps) if deps else 'None'}"

    def check_recent_deployments(self, service_name: str) -> str:
        """Checks if a service was deployed recently."""
        return self.deployments.get(service_name, "No recent deployments in the last 24 hours.")

    def grep_recent_logs(self, service_name: str) -> str:
        """Searches logs for a specific service."""
        return "\n".join(self.logs_db.get(service_name, ["No logs found."]))

    def search_runbooks(self, query: str) -> str:
        """Searches the internal Wiki."""
        for key, text in self.runbooks.items():
            if any(word in query.lower() for word in key.split()):
                return text
        return "No runbook found."

    #Actuation tools (agent should choose appropriate fix)
    def rollback_deployment(self, service_name: str) -> str:
        """Rolls back a service to its previous stable version."""
        if service_name == "checkout-service":
            return "SUCCESS: checkout-service rolled back to v2.1.3. DB locks cleared. System recovering."
        return f"FAILED: Cannot rollback {service_name}, no faulty deployment detected."

    def restart_database(self, db_name: str) -> str:
        """Restarts a database cluster (DANGEROUS)."""
        return f"CRITICAL FAILURE: Restarting {db_name} during a deadlock caused data corruption. Escalation required."

    def resolve_ticket(self, summary: str) -> str:
        return f"TICKET CLOSED: {summary}"