#!/usr/bin/env python
"""Seed mock conversations + messages for a given user.

Usage (inside backend container):
  python /app/scripts/seed_mock_conversations.py --email admin@example.com

Notes:
- Idempotent: uses Conversation.summary_data['seed_key'] to avoid duplicates.
- Expects JSON schema: {"conversations": [{"key","title","conv_type","messages": [{"is_user","content"}]}]}
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import django


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--path",
        default=str(Path(__file__).with_name("mock_conversations.seed.json")),
        help="Path to seed JSON (default: alongside this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input and show counts without writing to DB",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    # Ensure /app is importable when run as a standalone script.
    app_root = str(Path(__file__).resolve().parents[1])
    if app_root not in sys.path:
        sys.path.insert(0, app_root)

    # Ensure Django is configured when running as a standalone script.
    try:
        from django.conf import settings as _settings  # noqa: F401
    except Exception:
        pass

    django.setup()

    from api.models.conversation import Conversation, ConversationType
    from api.models.message import Message
    from api.models.user import User

    seed_path = Path(args.path).expanduser().resolve()
    if not seed_path.exists():
        raise SystemExit(f"Seed file not found: {seed_path}")

    data = json.loads(seed_path.read_text(encoding="utf-8"))
    conversations = data.get("conversations")
    if not isinstance(conversations, list):
        raise SystemExit("Invalid seed JSON: 'conversations' must be a list")

    user = User.objects.filter(email=args.email).first()
    if not user:
        raise SystemExit(f"User not found with email: {args.email}")

    created_conversations = 0
    created_messages = 0
    skipped_existing = 0

    for item in conversations:
        key = item.get("key")
        title = item.get("title")
        conv_type = item.get("conv_type")
        messages = item.get("messages")

        if not key or not title or not conv_type or not isinstance(messages, list):
            raise SystemExit(f"Invalid conversation entry: {item}")

        try:
            conv_type_value = ConversationType[conv_type]
        except KeyError:
            allowed = ", ".join([e.name for e in ConversationType])
            raise SystemExit(f"Unknown conv_type '{conv_type}'. Allowed: {allowed}")

        existing = Conversation.objects.filter(
            user=user,
            summary_data__seed_key=key,
        ).first()
        if existing:
            skipped_existing += 1
            continue

        if args.dry_run:
            created_conversations += 1
            created_messages += len(messages)
            continue

        conv = Conversation.objects.create(
            user=user,
            title=title,
            conv_type=conv_type_value.value,
            summary_data={"seed_key": key, "seed_version": data.get("version", 1)},
        )
        created_conversations += 1

        msg_objs = []
        for msg in messages:
            if not isinstance(msg, dict) or "content" not in msg or "is_user" not in msg:
                raise SystemExit(f"Invalid message entry in '{key}': {msg}")
            msg_objs.append(
                Message(
                    conversation=conv,
                    content=msg["content"],
                    is_user=bool(msg["is_user"]),
                    context_used=msg.get("context_used") or {},
                )
            )

        Message.objects.bulk_create(msg_objs)
        created_messages += len(msg_objs)

    print(
        json.dumps(
            {
                "user_email": args.email,
                "seed_path": str(seed_path),
                "created_conversations": created_conversations,
                "created_messages": created_messages,
                "skipped_existing": skipped_existing,
                "dry_run": bool(args.dry_run),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    # When run inside the container, Django settings should already be discoverable
    # via /app/manage.py environment. If not, caller can export DJANGO_SETTINGS_MODULE.
    main()
