import heapq

class Network:
    def __init__(self):
        self.processes = {}

    def register(self, process):
        self.processes[process.pid] = process
        process.network = self

    def broadcast(self, sender_pid, msg):
        for pid, process in self.processes.items():
            if pid != sender_pid:
                process.receive(msg)

    def send(self, sender_pid, receiver_pid, msg):
        self.processes[receiver_pid].receive(msg)

class Process:
    def __init__(self, pid, total_processes):
        self.pid = pid
        self.clock = 0
        # Priority queue to store requests. Format: (timestamp, process_id)
        self.queue = []  
        # Track the latest timestamp received from every other process
        self.last_msg_timestamp = {i: 0 for i in range(1, total_processes + 1) if i != pid}
        self.network = None
        self.has_resource = False

    def request_resource(self):
        """Rule 1: Send a REQUEST message to all processes and put it in own queue."""
        self.clock += 1
        msg = {'type': 'REQUEST', 'sender': self.pid, 'ts': self.clock}
        print(f"[Time {self.clock}] P{self.pid} BROADCASTS REQUEST")
        heapq.heappush(self.queue, (msg['ts'], self.pid))
        self.network.broadcast(self.pid, msg)

    def release_resource(self):
        """Rule 3: Remove own request and send a RELEASE message to all processes."""
        self.clock += 1
        print(f"[Time {self.clock}] P{self.pid} RELEASES the resource and BROADCASTS RELEASE")
        self.queue = [req for req in self.queue if req[1] != self.pid]
        heapq.heapify(self.queue)
        self.has_resource = False
        msg = {'type': 'RELEASE', 'sender': self.pid, 'ts': self.clock}
        self.network.broadcast(self.pid, msg)

    def receive(self, msg):
        """Handles incoming messages and updates the logical clock."""
        self.clock = max(self.clock, msg['ts']) + 1
        sender = msg['sender']
        self.last_msg_timestamp[sender] = self.clock

        if msg['type'] == 'REQUEST':
            # Rule 2: Place request on queue and send an ACK
            heapq.heappush(self.queue, (msg['ts'], sender))
            self.clock += 1
            ack_msg = {'type': 'ACK', 'sender': self.pid, 'ts': self.clock}
            self.network.send(self.pid, sender, ack_msg)
            
        elif msg['type'] == 'RELEASE':
            # Rule 4: Remove the released request from the queue
            self.queue = [req for req in self.queue if req[1] != sender]
            heapq.heapify(self.queue)

    def check_granted(self):
        """Rule 5: Check if the resource can be granted."""
        if not self.queue or self.has_resource:
            return

        # Condition (i): Is this process's request at the very top of the queue?
        # Condition (ii): Has this process received a message from EVERY other process with a timestamp > its request?
        top_ts, top_pid = self.queue[0]
        
        if top_pid == self.pid:
            if all(ts > top_ts for ts in self.last_msg_timestamp.values()):
                self.has_resource = True
                print(f"*** P{self.pid} is GRANTED the resource at Time {self.clock} ***")

# --- Simulation Setup ---
net = Network()
p1 = Process(1, 3)
p2 = Process(2, 3)
p3 = Process(3, 3)

for p in [p1, p2, p3]:
    net.register(p)

print("--- Step 1: P1 and P2 request the resource concurrently ---")
p1.request_resource()
p2.request_resource()

print("\n--- Step 2: Processes check if they are granted the resource ---")
p1.check_granted()
p2.check_granted()
p3.check_granted()

print("\n--- Step 3: P1 finishes and releases the resource ---")
p1.release_resource()

print("\n--- Step 4: P2 checks if it is granted the resource ---")
p2.check_granted()
