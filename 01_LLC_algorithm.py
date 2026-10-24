from models.llc_process import Process

print("--- System Start ---")

p1 = Process(1)
p2 = Process(2)
p3 = Process(3)

# P1 performs local event
p1.local_event("Event A")

# P1 sends message to P2 (Returns a Message object now)
msg_1 = p1.send_message(p2, "Message 1")

# P2 performs independent local event
p2.local_event("Event B")

# P2 receives the Message object from P1
p2.receive_message(p1.pid, msg_1)

# P3 performs local event
p3.local_event("Event C")

# P2 sends message to P3
msg_2 = p2.send_message(p3, "Message 2")

# P3 receives the Message object from P2
p3.receive_message(p2.pid, msg_2)

print("\n--- Final Event Logs (Total Ordering by Timestamp) ---")
all_events = []
for p in [p1, p2, p3]:
    for time, action in p.event_log:
        all_events.append((time, p.pid, action))

all_events.sort(key=lambda x: (x[0], x[1]))

for time, pid, action in all_events:
    print(f"Time {time} | Process {pid} | {action}")