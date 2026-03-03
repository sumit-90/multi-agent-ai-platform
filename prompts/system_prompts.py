from pathlib import Path
from typing import Any
import logging
from jinja2 import Environment, BaseLoader, StrictUndefined, UndefinedError


class PromptLoader:
    """Loads and renders Jinja2-templated prompt files from a configurable directory.

    Prompts are read from disk once and cached in memory for the lifetime of the
    process. Missing prompt files raise immediately with the full path in the message.
    Undefined template variables also raise, preventing silent prompt corruption.
    """

    def __init__(self, prompt_dir: str | Path) -> None:
        self._prompt_dir = Path(prompt_dir)
        self._cache: dict[str, str] = {}
        self._jinja_env = Environment(
            loader=BaseLoader(),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )
        self.logger = logging.getLogger("prompt.PromptLoader")

    def load(self, prompt_name: str) -> str:
        if prompt_name in self._cache:
            self.logger.debug(f"Cache hit — returning '{prompt_name}' from cache")
            return self._cache[prompt_name]

        self.logger.debug(f"Cache miss — loading '{prompt_name}' from disk")
        path = self._prompt_dir / f"{prompt_name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path.resolve()}")

        text = path.read_text(encoding="utf-8")
        self._cache[prompt_name] = text
        return text
    

    def render(self, prompt_name: str, **variables: Any) -> str:
        """Load *prompt_name* and render it with Jinja2 variable substitution.

        Args:
            prompt_name: Filename without the .txt extension.
            **variables: Template variables to inject (e.g. task="...", context="...").

        Returns:
            The rendered prompt string.

        Raises:
            FileNotFoundError: If the prompt file does not exist.
            jinja2.UndefinedError: If the template references a variable not supplied.
        """
        template_str = self.load(prompt_name)
        template = self._jinja_env.from_string(template_str)
        return template.render(**variables)

    def invalidate(self, prompt_name: str | None = None) -> None:
        """Evict one or all entries from the cache (useful in tests or after hot-reload).

        Args:
            prompt_name: Name to evict, or None to clear the entire cache.
        """
        if prompt_name is None:
            self._cache.clear()
        else:
            self._cache.pop(prompt_name, None)

    def __repr__(self) -> str:
        return (
            f"PromptLoader("
            f"prompt_dir={str(self._prompt_dir)!r}, "
            f"cached={list(self._cache.keys())})"
        )