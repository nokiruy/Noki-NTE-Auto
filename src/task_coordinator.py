"""Cross-task mutual exclusion for long-running automation jobs."""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable, Optional


@dataclass(frozen=True)
class TaskLease:
    """A unique claim on the single automation execution slot."""

    token: int
    name: str


class TaskCoordinator:
    """Allow only one automation task to own input/ADB resources at a time."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._next_token = 1
        self._active: Optional[TaskLease] = None
        self._listener: Optional[Callable[[Optional[str]], None]] = None

    def set_listener(self, listener: Optional[Callable[[Optional[str]], None]]) -> None:
        with self._lock:
            self._listener = listener
            active_name = self._active.name if self._active else None
        self._notify(listener, active_name)

    def acquire(self, name: str) -> Optional[TaskLease]:
        with self._lock:
            if self._active is not None:
                return None
            lease = TaskLease(self._next_token, name)
            self._next_token += 1
            self._active = lease
            listener = self._listener
        self._notify(listener, name)
        return lease

    def release(self, lease: Optional[TaskLease]) -> bool:
        if lease is None:
            return False
        with self._lock:
            if self._active is None or self._active.token != lease.token:
                return False
            self._active = None
            listener = self._listener
        self._notify(listener, None)
        return True

    @property
    def active_name(self) -> Optional[str]:
        with self._lock:
            return self._active.name if self._active else None

    @staticmethod
    def _notify(
        listener: Optional[Callable[[Optional[str]], None]],
        active_name: Optional[str],
    ) -> None:
        if listener is None:
            return
        try:
            listener(active_name)
        except Exception:
            # Presentation errors must never hold the execution lock forever.
            pass
