import heapq
from models.message import Message

class Process:
    def __init__(self, pid, total_processes):
        self.pid = pid
        self.clock = 0
        self.queue = []  
        self.last_msg_timestamp = {i: 0 for i in range(1, total_processes + 1) if i != pid}
        self.network = None
        self.has_resource = False

    def request_resource(self):
        self.clock += 1
        msg = Message('REQUEST', self.pid, self.clock)
        print(f"[Time {self.clock}] P{self.pid} BROADCASTS REQUEST")
        heapq.heappush(self.queue, (msg.ts, self.pid))
        if self.network:
            self.network.broadcast(self.pid, msg)

    def release_resource(self):
        self.clock += 1
        print(f"[Time {self.clock}] P{self.pid} RELEASES the resource and BROADCASTS RELEASE")
        self.queue = [req for req in self.queue if req[1] != self.pid]
        heapq.heapify(self.queue)
        self.has_resource = False
        msg = Message('RELEASE', self.pid, self.clock)
        if self.network:
            self.network.broadcast(self.pid, msg)

    def receive(self, msg):
        self.clock = max(self.clock, msg.ts) + 1
        sender = msg.sender
        self.last_msg_timestamp[sender] = msg.ts

        if msg.type == 'REQUEST':
            heapq.heappush(self.queue, (msg.ts, sender))
            self.clock += 1
            ack_msg = Message('ACK', self.pid, self.clock)
            if self.network:
                self.network.send(self.pid, sender, ack_msg)
            
        elif msg.type == 'RELEASE':
            self.queue = [req for req in self.queue if req[1] != sender]
            heapq.heapify(self.queue)

    def check_granted(self):
        if not self.queue or self.has_resource:
            return

        top_ts, top_pid = self.queue[0]
        
        if top_pid == self.pid:
            if all(ts > top_ts for ts in self.last_msg_timestamp.values()):
                self.has_resource = True
                print(f"*** P{self.pid} is GRANTED the resource at Time {self.clock} ***")