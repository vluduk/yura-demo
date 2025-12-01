from rest_framework.renderers import BaseRenderer


class EventStreamRenderer(BaseRenderer):
    """A minimal renderer that advertises support for text/event-stream Accept header.

    It doesn't attempt to transform generator responses (StreamingHttpResponse is
    used in the view), but registering this renderer prevents DRF from returning
    406 Not Acceptable for clients requesting `text/event-stream`.
    """
    media_type = "text/event-stream"
    format = "event-stream"
    charset = None

    def render(self, data, media_type=None, renderer_context=None):
        # If DRF chooses to use this renderer, return bytes/str as-is.
        if data is None:
            return b""
        if isinstance(data, bytes):
            return data
        return str(data).encode("utf-8")
