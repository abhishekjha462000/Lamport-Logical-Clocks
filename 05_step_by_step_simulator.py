import streamlit as st
import pandas as pd
from models.mutex_process import Process
from models.message import Message

st.set_page_config(page_title="Step-by-Step Mutex Debugger", layout="wide")

# --- Custom Queued Network Wrapper ---
class QueuedNetwork:
    def __init__(self):
        self.peers = {}

    def register(self, process):
        self.peers[process.pid] = process

    def send(self, sender_id, receiver_id, msg):
        # Instead of delivering instantly, add to the global queue
        st.session_state.message_queue.append({
            "from": sender_id,
            "to": receiver_id,
            "msg": msg
        })

    def broadcast(self, sender_id, msg):
        for pid in self.peers:
            if pid != sender_id:
                self.send(sender_id, pid, msg)

# --- Initialize Session State ---
if 'step_net' not in st.session_state:
    st.session_state.step_net = QueuedNetwork()
    st.session_state.processes = {i: Process(i, 3) for i in range(1, 4)}
    st.session_state.message_queue = []
    st.session_state.audit_log = []
    
    for p in st.session_state.processes.values():
        p.network = st.session_state.step_net
        st.session_state.step_net.register(p)

processes = list(st.session_state.processes.values())

def check_all_grants():
    for p in processes:
        p.check_granted()

# --- App Layout ---
st.title("🔍 Step-by-Step Algorithm Debugger")
st.markdown("Generate requests, then deliver messages one by one to watch the mathematical state evolve.")

# --- 1. Generation Controls ---
st.header("1. Generate Events (Adds to Queue)")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("P1: Request Resource", disabled=any(req[1] == 1 for req in st.session_state.processes[1].queue)):
        st.session_state.processes[1].request_resource()
        st.session_state.audit_log.insert(0, f"🕒 P1 generated REQUEST at local time {st.session_state.processes[1].clock}")
        st.rerun()
with c2:
    if st.button("P2: Request Resource", disabled=any(req[1] == 2 for req in st.session_state.processes[2].queue)):
        st.session_state.processes[2].request_resource()
        st.session_state.audit_log.insert(0, f"🕒 P2 generated REQUEST at local time {st.session_state.processes[2].clock}")
        st.rerun()
with c3:
    if st.button("P3: Request Resource", disabled=any(req[1] == 3 for req in st.session_state.processes[3].queue)):
        st.session_state.processes[3].request_resource()
        st.session_state.audit_log.insert(0, f"🕒 P3 generated REQUEST at local time {st.session_state.processes[3].clock}")
        st.rerun()

st.divider()

# --- 2. Execution Queue ---
st.header("2. Message Queue Execution")
col_queue, col_log = st.columns([1, 1])

with col_queue:
    st.subheader("Pending Network Messages")
    if st.session_state.message_queue:
        df_queue = pd.DataFrame([{
            "Sender": m["from"], 
            "Receiver": m["to"], 
            "Type": m["msg"].type, 
            "Timestamp": m["msg"].ts
        } for m in st.session_state.message_queue])
        st.dataframe(df_queue, hide_index=True, use_container_width=True)
        
        if st.button("🚀 Deliver Next Message (Pop Top)", type="primary"):
            # Pop the first message and deliver it
            delivery = st.session_state.message_queue.pop(0)
            target_pid = delivery["to"]
            msg = delivery["msg"]
            
            target_process = st.session_state.processes[target_pid]
            old_clock = target_process.clock
            target_process.receive(msg)
            
            log_entry = f"📥 Delivered {msg.type}(T={msg.ts}) from P{delivery['from']} to P{target_pid}. P{target_pid} clock updated: max({old_clock}, {msg.ts}) + 1 = {target_process.clock}."
            st.session_state.audit_log.insert(0, log_entry)
            
            check_all_grants()
            st.rerun()
    else:
        st.info("The network is idle. No pending messages.")

with col_log:
    st.subheader("Audit Log")
    if st.session_state.audit_log:
        st.dataframe(pd.DataFrame({"Event History": st.session_state.audit_log}), hide_index=True, use_container_width=True)

st.divider()

# --- 3. Live System State ---
st.header("3. Process Memory States")
state_cols = st.columns(3)

for i, col in enumerate(state_cols):
    p = processes[i]
    with col:
        st.markdown(f"### Process {p.pid}")
        if p.has_resource:
            st.success("Holding Resource 🟢")
            if st.button(f"Release Resource", key=f"rel_{p.pid}"):
                p.release_resource()
                st.session_state.audit_log.insert(0, f"🔓 P{p.pid} released the resource.")
                st.rerun()
        else:
            st.warning("Waiting / Idle 🟡")
            
        st.metric(label="Logical Clock", value=p.clock)
        
        st.markdown("**Local Priority Queue**")
        if p.queue:
            sorted_queue = sorted(p.queue, key=lambda x: (x[0], x[1]))
            df_q = pd.DataFrame(sorted_queue, columns=["Timestamp", "Process ID"])
            st.dataframe(df_q.style.apply(lambda x: ['background: #1e3a8a' if x.name == 0 else '' for i in x], axis=1), hide_index=True, use_container_width=True)
        else:
            st.write("*Queue is empty*")
            
        st.markdown("**Acknowledgment Tracker**")
        df_acks = pd.DataFrame(list(p.last_msg_timestamp.items()), columns=["From P_ID", "Latest Timestamp"])
        st.dataframe(df_acks, hide_index=True, use_container_width=True)