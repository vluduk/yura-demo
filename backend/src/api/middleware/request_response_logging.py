import logging


class RequestResponseLoggingMiddleware:
    """Middleware that logs requests and responses, with special attention to 406 responses.

    Place early in the middleware stack so it sees requests before DRF content negotiation
    rejects them. Logs path, method, headers, user (if available) and a short body preview.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        try:
            user = getattr(request, 'user', None)
        except Exception:
            user = None

        # Small preview of body for logging (don't read large bodies)
        body_preview = None
        try:
            if request.body:
                body_preview = request.body[:500].decode('utf-8', errors='replace')
        except Exception:
            body_preview = '<unavailable>'

        self.logger.debug('Incoming request', extra={
            'path': getattr(request, 'path', None),
            'method': getattr(request, 'method', None),
            'user': getattr(user, 'email', None) if user else None,
            'headers': dict(getattr(request, 'headers', {})),
            'body_preview': body_preview,
        })

        response = self.get_response(request)

        # Log 406 specifically and other client/server errors
        try:
            status_code = getattr(response, 'status_code', None)
            if status_code == 406:
                self.logger.error('Response 406 Not Acceptable', extra={
                    'path': getattr(request, 'path', None),
                    'method': getattr(request, 'method', None),
                    'user': getattr(user, 'email', None) if user else None,
                    'headers': dict(getattr(request, 'headers', {})),
                    'response_content_type': response.get('Content-Type'),
                })
            elif status_code and status_code >= 400:
                self.logger.warning('Client/Server error response', extra={
                    'status_code': status_code,
                    'path': getattr(request, 'path', None),
                    'method': getattr(request, 'method', None),
                    'user': getattr(user, 'email', None) if user else None,
                })
        except Exception:
            self.logger.exception('Failed to log response status')

        return response
