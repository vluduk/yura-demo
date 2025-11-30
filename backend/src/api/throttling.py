from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Throttle for login attempts.

    Uses scope 'login' with a rate configured in `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`.
    This protects the login endpoint from brute-force attempts.
    """
    scope = 'login'


class SignupRateThrottle(SimpleRateThrottle):
    """Throttle for signup attempts (more restrictive).

    Uses scope 'signup' so account creation is limited.
    """
    scope = 'signup'


class RefreshRateThrottle(SimpleRateThrottle):
    """Throttle for token refresh endpoint to avoid token abuse."""
    scope = 'refresh'


class CreateAdminRateThrottle(SimpleRateThrottle):
    """Highly restrictive throttle for the admin-creation helper."""
    scope = 'create_admin'
