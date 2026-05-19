"""File History Manager - tracks recently used files by category"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class HistoryManager:
    MAX_ENTRIES = 15
    CATEGORIES = ('data', 'grammar', 'tags')

    def __init__(self):
        config_dir = Path.home() / '.asn1viewer'
        config_dir.mkdir(exist_ok=True)
        self._path = config_dir / 'history.json'
        self._data: Dict[str, List[Dict]] = self._load()

    def _load(self) -> Dict[str, List[Dict]]:
        if self._path.exists():
            try:
                with open(self._path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {cat: [] for cat in self.CATEGORIES}

    def _save(self):
        try:
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def add(self, category: str, file_path: str):
        """Add or move a file to the front of the given category's history."""
        if category not in self.CATEGORIES:
            return
        if category not in self._data:
            self._data[category] = []
        lst = [e for e in self._data[category] if e['path'] != file_path]
        lst.insert(0, {
            'path': file_path,
            'name': Path(file_path).name,
            'accessed': datetime.now().isoformat(timespec='seconds'),
        })
        self._data[category] = lst[:self.MAX_ENTRIES]
        self._save()

    def get(self, category: str) -> List[Dict]:
        """Return list of history entries for a category (newest first)."""
        return list(self._data.get(category, []))

    def remove(self, category: str, file_path: str):
        """Remove a specific entry from history."""
        if category in self._data:
            self._data[category] = [
                e for e in self._data[category] if e['path'] != file_path
            ]
            self._save()

    def clear(self, category: Optional[str] = None):
        """Clear history for one category or all categories."""
        if category:
            self._data[category] = []
        else:
            self._data = {cat: [] for cat in self.CATEGORIES}
        self._save()
