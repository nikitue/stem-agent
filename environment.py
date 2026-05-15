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