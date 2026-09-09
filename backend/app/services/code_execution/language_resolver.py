import re
import time
from typing import Dict, List, Optional, Tuple, Any
from app.schemas.code_execution import LanguageItem
from app.core.logging import logger

# Canonical fallback Judge0 language IDs (standard official Judge0 CE mapping)
DEFAULT_CANONICAL_LANGUAGE_IDS: Dict[str, int] = {
    "python": 71,       # Python (3.8.1) / 92 (Python 3.11)
    "c": 50,            # C (GCC 9.2.0) / 105
    "cpp": 54,          # C++ (GCC 9.2.0) / 105
    "java": 62,         # Java (OpenJDK 13.0.1) / 91
    "javascript": 63,   # JavaScript (Node.js 12.14.0) / 93
    "typescript": 74,   # TypeScript (3.7.4) / 94
    "csharp": 51,       # C# (Mono 6.6.0.161)
    "go": 60,           # Go (1.13.5) / 95
    "rust": 73,         # Rust (1.40.0) / 107
    "ruby": 72,         # Ruby (2.7.0)
    "php": 68,          # PHP (7.4.1)
    "swift": 83,        # Swift (5.2.3)
    "kotlin": 78,       # Kotlin (1.3.70)
    "bash": 46,         # Bash (5.0.0)
    "sql": 82,          # SQL (SQLite 3.27.2)
}

# Alias dictionary mapping variants to canonical keys
LANGUAGE_ALIASES: Dict[str, str] = {
    "python": "python",
    "python3": "python",
    "python 3": "python",
    "py": "python",
    "c": "c",
    "gcc": "c",
    "clang": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "c plus plus": "cpp",
    "cplusplus": "cpp",
    "g++": "cpp",
    "cxx": "cpp",
    "java": "java",
    "openjdk": "java",
    "jdk": "java",
    "javascript": "javascript",
    "js": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
    "node.js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "csharp": "csharp",
    "c#": "csharp",
    "c sharp": "csharp",
    "cs": "csharp",
    "dotnet": "csharp",
    ".net": "csharp",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "rs": "rust",
    "ruby": "ruby",
    "rb": "ruby",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "kt": "kotlin",
    "bash": "bash",
    "sh": "bash",
    "shell": "bash",
    "sql": "sql",
    "sqlite": "sql",
}


class LanguageResolver:
    """
    Dynamically resolves user-provided language names/aliases to Judge0 language IDs.
    Caches languages fetched from Judge0 and falls back cleanly.
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_languages: List[LanguageItem] = []
        self._last_fetch_time: float = 0
        self._dynamic_map: Dict[str, int] = {}

    def set_languages(self, languages: List[LanguageItem]) -> None:
        """Updates internal cache and reindexes language aliases."""
        self._cached_languages = languages
        self._last_fetch_time = time.time()
        self._dynamic_map = self._build_dynamic_index(languages)
        logger.info(f"LanguageResolver indexed {len(languages)} languages from Judge0.")

    def is_cache_expired(self) -> bool:
        return (time.time() - self._last_fetch_time) > self.cache_ttl_seconds

    def get_cached_languages(self) -> List[LanguageItem]:
        return self._cached_languages

    def normalize_language_name(self, raw_name: str) -> str:
        """Cleans and standardizes user-provided language name."""
        if not raw_name:
            return ""
        cleaned = raw_name.strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def resolve_language(self, language_name: str) -> Tuple[int, str]:
        """
        Resolves a user-input language string to (judge0_language_id, canonical_name).
        Raises ValueError if language is unsupported or invalid.
        """
        norm = self.normalize_language_name(language_name)
        if not norm:
            raise ValueError("Programming language must be specified.")

        # Disambiguate Ruby on Rails vs Ruby
        if "rails" in norm or "ruby on rails" in norm:
            raise ValueError(
                "Ruby on Rails is a full-stack web application framework, not a standalone script runtime. "
                "To execute Ruby code, specify language as 'ruby'."
            )

        # Check alias dictionary
        canonical = LANGUAGE_ALIASES.get(norm, norm)

        # 1. Check dynamically resolved Judge0 index
        if canonical in self._dynamic_map:
            return self._dynamic_map[canonical], canonical

        # 2. Check direct match in dynamic languages list
        for item in self._cached_languages:
            item_norm = item.name.lower()
            if canonical in item_norm:
                return item.id, canonical

        # 3. Check fallback canonical map
        if canonical in DEFAULT_CANONICAL_LANGUAGE_IDS:
            return DEFAULT_CANONICAL_LANGUAGE_IDS[canonical], canonical

        # 4. Scan alias dictionary values with word boundaries
        for alias, target in LANGUAGE_ALIASES.items():
            pattern = rf"(?:^|\s|\b){re.escape(alias)}(?:$|\s|\b)"
            if re.search(pattern, norm):
                if target in self._dynamic_map:
                    return self._dynamic_map[target], target
                if target in DEFAULT_CANONICAL_LANGUAGE_IDS:
                    return DEFAULT_CANONICAL_LANGUAGE_IDS[target], target

        raise ValueError(
            f"Unsupported language '{language_name}'. Supported languages include: "
            "Python, C, C++, Java, JavaScript, TypeScript, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Bash, and SQL."
        )

    def _build_dynamic_index(self, languages: List[LanguageItem]) -> Dict[str, int]:
        """
        Builds a map from canonical alias to Judge0 ID, preferring newer/higher ID versions.
        """
        index: Dict[str, Tuple[int, str]] = {}  # alias -> (id, name)

        for lang in languages:
            name_lower = lang.name.lower()
            lid = lang.id

            # Determine matching key
            matched_key = None
            if "python" in name_lower:
                matched_key = "python"
            elif re.search(r"\bc\+\+\b", name_lower) or "g++" in name_lower or "clang++" in name_lower:
                matched_key = "cpp"
            elif re.search(r"\bc\b", name_lower) and "c++" not in name_lower and "c#" not in name_lower:
                matched_key = "c"
            elif "java " in name_lower or "openjdk" in name_lower or name_lower == "java":
                matched_key = "java"
            elif "javascript" in name_lower or "node" in name_lower:
                matched_key = "javascript"
            elif "typescript" in name_lower:
                matched_key = "typescript"
            elif "c#" in name_lower or "csharp" in name_lower or "mono" in name_lower:
                matched_key = "csharp"
            elif "go (" in name_lower or "golang" in name_lower:
                matched_key = "go"
            elif "rust" in name_lower:
                matched_key = "rust"
            elif "ruby" in name_lower:
                matched_key = "ruby"
            elif "php" in name_lower:
                matched_key = "php"
            elif "swift" in name_lower:
                matched_key = "swift"
            elif "kotlin" in name_lower:
                matched_key = "kotlin"
            elif "bash" in name_lower:
                matched_key = "bash"
            elif "sql" in name_lower:
                matched_key = "sql"

            if matched_key:
                # If existing version found, prefer higher ID (usually newer compiler version in Judge0)
                if matched_key not in index or lid > index[matched_key][0]:
                    index[matched_key] = (lid, lang.name)

        return {k: v[0] for k, v in index.items()}
