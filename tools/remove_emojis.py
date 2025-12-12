import argparse
import os
import re
import sys
from pathlib import Path


# Regex covering common emoji blocks and related modifiers
# Ranges include: Misc Symbols & Pictographs, Emoticons, Transport, Supplemental Symbols,
# Symbols & Pictographs Extended-A, Dingbats, Misc Symbols, Regional Indicators (flags),
# Skin tone modifiers, Variation selectors, Zero-width joiner, Keycap combining, Tags
EMOJI_RE = re.compile(
    "["  # start char class
    "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\u2600-\u26FF"          # Miscellaneous Symbols
    "\u2700-\u27BF"          # Dingbats
    "\U0001F1E6-\U0001F1FF"  # Regional Indicator Symbols (flags)
    "]",
    flags=re.UNICODE,
)

# Additional characters used in emoji sequences
MODIFIERS_RE = re.compile(
    "["  # start char class
    "\U0001F3FB-\U0001F3FF"  # Skin tone modifiers
    "\uFE0E\uFE0F"            # Variation selectors
    "\u200D"                   # Zero-width joiner
    "\u20E3"                   # Combining enclosing keycap
    "\U000E0000-\U000E007F"   # Tags
    "]",
    flags=re.UNICODE,
)


TEXT_LIKE_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".html",
    ".css",
    ".scss",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".csv",
    ".tsv",
    ".env",
    ".sh",
    ".bat",
    ".xml",
    ".ics",
}

BINARY_LIKE_EXTENSIONS = {
    ".lockb",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".ttf",
    ".woff",
    ".woff2",
    ".eot",
    ".mp4",
    ".zip",
    ".gz",
    ".tar",
    ".jar",
    ".egg",
    ".db",
    ".sqlite",
    ".so",
    ".dylib",
    ".bin",
}

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "node_modules",
    "dist",
    "build",
}


def is_text_candidate(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in BINARY_LIKE_EXTENSIONS:
        return False
    if ext in TEXT_LIKE_EXTENSIONS:
        return True
    # Default heuristic: try opening small files as UTF-8 to decide
    try:
        with path.open("r", encoding="utf-8") as f:
            f.read(2048)
        return True
    except Exception:
        return False


def strip_emojis(text: str) -> tuple[str, int]:
    removed = 0

    def repl(m):
        nonlocal removed
        removed += len(m.group(0))
        return ""

    text2 = EMOJI_RE.sub(repl, text)
    text3 = MODIFIERS_RE.sub(repl, text2)
    return text3, removed


def process_file(path: Path, dry_run: bool = False, max_size_bytes: int = 5 * 1024 * 1024):
    try:
        if path.stat().st_size > max_size_bytes:
            return 0, False
    except FileNotFoundError:
        return 0, False

    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Not UTF-8 text
        return 0, False
    except Exception:
        return 0, False

    cleaned, removed = strip_emojis(original)
    if removed > 0 and not dry_run:
        try:
            path.write_text(cleaned, encoding="utf-8")
        except Exception:
            return 0, False
    return removed, removed > 0


def walk_and_clean(root: Path, dry_run: bool) -> tuple[int, int, list[Path]]:
    total_removed = 0
    files_changed = 0
    changed_paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter excluded directories in-place for os.walk efficiency
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for fname in filenames:
            p = Path(dirpath) / fname
            if not is_text_candidate(p):
                continue
            removed, changed = process_file(p, dry_run=dry_run)
            total_removed += removed
            if changed:
                files_changed += 1
                changed_paths.append(p)
    return total_removed, files_changed, changed_paths


def main():
    parser = argparse.ArgumentParser(description="Remove all emoji characters from text files in a repository.")
    parser.add_argument("--root", type=str, default=str(Path.cwd()), help="Root directory to process")
    parser.add_argument("--check", action="store_true", help="Only report files that would change")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    dry_run = args.check

    total_removed, files_changed, changed_paths = walk_and_clean(root, dry_run=dry_run)

    action = "would be removed" if dry_run else "removed"
    print(f"Emoji characters {action}: {total_removed}")
    print(f"Files {'to be changed' if dry_run else 'changed'}: {files_changed}")
    if changed_paths:
        for p in changed_paths[:200]:  # cap to avoid massive output
            rel = p.relative_to(root)
            print(f" - {rel}")
        if len(changed_paths) > 200:
            print(f" ... and {len(changed_paths) - 200} more")

    # Exit non-zero in check mode if changes are detected
    if dry_run and files_changed > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
