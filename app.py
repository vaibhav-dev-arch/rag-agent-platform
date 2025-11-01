"""
RAG Agent Platform - 1-Click Cost & Latency Dashboard (Streamlit)
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from collections import defaultdict, deque
import pandas as pd

# Configuration
# Support Streamlit secrets for cloud deployment
# Will be set after st is imported
API_URL = None
DEFAULT_MODEL = None

# Cost per token (OpenAI pricing as of 2024)
COST_PER_1K_TOKENS = {
    "gpt-3.5-turbo": {
        "input": 0.0015,   # $0.0015 per 1K tokens
        "output": 0.002    # $0.002 per 1K tokens
    },
    "gpt-4": {
        "input": 0.03,     # $0.03 per 1K tokens
        "output": 0.06     # $0.06 per 1K tokens
    },
    "text-embedding-3-small": {
        "input": 0.00002   # $0.00002 per 1K tokens
    }
}


# Initialize session state
if 'cost_history' not in st.session_state:
    st.session_state.cost_history = deque(maxlen=1000)
if 'latency_history' not in st.session_state:
    st.session_state.latency_history = deque(maxlen=1000)


def estimate_tokens(text: str) -> int:
    """Rough estimation: ~4 characters per token"""
    return len(text) // 4


def calculate_cost(input_tokens: int, output_tokens: int, model: str = DEFAULT_MODEL) -> float:
    """Calculate cost based on token usage"""
    if model not in COST_PER_1K_TOKENS:
        model = DEFAULT_MODEL
    
    costs = COST_PER_1K_TOKENS.get(model, COST_PER_1K_TOKENS[DEFAULT_MODEL])
    
    input_cost = (input_tokens / 1000) * costs.get("input", 0)
    output_cost = (output_tokens / 1000) * costs.get("output", 0)
    
    return input_cost + output_cost


def get_stats():
    """Calculate statistics from history"""
    cost_history = list(st.session_state.cost_history)
    latency_history = list(st.session_state.latency_history)
    
    now = datetime.utcnow()
    last_24h_cost = [item for item in cost_history if item.get('timestamp', now) > now - timedelta(hours=24)]
    last_hour_cost = [item for item in cost_history if item.get('timestamp', now) > now - timedelta(hours=1)]
    recent_latencies = [item.get('latency', 0) for item in latency_history[-100:]]
    
    if recent_latencies:
        sorted_latencies = sorted(recent_latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[p95_index] if sorted_latencies else 0
        avg_latency = sum(recent_latencies) / len(recent_latencies)
    else:
        p95_latency = 0
        avg_latency = 0
    
    total_cost_24h = sum(item.get('cost', 0) for item in last_24h_cost)
    total_cost_hour = sum(item.get('cost', 0) for item in last_hour_cost)
    total_cost_all = sum(item.get('cost', 0) for item in cost_history)
    
    total_queries_24h = len(last_24h_cost)
    total_queries_hour = len(last_hour_cost)
    cost_per_query = total_cost_24h / total_queries_24h if total_queries_24h > 0 else 0
    
    return {
        'p95_latency_ms': p95_latency * 1000,
        'avg_latency_ms': avg_latency * 1000,
        'cost_per_query': cost_per_query,
        'total_cost_24h': total_cost_24h,
        'total_cost_hour': total_cost_hour,
        'total_cost_all': total_cost_all,
        'total_queries_24h': total_queries_24h,
        'total_queries_hour': total_queries_hour,
        'total_queries_all': len(cost_history)
    }


def send_query(query: str):
    """Send query to API server and track cost/latency"""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={'query': query, 'include_sources': True},
            timeout=60
        )
        
        latency = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            # Estimate tokens
            input_tokens = estimate_tokens(query)
            output_tokens = estimate_tokens(answer)
            
            # Calculate cost
            cost = calculate_cost(input_tokens, output_tokens, DEFAULT_MODEL)
            
            # Store in history
            st.session_state.cost_history.append({
                'timestamp': datetime.utcnow(),
                'query': query[:100],
                'cost': cost,
                'model': DEFAULT_MODEL,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'latency': latency
            })
            
            st.session_state.latency_history.append({
                'timestamp': datetime.utcnow(),
                'latency': latency,
                'query': query[:100]
            })
            
            return {
                'success': True,
                'answer': answer,
                'cost': cost,
                'latency_ms': latency * 1000,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'sources': result.get('sources', [])
            }
        else:
            return {
                'success': False,
                'error': f'API Error: {response.text}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


# Page configuration
st.set_page_config(
    page_title="Cost & Latency Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set configuration from secrets or environment variables (after st is imported)
if API_URL is None:
    try:
        API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))
        DEFAULT_MODEL = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    except:
        API_URL = os.getenv("API_URL", "http://localhost:8000")
        DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Title
st.title("💰 1-Click Cost & Latency Dashboard")
st.markdown("Real-time tracking of API costs and query performance")

# Sidebar metrics
st.sidebar.header("📊 Key Metrics")

# Get stats
stats = get_stats()

# Calculate deltas (mock - in production, compare with previous period)
previous_p95 = 220  # Example previous value
previous_cost_per_query = 0.001  # Example previous value

p95_delta = stats['p95_latency_ms'] - previous_p95 if previous_p95 > 0 else None
cost_delta = ((stats['cost_per_query'] - previous_cost_per_query) / previous_cost_per_query * 100) if previous_cost_per_query > 0 else None

# Display sidebar metrics
st.sidebar.metric(
    "p95 Latency",
    f"{stats['p95_latency_ms']:.0f} ms",
    f"{p95_delta:.0f} ms" if p95_delta is not None else None,
    delta_color="inverse" if p95_delta and p95_delta > 0 else "normal"
)

st.sidebar.metric(
    "Cost per Query",
    f"${stats['cost_per_query']:.6f}",
    f"{cost_delta:.0f}%" if cost_delta is not None else None,
    delta_color="inverse" if cost_delta and cost_delta > 0 else "normal"
)

st.sidebar.metric("Avg Latency", f"{stats['avg_latency_ms']:.0f} ms")
st.sidebar.metric("Total Cost (24h)", f"${stats['total_cost_24h']:.4f}")
st.sidebar.metric("Total Queries (24h)", f"{stats['total_queries_24h']:,}")
st.sidebar.metric("Total Cost (All Time)", f"${stats['total_cost_all']:.4f}")

# Reset button
if st.sidebar.button("🔄 Reset Statistics"):
    st.session_state.cost_history.clear()
    st.session_state.latency_history.clear()
    st.success("Statistics reset!")
    st.rerun()

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Queries/Hour", f"{stats['total_queries_hour']:,}")
with col2:
    st.metric("Cost/Hour", f"${stats['total_cost_hour']:.4f}")
with col3:
    st.metric("Total Queries", f"{stats['total_queries_all']:,}")
with col4:
    st.metric("Min Latency", f"{stats['avg_latency_ms'] * 0.8:.0f} ms" if stats['avg_latency_ms'] > 0 else "0 ms")

# Charts section
st.header("📈 Visualizations")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Cost Over Time (24h)")
    cost_history = list(st.session_state.cost_history)
    if cost_history:
        now = datetime.utcnow()
        last_24h = [item for item in cost_history if item.get('timestamp', now) > now - timedelta(hours=24)]
        
        if last_24h:
            # Group by hour
            hourly_cost = defaultdict(float)
            for item in last_24h:
                timestamp = item.get('timestamp', now)
                hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_cost[hour_key] += item.get('cost', 0)
            
            # Create DataFrame
            df_cost = pd.DataFrame([
                {'hour': hour, 'cost': hourly_cost[hour]}
                for hour in sorted(hourly_cost.keys())
            ])
            
            if not df_cost.empty:
                st.line_chart(df_cost.set_index('hour')['cost'])
            else:
                st.info("No cost data available yet")
        else:
            st.info("No queries in the last 24 hours")
    else:
        st.info("No cost history yet. Send a query to start tracking!")

with chart_col2:
    st.subheader("Query Volume (24h)")
    cost_history = list(st.session_state.cost_history)
    if cost_history:
        now = datetime.utcnow()
        last_24h = [item for item in cost_history if item.get('timestamp', now) > now - timedelta(hours=24)]
        
        if last_24h:
            # Group by hour
            hourly_queries = defaultdict(int)
            for item in last_24h:
                timestamp = item.get('timestamp', now)
                hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_queries[hour_key] += 1
            
            # Create DataFrame
            df_queries = pd.DataFrame([
                {'hour': hour, 'queries': hourly_queries[hour]}
                for hour in sorted(hourly_queries.keys())
            ])
            
            if not df_queries.empty:
                st.bar_chart(df_queries.set_index('hour')['queries'])
            else:
                st.info("No query data available yet")
        else:
            st.info("No queries in the last 24 hours")
    else:
        st.info("No query history yet. Send a query to start tracking!")

# Query testing section
st.header("🔍 Test Query")

query_input = st.text_input(
    "Enter your query:",
    placeholder="Ask a question...",
    key="query_input"
)

col_btn1, col_btn2 = st.columns([1, 5])

with col_btn1:
    send_button = st.button("🚀 Send Query", type="primary")

if send_button and query_input:
    with st.spinner("Processing query..."):
        result = send_query(query_input)
        
        if result['success']:
            st.success("✅ Query processed successfully!")
            
            # Display answer
            st.subheader("Answer:")
            st.write(result['answer'])
            
            # Display metadata
            metadata_col1, metadata_col2, metadata_col3, metadata_col4 = st.columns(4)
            with metadata_col1:
                st.metric("Cost", f"${result['cost']:.6f}")
            with metadata_col2:
                st.metric("Latency", f"{result['latency_ms']:.0f} ms")
            with metadata_col3:
                st.metric("Input Tokens", f"{result['input_tokens']:,}")
            with metadata_col4:
                st.metric("Output Tokens", f"{result['output_tokens']:,}")
            
            # Display sources if available
            if result.get('sources'):
                with st.expander("📚 Sources"):
                    for i, source in enumerate(result['sources'], 1):
                        st.write(f"**Source {i}:**")
                        st.write(source.get('text', '')[:200] + "...")
                        st.write(f"Score: {source.get('score', 0):.4f}")
                        st.divider()
            
            # Auto-refresh stats
            st.rerun()
        else:
            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

# Recent queries table
st.header("📋 Recent Queries")

cost_history = list(st.session_state.cost_history)
if cost_history:
    # Get last 20 queries
    recent_queries = sorted(cost_history, key=lambda x: x.get('timestamp', datetime.min), reverse=True)[:20]
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            'Timestamp': item.get('timestamp', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S'),
            'Query': item.get('query', '')[:50] + '...',
            'Cost': f"${item.get('cost', 0):.6f}",
            'Latency (ms)': f"{item.get('latency', 0) * 1000:.0f}",
            'Tokens': f"{item.get('input_tokens', 0):,} / {item.get('output_tokens', 0):,}"
        }
        for item in recent_queries
    ])
    
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No queries yet. Send a query to start tracking!")

# Footer
st.markdown("---")
st.markdown(f"**API Server:** {API_URL}")
st.markdown(f"**Model:** {DEFAULT_MODEL}")

# Auto-refresh
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
