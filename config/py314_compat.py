# Python 3.14 compatibility shims for Django template Context copying
# Avoids "'super' object has no attribute 'dicts'" arising from __copy__ implementation

from __future__ import annotations

try:
    from django.template.context import Context, RequestContext
except Exception:  # pragma: no cover
    Context = None  # type: ignore
    RequestContext = None  # type: ignore


def _safe_context_copy(self: "Context") -> "Context":
    # If it's a RequestContext, return a plain Context with flattened data to avoid internals
    try:
        if RequestContext is not None and isinstance(self, RequestContext):
            try:
                flat = {}
                try:
                    flat = self.flatten()  # type: ignore[attr-defined]
                except Exception:
                    pass
                new_ctx = Context()
                try:
                    new_ctx.update(flat)
                except Exception:
                    for k, v in flat.items():
                        try:
                            new_ctx[k] = v
                        except Exception:
                            pass
                # Preserve render_context and template if present
                if hasattr(self, "render_context"):
                    try:
                        new_ctx.render_context = self.render_context  # type: ignore[attr-defined]
                    except Exception:
                        pass
                if hasattr(self, "template"):
                    try:
                        new_ctx.template = self.template  # type: ignore[attr-defined]
                    except Exception:
                        pass
                return new_ctx
            except Exception:
                return self
    except Exception:
        pass

    # Create a new instance of the same class without extra kwargs to avoid signature issues
    try:
        new = self.__class__()
    except Exception:
        # Fallback to base Context
        try:
            new = Context()
        except Exception:
            return self

    # Shallow copy internal structures if available
    if hasattr(self, "dicts"):
        try:
            new.dicts = list(self.dicts)  # type: ignore[attr-defined]
        except Exception:
            pass
    if hasattr(self, "render_context"):
        try:
            new.render_context = self.render_context  # type: ignore[attr-defined]
        except Exception:
            pass
    if hasattr(self, "template"):
        try:
            new.template = self.template  # type: ignore[attr-defined]
        except Exception:
            pass
    return new


def apply():
    if Context is not None:
        try:
            Context.__copy__ = _safe_context_copy  # type: ignore[assignment]
        except Exception:
            pass
    if RequestContext is not None:
        try:
            RequestContext.__copy__ = _safe_context_copy  # type: ignore[assignment]
        except Exception:
            pass


# Apply immediately on import
apply()
