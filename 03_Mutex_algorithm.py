from models.mutex_process import Process
from services.network import Network

print("--- Simulation Setup ---")
net = Network()
p1 = Process(1, 3)
p2 = Process(2, 3)
p3 = Process(3, 3)

for p in [p1, p2, p3]:
    net.register(p)

print("\n--- Step 1: P1 and P2 request the resource concurrently ---")
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