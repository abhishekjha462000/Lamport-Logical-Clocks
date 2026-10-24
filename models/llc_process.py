from models.message import Message

class Process:
    def __init__(self, process_id):
        self.pid = process_id
        self.clock = 0
        self.event_log = []

    def local_event(self, event_name):
        self.clock += 1
        self.event_log.append((self.clock, event_name))
        print(f"Process {self.pid} executed local '{event_name}'. Clock -> {self.clock}")

    def send_message(self, receiver, message_content):
        self.clock += 1
        timestamp = self.clock
        self.event_log.append((self.clock, f"Send '{message_content}' to P{receiver.pid}"))
        print(f"Process {self.pid} sending '{message_content}' to P{receiver.pid}. Clock -> {self.clock}")
        
        # Uses 'EVENT' as the type, and passes the string into content
        return Message('EVENT', self.pid, timestamp, content=message_content)

    def receive_message(self, sender_pid, message):
        self.clock = max(self.clock, message.ts)
        self.clock += 1
        
        self.event_log.append((self.clock, f"Receive '{message.content}' from P{sender_pid}"))
        print(f"Process {self.pid} received '{message.content}' (Tm={message.ts}) from P{sender_pid}. Clock -> {self.clock}")