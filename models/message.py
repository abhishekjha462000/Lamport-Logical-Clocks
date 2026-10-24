class Message:
    def __init__(self, msg_type, sender, ts, content=None):
        self.type = msg_type
        self.sender = sender
        self.ts = ts
        self.content = content

    def __repr__(self):
        if self.content:
            return f"Message('{self.content}', ts={self.ts})"
        return f"Message({self.type}, sender={self.sender}, ts={self.ts})"