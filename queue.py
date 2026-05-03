from collections import defaultdict, deque
queues = defaultdict(deque)

def add(chat_id, item): queues[chat_id].append(item)
def pop(chat_id):
    if queues[chat_id]: return queues[chat_id].popleft()
    return None
def clear(chat_id): queues[chat_id].clear()
def peek(chat_id): return queues[chat_id][0] if queues[chat_id] else None
