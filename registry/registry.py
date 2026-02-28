import os
import csv
import re
from typing import Tuple


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
            return False, 'Email already registered.'

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
