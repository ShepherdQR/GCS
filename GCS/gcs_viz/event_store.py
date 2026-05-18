import json
import os
import time
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class GCSEvent:
    event_type: str
    timestamp: float
    payload: dict

    def to_dict(self) -> dict:
        return {"event_type": self.event_type, "timestamp": self.timestamp, "payload": self.payload}

    @classmethod
    def from_dict(cls, d: dict) -> "GCSEvent":
        return cls(event_type=d["event_type"], timestamp=d["timestamp"], payload=d["payload"])


class EventStore:
    def __init__(self, store_dir: str = None):
        if store_dir is None:
            store_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".events")
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)

    def _event_file(self, scene_id: str) -> str:
        return os.path.join(self.store_dir, f"{scene_id}.jsonl")

    def append(self, scene_id: str, event_type: str, payload: dict):
        event = GCSEvent(event_type=event_type, timestamp=time.time(), payload=payload)
        path = self._event_file(scene_id)
        with open(path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def replay(self, scene_id: str) -> List[GCSEvent]:
        path = self._event_file(scene_id)
        if not os.path.exists(path):
            return []
        events = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(GCSEvent.from_dict(json.loads(line)))
        return events

    def get_state_at(self, scene_id: str, event_index: int) -> dict:
        events = self.replay(scene_id)
        if event_index >= len(events):
            event_index = len(events) - 1
        state = {"rigid_sets": [], "geometries": [], "constraints": []}
        for i in range(event_index + 1):
            evt = events[i]
            p = evt.payload
            if evt.event_type == "GraphLoaded":
                state = p.get("graph", state)
            elif evt.event_type == "RigidSetAdded":
                state["rigid_sets"].append(p)
            elif evt.event_type == "GeometryAdded":
                state["geometries"].append(p)
            elif evt.event_type == "ConstraintAdded":
                state["constraints"].append(p)
            elif evt.event_type == "RigidSetRemoved":
                state["rigid_sets"] = [rs for rs in state["rigid_sets"] if rs.get("id") != p.get("id")]
            elif evt.event_type == "GeometryRemoved":
                state["geometries"] = [g for g in state["geometries"] if g.get("id") != p.get("id")]
            elif evt.event_type == "ConstraintRemoved":
                state["constraints"] = [c for c in state["constraints"] if c.get("id") != p.get("id")]
            elif evt.event_type == "GeometryUpdated":
                for g in state["geometries"]:
                    if g.get("id") == p.get("id"):
                        g.update(p)
            elif evt.event_type == "ConstraintUpdated":
                for c in state["constraints"]:
                    if c.get("id") == p.get("id"):
                        c.update(p)
        return state

    def list_scenes(self) -> List[str]:
        scenes = []
        if os.path.exists(self.store_dir):
            for fname in os.listdir(self.store_dir):
                if fname.endswith(".jsonl"):
                    scenes.append(fname[:-6])
        return sorted(scenes)
