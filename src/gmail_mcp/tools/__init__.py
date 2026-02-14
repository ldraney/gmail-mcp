"""Tool registration — imports every tool module so @mcp.tool() decorators fire."""

from __future__ import annotations


def register_all_tools() -> None:
    """Import all tool modules, which register tools via the module-level @mcp.tool() decorators."""
    from . import messages  # noqa: F401
    from . import threads  # noqa: F401
    from . import drafts  # noqa: F401
    from . import labels  # noqa: F401
    from . import attachments  # noqa: F401
    from . import filters  # noqa: F401
    from . import settings  # noqa: F401
    from . import history  # noqa: F401
