"""
Runs daily via GitHub Actions. Rewrites the content between marker comments
in README.md so the profile literally updates itself — no manual edits.

Sections it controls:
  LIVE:UPTIME     -> days since account creation, formatted like a system uptime counter
  LIVE:QUOTE      -> a rotating hacker/dev quote pulled from a public API
  LIVE:LASTBOOT   -> timestamp of this run, IST, styled like a reboot log line
  LIVE:CIPHER     -> a new ROT13-encoded easter-egg message each day
"""
import os
import random
import codecs
import datetime
import urllib.request
import json
import re

GITHUB_USER = "Sa7thak"
README_PATH = "README.md"

FALLBACK_QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Programs must be written for people to read.", "Harold Abelson"),
    ("There are only two hard things in CS: cache invalidation and naming things.", "Phil Karlton"),
    ("It works on my machine.", "Every developer, ever"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
]

EASTER_EGG_MESSAGES = [
    "if you can read this, you decoded rot13 by hand. respect.",
    "there is no secret. i just wanted you to open dev tools.",
    "the real treasure was the commits we made along the way.",
    "achievement unlocked: curiosity level 99.",
    "ping me, tell me you found this. bonus points for creativity.",
]


def get_account_age_days():
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{GITHUB_USER}",
            headers={"Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        created = datetime.datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        return (datetime.datetime.utcnow() - created).days
    except Exception:
        return None


def get_quote():
    try:
        req = urllib.request.Request("https://api.quotable.io/random?tags=technology|famous-quotes")
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        return data["content"], data["author"]
    except Exception:
        return random.choice(FALLBACK_QUOTES)


def rot13(text):
    return codecs.encode(text, "rot_13")


def replace_section(content, tag, new_value):
    pattern = rf"(<!--START_SECTION:{tag}-->)(.*?)(<!--END_SECTION:{tag}-->)"
    return re.sub(pattern, rf"\1\n{new_value}\n\3", content, flags=re.DOTALL)


def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    days = get_account_age_days()
    uptime_line = (
        f"`SYSTEM UPTIME: {days} days since first commit to existence on GitHub`"
        if days is not None
        else "`SYSTEM UPTIME: [unavailable this run]`"
    )
    content = replace_section(content, "UPTIME", uptime_line)

    quote_text, author = get_quote()
    quote_block = f"> \"{quote_text}\"\n> — {author}"
    content = replace_section(content, "QUOTE", quote_block)

    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    boot_line = f"`last self-update: {now_utc} · this file rewrote its own content to say that`"
    content = replace_section(content, "LASTBOOT", boot_line)

    msg = random.choice(EASTER_EGG_MESSAGES)
    cipher_block = f"<!-- decoded rot13: {msg} -->\n`{rot13(msg)}`"
    content = replace_section(content, "CIPHER", cipher_block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()
