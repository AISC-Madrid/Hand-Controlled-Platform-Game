import os
import csv
import re
from typing import Tuple, List, Dict


class UserRegistry:
    def __init__(self, csv_path: str = os.path.join('registry', 'users.csv')):
        self.csv_path = csv_path
        self.users = []  # list of dicts {name, email}
        self.emails = set()
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._load()

    def _load(self):
        if not os.path.exists(self.csv_path):
            return
        try:
            with open(self.csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    name = (r.get('name') or '').strip()
                    email = (r.get('email') or '').strip().lower()
                    if email:
                        self.users.append({'name': name, 'email': email})
                        self.emails.add(email)
        except Exception:
            # If reading fails, start empty
            self.users = []
            self.emails = set()

    def _write_header_if_missing(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'email'])

    def validate_email(self, email: str) -> bool:
        if not email:
            return False
        email = email.strip()
        # Simple regex for basic validation
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        return re.match(pattern, email) is not None

    def exists(self, email: str) -> bool:
        if not email:
            return False
        return email.strip().lower() in self.emails

    def add_user(self, name: str, email: str) -> Tuple[bool, str]:
        name = (name or '').strip()
        email = (email or '').strip().lower()
        if not name:
            return False, 'Name is required.'
        if not email:
            return False, 'Email is required.'
        if not self.validate_email(email):
            return False, 'Invalid email format.'
        if self.exists(email):
            return True, 'Email already registered.'

        try:
            self._write_header_if_missing()
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([name, email])
            self.users.append({'name': name, 'email': email})
            self.emails.add(email)
            return True, 'User added.'
        except Exception as e:
            return False, f'Failed to save: {e}'

    def list_users(self):
        return list(self.users)


class Leaderboard:
    """Tracks the best (lowest) completion time per user (identified by email)."""

    def __init__(self, csv_path: str = os.path.join('registry', 'leaderboard.csv')):
        self.csv_path = csv_path
        # {email: {'name': str, 'best_time_ms': int}}
        self.entries: Dict[str, Dict] = {}
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._load()

    def _load(self):
        if not os.path.exists(self.csv_path):
            return
        try:
            with open(self.csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    email = (r.get('email') or '').strip().lower()
                    name = (r.get('name') or '').strip()
                    try:
                        best = int(r.get('best_time_ms', 0))
                    except (ValueError, TypeError):
                        continue
                    if email:
                        self.entries[email] = {'name': name, 'best_time_ms': best}
        except Exception:
            self.entries = {}

    def _save(self):
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['email', 'name', 'best_time_ms'])
                for email, data in self.entries.items():
                    writer.writerow([email, data['name'], data['best_time_ms']])
        except Exception:
            pass

    def record_time(self, email: str, name: str, time_ms: int):
        """Record a completion time. Keeps only the best (lowest) per email."""
        if not email:
            return
        email = email.strip().lower()
        existing = self.entries.get(email)
        if existing is None or time_ms < existing['best_time_ms']:
            self.entries[email] = {'name': name, 'best_time_ms': time_ms}
            self._save()

    def get_top(self, n: int = 5) -> List[Dict]:
        """Return the top-n entries sorted by best time (ascending)."""
        sorted_entries = sorted(self.entries.items(), key=lambda kv: kv[1]['best_time_ms'])
        result = []
        for i, (email, data) in enumerate(sorted_entries[:n]):
            result.append({
                'rank': i + 1,
                'name': data['name'],
                'best_time_ms': data['best_time_ms'],
            })
        return result
