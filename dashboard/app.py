import os
import socket
import threading
import time
from collections import deque
from urllib.parse import urlparse

import httpx
import pandas as pd
import streamlit as st


API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_API_KEY = os.getenv("API_KEY", "demo-key")


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _should_start_embedded_api() -> bool:
    parsed_api = urlparse(API_BASE)
    is_local_api = parsed_api.hostname in {"localhost", "127.0.0.1"}
    is_azure_web_app = bool(os.getenv("WEBSITE_SITE_NAME"))
    explicit_enabled = os.getenv("ENABLE_EMBEDDED_API", "").lower() == "true"
    return is_local_api and (is_azure_web_app or explicit_enabled)


def _start_embedded_api() -> None:
    if not _should_start_embedded_api() or _is_port_open("127.0.0.1", 8000):
        return

    def run_api() -> None:
        import uvicorn

        uvicorn.run(
            "api.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )

    thread = threading.Thread(target=run_api, daemon=True)
    thread.start()


_start_embedded_api()


st.set_page_config(
    page_title="DevOps Monitor",
    page_icon="📊",
    layout="wide",
)


if "metrics_history" not in st.session_state:
    st.session_state.metrics_history = deque(maxlen=60)

if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY


@st.cache_data(ttl=2)
def fetch_metrics() -> dict:
    response = httpx.get(f"{API_BASE}/metrics", timeout=5.0)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=5)
def fetch_servers(status: str | None = None) -> list[dict]:
    params = {"status": status} if status and status != "All" else None
    response = httpx.get(f"{API_BASE}/servers", params=params, timeout=5.0)
    response.raise_for_status()
    return response.json()


def colour_status(row):
    if row["status"] == "UP":
        return ["background-color: #d4edda"] * len(row)
    if row["status"] == "DEGRADED":
        return ["background-color: #fff3cd"] * len(row)
    if row["status"] == "DOWN":
        return ["background-color: #f8d7da"] * len(row)
    return ["background-color: #e2e3e5"] * len(row)


def clear_api_cache() -> None:
    fetch_metrics.clear()
    fetch_servers.clear()


st.sidebar.title("Settings")
st.session_state.api_key = st.sidebar.text_input(
    "API Key",
    value=st.session_state.api_key,
    type="password",
)
refresh_seconds = st.sidebar.slider(
    "Auto-refresh seconds",
    min_value=1,
    max_value=10,
    value=2,
)
auto_refresh = st.sidebar.toggle("Auto-refresh", value=True)

if st.sidebar.button("Refresh now"):
    clear_api_cache()
    st.rerun()


st.title("DevOps Monitoring Dashboard")
st.caption("FastAPI backend + Streamlit frontend")

tab_metrics, tab_servers = st.tabs(["Metrics", "Servers"])


with tab_metrics:
    st.subheader("Live System Metrics")

    try:
        metrics = fetch_metrics()
    except httpx.HTTPError as error:
        st.error(f"Could not fetch metrics: {error}")
    else:
        cpu = metrics["cpu_percent"]
        memory = metrics["memory_percent"]
        disk = metrics["disk_percent"]

        col_cpu, col_memory, col_disk = st.columns(3)
        col_cpu.metric("CPU", f"{cpu:.1f}%")
        col_memory.metric(
            "Memory",
            f"{memory:.1f}%",
            f"{metrics['memory_used_gb']} / {metrics['memory_total_gb']} GB",
        )
        col_disk.metric("Disk", f"{disk:.1f}%")

        st.session_state.metrics_history.append(
            {
                "time": time.strftime("%H:%M:%S"),
                "cpu_percent": cpu,
                "memory_percent": memory,
            }
        )

        history_df = pd.DataFrame(st.session_state.metrics_history)
        if not history_df.empty:
            chart_df = history_df.set_index("time")
            st.line_chart(chart_df, height=260)


with tab_servers:
    st.subheader("Monitored Servers")

    status_filter = st.selectbox(
        "Filter by status",
        ["All", "unknown", "UP", "DEGRADED", "DOWN"],
    )

    try:
        servers = fetch_servers(status_filter)
    except httpx.HTTPError as error:
        st.error(f"Could not fetch servers: {error}")
        servers = []

    if servers:
        server_df = pd.DataFrame(servers)
        st.dataframe(
            server_df.style.apply(colour_status, axis=1),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No servers registered yet.")

    st.divider()
    st.subheader("Register Server")

    with st.form("register_server", clear_on_submit=True):
        name = st.text_input("Name", placeholder="api-prod")
        host = st.text_input("Host", placeholder="127.0.0.1")
        port = st.number_input(
            "Port",
            min_value=1,
            max_value=65535,
            value=8000,
        )
        submitted = st.form_submit_button("Register")

    if submitted:
        if not name or not host:
            st.error("Name and host are required.")
        else:
            try:
                response = httpx.post(
                    f"{API_BASE}/servers",
                    json={"name": name, "host": host, "port": port},
                    headers={"X-API-Key": st.session_state.api_key},
                    timeout=5.0,
                )
                response.raise_for_status()
                clear_api_cache()
                st.success(f"Registered {name}.")
                st.rerun()
            except httpx.HTTPStatusError as error:
                st.error(
                    f"API returned {error.response.status_code}: "
                    f"{error.response.text}"
                )
            except httpx.HTTPError as error:
                st.error(f"Could not register server: {error}")

    if servers:
        st.divider()
        st.subheader("Immediate Health Check")
        server_options = {
            server["id"]: (
                f"{server['name']} ({server['host']}:{server['port']})"
            )
            for server in servers
        }
        selected_id = st.selectbox(
            "Server",
            list(server_options.keys()),
            format_func=lambda server_id: server_options[server_id],
        )

        if st.button("Run health check"):
            try:
                response = httpx.post(
                    f"{API_BASE}/servers/{selected_id}/check",
                    timeout=5.0,
                )
                response.raise_for_status()
                clear_api_cache()
                st.success(
                    f"Health check completed: {response.json()['status']}"
                )
                st.rerun()
            except httpx.HTTPError as error:
                st.error(f"Could not run health check: {error}")


refresh_placeholder = st.empty()
with refresh_placeholder.container():
    if auto_refresh:
        st.caption(f"Auto-refresh enabled every {refresh_seconds}s")
    else:
        st.caption("Auto-refresh paused")

if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
