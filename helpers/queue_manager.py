from typing import Optional

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎵 THRINO MUSIC BOT — Queue Manager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class QueueManager:
    def __init__(self):
        self._queues: dict[int, list] = {}          # chat_id → list of tracks
        self._current: dict[int, dict] = {}         # chat_id → current track
        self._search_cache: dict[int, list] = {}    # user_id → search results

    # ── Playback State ─────────────────────────────

    def is_active(self, chat_id: int) -> bool:
        return chat_id in self._current and self._current[chat_id] is not None

    def set_active(self, chat_id: int, track: dict):
        self._current[chat_id] = track

    def get_current(self, chat_id: int) -> Optional[dict]:
        return self._current.get(chat_id)

    # ── Queue Operations ───────────────────────────

    def add(self, chat_id: int, track: dict):
        if chat_id not in self._queues:
            self._queues[chat_id] = []
        self._queues[chat_id].append(track)

    def next(self, chat_id: int) -> Optional[dict]:
        q = self._queues.get(chat_id, [])
        if q:
            track = q.pop(0)
            self._current[chat_id] = track
            return track
        self._current.pop(chat_id, None)
        return None

    def get_queue(self, chat_id: int) -> list:
        return self._queues.get(chat_id, [])

    def length(self, chat_id: int) -> int:
        return len(self._queues.get(chat_id, []))

    def clear(self, chat_id: int):
        self._queues.pop(chat_id, None)
        self._current.pop(chat_id, None)

    # ── Search Cache ───────────────────────────────

    def set_search_cache(self, user_id: int, results: list):
        self._search_cache[user_id] = results

    def get_search_cache(self, user_id: int) -> Optional[list]:
        return self._search_cache.get(user_id)
