from collections import defaultdict, deque

QUEUE: dict[int, deque] = defaultdict(deque)

def add(chat_id, item):
    QUEUE[chat_id].append(item)
    return len(QUEUE[chat_id])

def pop(chat_id):
    if QUEUE[chat_id]:
        return QUEUE[chat_id].popleft()
    return None

def peek(chat_id):
    return QUEUE[chat_id][0] if QUEUE[chat_id] else None

def clear(chat_id):
    QUEUE[chat_id].clear()

def size(chat_id):
    return len(QUEUE[chat_id])

def list_items(chat_id):
    return list(QUEUE[chat_id])
