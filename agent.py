"""
LangGraph Agent for Anomaly Detection and Auto-Scaling
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import os
import time
from datetime import datetime


class AgentState(TypedDict):
    alert: str
    action: str
    metrics: Optional[dict]
    timestamp: Optional[str]
    severity: Optional[str]


def detect_anomaly(state):
    """Detect anomalies in system metrics"""
    # Analyze metrics to determine if scaling is needed
    metrics = state.get("metrics", {})
    alert = state.get("alert", "")
    
    # Example anomaly detection logic
    cpu_usage = metrics.get("cpu_usage", 0)
    memory_usage = metrics.get("memory_usage", 0)
    latency_p95 = metrics.get("latency_p95", 0)
    error_rate = metrics.get("error_rate", 0)
    
    # Determine action based on metrics
    if cpu_usage > 80 or memory_usage > 85 or latency_p95 > 2000 or error_rate > 0.05:
        state["action"] = "scale_up_replicas"
        state["severity"] = "high"
        state["alert"] = f"High resource usage detected: CPU={cpu_usage}%, Memory={memory_usage}%, Latency={latency_p95}ms, Errors={error_rate}"
    elif cpu_usage < 30 and memory_usage < 40:
        state["action"] = "scale_down_replicas"
        state["severity"] = "low"
        state["alert"] = f"Low resource usage: CPU={cpu_usage}%, Memory={memory_usage}%"
    else:
        state["action"] = "no_action"
        state["severity"] = "normal"
        state["alert"] = "System operating normally"
    
    state["timestamp"] = datetime.utcnow().isoformat()
    return state


def scale_up_replicas(state):
    """Scale up Kubernetes replicas"""
    action = state.get("action")
    
    if action == "scale_up_replicas":
        # In production, this would call Kubernetes API
        # Example: kubectl scale deployment rag-platform-api --replicas=5
        print(f"🚀 Scaling up replicas - {state.get('alert')}")
        
        # Simulate API call (replace with actual K8s API call)
        # from kubernetes import client, config
        # config.load_incluster_config()
        # apps_v1 = client.AppsV1Api()
        # deployment = apps_v1.read_namespaced_deployment(
        #     name="rag-platform-api", namespace="rag-platform"
        # )
        # deployment.spec.replicas = min(deployment.spec.replicas + 2, 10)
        # apps_v1.patch_namespaced_deployment(
        #     name="rag-platform-api", namespace="rag-platform", body=deployment
        # )
    
    return state


def scale_down_replicas(state):
    """Scale down Kubernetes replicas"""
    action = state.get("action")
    
    if action == "scale_down_replicas":
        print(f"📉 Scaling down replicas - {state.get('alert')}")
        
        # Simulate API call (replace with actual K8s API call)
        # Similar to scale_up_replicas but decrease replicas
    
    return state


def log_action(state):
    """Log the action taken"""
    action = state.get("action")
    alert = state.get("alert")
    severity = state.get("severity")
    
    print(f"📝 [{severity.upper()}] {action}: {alert}")
    
    # In production, log to monitoring system (Prometheus, Grafana, etc.)
    # structured_log("INFO", "Auto-scaling action", 
    #                action=action, severity=severity, alert=alert)
    
    return state


# Create the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("detect", detect_anomaly)
graph.add_node("scale_up", scale_up_replicas)
graph.add_node("scale_down", scale_down_replicas)
graph.add_node("log", log_action)

# Set entry point
graph.set_entry_point("detect")

# Add conditional edges based on action
graph.add_conditional_edges(
    "detect",
    lambda state: state.get("action"),
    {
        "scale_up_replicas": "scale_up",
        "scale_down_replicas": "scale_down",
        "no_action": "log"
    }
)

# Connect scaling actions to log
graph.add_edge("scale_up", "log")
graph.add_edge("scale_down", "log")

# Log always ends
graph.add_edge("log", END)

# Compile the agent
agent = graph.compile()


def run_anomaly_detection(metrics: dict) -> dict:
    """Run anomaly detection with given metrics"""
    initial_state = {
        "alert": "",
        "action": "",
        "metrics": metrics,
        "timestamp": None,
        "severity": None
    }
    
    result = agent.invoke(initial_state)
    return result


# Example usage
if __name__ == "__main__":
    # Example metrics
    test_metrics = {
        "cpu_usage": 85,      # High CPU
        "memory_usage": 90,   # High Memory
        "latency_p95": 2500,  # High latency
        "error_rate": 0.08    # High error rate
    }
    
    print("🔍 Running anomaly detection...")
    result = run_anomaly_detection(test_metrics)
    
    print(f"\n📊 Result:")
    print(f"  Action: {result['action']}")
    print(f"  Alert: {result['alert']}")
    print(f"  Severity: {result['severity']}")
    print(f"  Timestamp: {result['timestamp']}")

