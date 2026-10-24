import streamlit as st
import pandas as pd

# Import the refactored Process model
from models.llc_process import Process

# --- 1. Initialize Session State ---
# We use session state so the clocks and logs persist when Streamlit reruns
if 'processes' not in st.session_state:
    st.session_state.processes = {
        1: Process(1),
        2: Process(2),
        3: Process(3)
    }
    st.session_state.event_counter = 1
    st.session_state.message_counter = 1

processes = st.session_state.processes

# --- 2. App Title and Description ---
st.title("🕰️ Lamport's Logical Clocks Simulator")
st.markdown("""
This interactive simulation demonstrates Lamport's partial and total ordering. 
Trigger local events or send messages between processes to watch the logical clocks update dynamically.
""")

# --- 3. Interactive Controls ---
st.header("🎛️ Control Panel")

col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    st.subheader("Trigger Local Event (IR1)")
    target_p = st.selectbox("Select Process for Local Event", [1, 2, 3])
    if st.button(f"Execute Local Event on P{target_p}"):
        event_name = f"Event {st.session_state.event_counter}"
        processes[target_p].local_event(event_name)
        st.session_state.event_counter += 1
        st.rerun()

with col_ctrl2:
    st.subheader("Send Message (IR2a & IR2b)")
    sender = st.selectbox("Sender", [1, 2, 3], index=0)
    receiver = st.selectbox("Receiver", [1, 2, 3], index=1)
    
    if st.button("Send Network Message"):
        if sender == receiver:
            st.error("A process cannot send a message to itself in this simulation.")
        else:
            msg_name = f"Msg {st.session_state.message_counter}"
            
            # Sender executes IR2a and returns a Message object
            msg_object = processes[sender].send_message(processes[receiver], msg_name)
            
            # Receiver executes IR2b using the Message object
            processes[receiver].receive_message(sender, msg_object)
            
            st.session_state.message_counter += 1
            st.rerun()

st.divider()

# --- 4. Visualizing the Distributed System ---
st.header("🌐 System State (Local Clocks)")

cols = st.columns(3)

for i, col in enumerate(cols):
    pid = i + 1
    p = processes[pid]
    with col:
        st.markdown(f"### Process {pid}")
        st.metric(label="Current Logical Clock", value=p.clock)
        
        # Display Local Event Log
        if p.event_log:
            df = pd.DataFrame(p.event_log, columns=["Logical Time", "Action"])
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.write("*No events yet.*")

st.divider()

# --- 5. The Total Ordering ---
st.header("📜 Global Timeline (Total Ordering)")

all_events = []
for pid, p in processes.items():
    for time, action in p.event_log:
        all_events.append((time, pid, action))

if all_events:
    # Sort primarily by time (x[0]), and break ties by Process ID (x[1])
    all_events.sort(key=lambda x: (x[0], x[1]))
    
    # Format for display
    total_order_df = pd.DataFrame(all_events, columns=["Logical Time", "Process ID", "Action"])
    st.dataframe(total_order_df, hide_index=True, use_container_width=True)
else:
    st.info("Trigger an event above to generate the global timeline.")