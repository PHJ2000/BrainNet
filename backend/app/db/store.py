#backend/app/db/store.py
from typing import Dict, List, Any

USERS: Dict[str, Dict[str, Any]] = {}
PROJECTS: Dict[str, Dict[str, Any]] = {}
NODES: Dict[str, Dict[str, Any]] = {}
TAGS: Dict[str, Dict[str, Any]] = {}
USER_PROJECT_MAP: Dict[str, List[str]] = {}
PROJECT_MEMBER_MAP: Dict[str, List[str]] = {}
NODE_TAG_MAP: Dict[str, List[str]] = {}

VOTES: List[Dict[str, Any]] = []
PROJECT_HISTORY: List[Dict[str, Any]] = []
INVITES: Dict[str, Dict[str, str]] = {}
