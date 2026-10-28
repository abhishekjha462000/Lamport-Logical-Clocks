import streamlit as st
import pandas as pd

from models.mutex_process import Process
from services.network import Network

# --- 1. Initialize Session State ---
if 'net' not in st.session_state:
    st.session_state.net = Network()
    st.session_state.p1 = Process(1, 3)
    st.session_state.p2 = Process(2, 3)
    st.session_state.p3 = Process(3, 3)
    
    for p in [st.session_state.p1, st.session_state.p2, st.session_state.p3]:
        st.session_state.net.register(p)

processes = [st.session_state.p1, st.session_state.p2, st.session_state.p3]

def check_all_grants():
    """Forces all processes to run their Rule 5 safety check."""
    for p in processes:
        p.check_granted()

# --- 2. App Title & Layout ---
st.title("🔐 Distributed Mutual Exclusion Simulator")
st.markdown("""
Watch Lamport's 5 rules in action. When a process requests the resource, it broadcasts the request, 
updates everyone's priority queues, and collects acknowledgments. The resource is only granted when a 
process is at the top of its own queue and has received ACKs from everyone.
""")

# --- 3. Control Panel ---
st.header("🎛️ Control Panel")

# Find if anyone currently holds the resource
current_holder = next((p for p in processes if p.has_resource), None)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("P1 Request Resource", disabled=any(req[1] == 1 for req in st.session_state.p1.queue)):
        st.session_state.p1.request_resource()
        check_all_grants()
        st.rerun()

with col2:
    if st.button("P2 Request Resource", disabled=any(req[1] == 2 for req in st.session_state.p2.queue)):
        st.session_state.p2.request_resource()
        check_all_grants()
        st.rerun()

with col3:
    if st.button("P3 Request Resource", disabled=any(req[1] == 3 for req in st.session_state.p3.queue)):
        st.session_state.p3.request_resource()
        check_all_grants()
        st.rerun()

st.divider()

# Release Controls
st.subheader("Resource Status")
if current_holder:
    st.success(f"🎉 Process {current_holder.pid} currently holds the resource!")
    if st.button(f"Process {current_holder.pid}: Release Resource"):
        current_holder.release_resource()
        check_all_grants()
        st.rerun()
else:
    st.info("The resource is currently free.")

# ==========================================
# --- NEW COLLISION CODE INSERTED HERE ---
# ==========================================
st.divider()
st.subheader("💥 Collision Demonstration (Tie-Breaker)")

if st.button("Simulate Concurrent Request (P1 & P2)", type="primary"):
    # 1. Temporarily disconnect the network to prevent instant clock updates
    st.session_state.p1.network = None
    st.session_state.p2.network = None
    
    # 2. Both processes request at the exact same logical time
    st.session_state.p1.request_resource()
    st.session_state.p2.request_resource()
    
    # 3. Reconnect the network
    st.session_state.p1.network = st.session_state.net
    st.session_state.p2.network = st.session_state.net
    
    # 4. Broadcast the frozen requests to the rest of the network
    msg1 = Message('REQUEST', 1, st.session_state.p1.clock)
    msg2 = Message('REQUEST', 2, st.session_state.p2.clock)
    
    st.session_state.net.broadcast(1, msg1)
    st.session_state.net.broadcast(2, msg2)
    
    check_all_grants()
    st.rerun()
# ==========================================

st.divider()

# --- 4. Live System State ---
st.header("🌐 Live Process Memory")

cols = st.columns(3)

for i, col in enumerate(cols):
    p = processes[i]
    with col:
        st.markdown(f"### Process {p.pid}")
        
        # Status Badge
        if p.has_resource:
            st.success("Holding Resource 🟢")
        else:
            st.warning("Waiting / Idle 🟡")
            
        st.metric(label="Logical Clock", value=p.clock)
        
        # Priority Queue Visualization
        st.markdown("**Local Priority Queue**")
        if p.queue:
            # Sort the heap to show accurate top-to-bottom priority
            sorted_queue = sorted(p.queue, key=lambda x: (x[0], x[1]))
            df_q = pd.DataFrame(sorted_queue, columns=["Timestamp", "Process ID"])
            
            # Highlight the top of the queue
            st.dataframe(
                df_q.style.apply(lambda x: ['background: #1e3a8a' if x.name == 0 else '' for i in x], axis=1), 
                hide_index=True, 
                use_container_width=True
            )
        else:
            st.write("*Queue is empty*")
            
        # ACK Tracker Visualization (Last Msg Timestamp)
        st.markdown("**Received ACKs (Rule 5 Tracker)**")
        df_acks = pd.DataFrame(list(p.last_msg_timestamp.items()), columns=["From P_ID", "Latest Time"])
        st.dataframe(df_acks, hide_index=True, use_container_width=True)