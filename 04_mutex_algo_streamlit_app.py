import streamlit as st
import pandas as pd

from models.mutex_process import Process
from services.network import Network
from models.message import Message

st.set_page_config(page_title="Lamport Mutex Simulator", layout="wide")

# --- 1. Dynamic Network Initialization (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Network Setup")
    st.write("Set the number of processes in the network.")
    num_procs = st.number_input("Total Processes", min_value=2, max_value=6, value=3)
    
    if st.button("Initialize / Reset Network", type="primary") or 'processes' not in st.session_state:
        st.session_state.net = Network()
        st.session_state.processes = {i: Process(i, num_procs) for i in range(1, num_procs + 1)}
        for p in st.session_state.processes.values():
            st.session_state.net.register(p)
        st.rerun()

def check_all_grants():
    """Forces all processes to run their Rule 5 safety check."""
    for p in st.session_state.processes.values():
        p.check_granted()

# Convenience variables
processes = list(st.session_state.processes.values())
pids = list(st.session_state.processes.keys())
current_holder = next((p for p in processes if p.has_resource), None)

# --- 2. App Title ---
st.title("🔐 Dynamic Distributed Mutual Exclusion")
st.markdown("Execute standard events, route messages, or trigger custom resource collisions across a dynamic network.")

# --- 3. Master Control Panel ---
st.header("🎛️ Control Panel")
col1, col2, col3 = st.columns(3)

# Panel 1: Standard Logical Clock Events
with col1:
    st.subheader("1. Standard Events")
    
    # Local Event
    ev_pid = st.selectbox("Execute Local Event on:", pids, key="ev_pid")
    if st.button("Trigger Local Event"):
        st.session_state.processes[ev_pid].clock += 1
        check_all_grants()
        st.rerun()
        
    st.divider()
    
    # Network Message
    st.write("**Send Network Message**")
    sender_pid = st.selectbox("Sender:", pids, key="sender")
    receiver_pid = st.selectbox("Receiver:", [p for p in pids if p != sender_pid], key="receiver")
    
    if st.button("Send Message"):
        sender = st.session_state.processes[sender_pid]
        receiver = st.session_state.processes[receiver_pid]
        sender.clock += 1
        msg = Message('EVENT', sender.pid, sender.clock, content="Standard Msg")
        st.session_state.net.send(sender.pid, receiver.pid, msg)
        check_all_grants()
        st.rerun()

# Panel 2: Mutex Operations & Collisions
with col2:
    st.subheader("2. Resource Requests")
    
    req_pid = st.selectbox("Request Resource for:", pids, key="req_pid")
    already_requested = any(req[1] == req_pid for req in st.session_state.processes[req_pid].queue)
    
    if st.button(f"P{req_pid}: Request Resource", disabled=already_requested):
        st.session_state.processes[req_pid].request_resource()
        check_all_grants()
        st.rerun()
        
    st.divider()
    
    st.write("**Custom Collision Simulator**")
    c1, c2 = st.columns(2)
    with c1:
        col_a = st.selectbox("Process A:", pids, index=0, key="col_a")
    with c2:
        col_b = st.selectbox("Process B:", pids, index=1 if len(pids)>1 else 0, key="col_b")
        
    if st.button("Simulate Concurrent Request"):
        if col_a != col_b:
            pa = st.session_state.processes[col_a]
            pb = st.session_state.processes[col_b]
            
            # Temporarily disconnect to sync timestamps
            pa.network = None
            pb.network = None
            
            pa.request_resource()
            pb.request_resource()
            
            # Reconnect and broadcast simultaneously
            pa.network = st.session_state.net
            pb.network = st.session_state.net
            
            msg_a = Message('REQUEST', pa.pid, pa.clock)
            msg_b = Message('REQUEST', pb.pid, pb.clock)
            
            st.session_state.net.broadcast(pa.pid, msg_a)
            st.session_state.net.broadcast(pb.pid, msg_b)
            
            check_all_grants()
            st.rerun()
        else:
            st.error("Select two different processes!")

# Panel 3: Resource Holding & Release
with col3:
    st.subheader("3. Resource Status")
    if current_holder:
        st.success(f"🎉 Process {current_holder.pid} holds the resource!")
        if st.button(f"P{current_holder.pid}: Release Resource", type="primary"):
            current_holder.release_resource()
            check_all_grants()
            st.rerun()
    else:
        st.info("The resource is currently free.")

st.divider()

# --- 4. Live System State (Dynamic Columns) ---
st.header("🌐 Live Process Memory")

# Dynamically wrap columns (max 3 or 4 per row depending on network size)
max_cols = 4 if len(processes) > 3 else 3
ui_columns = st.columns(min(len(processes), max_cols))

for i, p in enumerate(processes):
    col = ui_columns[i % max_cols]
    with col:
        st.markdown(f"### Process {p.pid}")
        
        if p.has_resource:
            st.success("Holding Resource 🟢")
        else:
            st.warning("Waiting / Idle 🟡")
            
        st.metric(label="Logical Clock", value=p.clock)
        
        st.markdown("**Local Priority Queue**")
        if p.queue:
            sorted_queue = sorted(p.queue, key=lambda x: (x[0], x[1]))
            df_q = pd.DataFrame(sorted_queue, columns=["Timestamp", "Process ID"])
            st.dataframe(
                df_q.style.apply(lambda x: ['background: #1e3a8a' if x.name == 0 else '' for i in x], axis=1), 
                hide_index=True, 
                use_container_width=True
            )
        else:
            st.write("*Queue is empty*")
            
        st.markdown("**Received Network Messages**")
        df_acks = pd.DataFrame(list(p.last_msg_timestamp.items()), columns=["From P_ID", "Latest Timestamp"])
        st.dataframe(df_acks, hide_index=True, use_container_width=True)