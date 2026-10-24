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