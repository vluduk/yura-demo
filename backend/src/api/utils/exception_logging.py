import logging
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """Wrap DRF's exception handler to log 406 Not Acceptable and other errors.

    Logs request information when a 406 is about to be returned to aid debugging.
    """
    logger = logging.getLogger(__name__)
    response = drf_exception_handler(exc, context)

    try:
        request = context.get('request')
    except Exception:
        request = None

    if response is not None and getattr(response, 'status_code', None) == 406:
        try:
            user = getattr(request, 'user', None)
            logger.error('Returning 406 Not Acceptable', extra={
                'path': getattr(request, 'path', None),
                'method': getattr(request, 'method', None),
                'user': getattr(user, 'email', None) if user else None,
                'headers': dict(getattr(request, 'headers', {})),
            })
        except Exception:
            logger.exception('Failed to log 406 context')

    # Also log unexpected server errors for visibility
    if response is not None and 500 <= response.status_code < 600:
        try:
            logger.exception('Server error during request', extra={
                'path': getattr(request, 'path', None),
                'method': getattr(request, 'method', None),
                'user': getattr(getattr(request, 'user', None), 'email', None),
            })
        except Exception:
            logger.exception('Failed to log server error context')

    return response
