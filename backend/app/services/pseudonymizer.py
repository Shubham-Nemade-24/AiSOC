"""Pseudonymization Module — masks sensitive data before sending to LLM APIs.

Replaces internal IPs, hostnames, usernames, email addresses, and file paths
with reversible opaque tokens. This ensures data sovereignty and privacy
compliance when using external LLM providers.
"""
import re
import uuid
from typing import Optional


class Pseudonymizer:
    """Bidirectional pseudonymization engine with reversible token mapping."""

    def __init__(self):
        self._forward: dict[str, str] = {}   # real -> token
        self._reverse: dict[str, str] = {}   # token -> real
        self._counters = {"IP": 0, "HOST": 0, "USER": 0, "EMAIL": 0, "PATH": 0}

    def _get_token(self, category: str, real_value: str) -> str:
        if real_value in self._forward:
            return self._forward[real_value]
        self._counters[category] += 1
        token = f"[{category}_{self._counters[category]:03d}]"
        self._forward[real_value] = token
        self._reverse[token] = real_value
        return token

    def pseudonymize(self, text: str) -> str:
        """Replace all sensitive values in text with opaque tokens."""
        if not text:
            return text

        result = text

        # Private IPs: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
        for match in re.findall(r'\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', result):
            result = result.replace(match, self._get_token("IP", match))
        for match in re.findall(r'\b(172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b', result):
            result = result.replace(match, self._get_token("IP", match))
        for match in re.findall(r'\b(192\.168\.\d{1,3}\.\d{1,3})\b', result):
            result = result.replace(match, self._get_token("IP", match))

        # Hostnames (common patterns)
        for match in re.findall(r'\b((?:prod|staging|dev|ws|dc|app|db|web|file|mail|vpn|k8s|jump)[-\w]+\d+)\b', result):
            result = result.replace(match, self._get_token("HOST", match))

        # Usernames (firstname.lastname or service accounts)
        for match in re.findall(r'\b([a-z]\.[a-z]+)\b', result):
            if match not in ("e.g", "i.e", "a.m", "p.m"):
                result = result.replace(match, self._get_token("USER", match))
        for match in re.findall(r'\b(svc_\w+|admin_\w+|www-data|terraform_\w+)\b', result):
            result = result.replace(match, self._get_token("USER", match))

        # Email addresses
        for match in re.findall(r'\b([\w.+-]+@[\w-]+\.[\w.]+)\b', result):
            result = result.replace(match, self._get_token("EMAIL", match))

        # File paths
        for match in re.findall(r'(/(?:home|tmp|var|etc|usr|opt)/[\w/.]+)', result):
            result = result.replace(match, self._get_token("PATH", match))
        for match in re.findall(r'([A-Z]:\\[\w\\]+)', result):
            result = result.replace(match, self._get_token("PATH", match))

        return result

    def depseudonymize(self, text: str) -> str:
        """Restore original values from pseudonymized text."""
        result = text
        for token, real in self._reverse.items():
            result = result.replace(token, real)
        return result

    def get_mapping(self) -> dict:
        """Return the full forward mapping for audit purposes."""
        return dict(self._forward)
