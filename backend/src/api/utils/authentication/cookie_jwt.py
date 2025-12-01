import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework.request import Request
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extracts the access token from HttpOnly cookies
    instead of the Authorization header. This provides better security by preventing
    JavaScript access to the token.
    
    Falls back to standard header-based authentication if no cookie is found.
    """
    
    def authenticate(self, request: Request):
        """
        Override the authenticate method to extract the JWT token from cookies.
        
        Args:
            request: The HTTP request object
            
        Returns:
            tuple: (user, validated_token) if authentication succeeds
            None: if no token is found in cookies (allows fallback to other auth methods)
            
        Raises:
            AuthenticationFailed: if token is invalid or user is not active
        """
        # Try to get the access token from HttpOnly cookie
        access_token = request.COOKIES.get('access_token')

        if access_token is None:
            # No token in cookie, return None to allow other authentication classes to try
            logger.debug('No access_token cookie present on request; falling back to other auth classes')
            return None
        
        # Validate the token
        try:
            validated_token = self.get_validated_token(access_token)
        except InvalidToken as e:
            logger.exception('InvalidToken while validating access token from cookie')
            raise AuthenticationFailed(
                _('Invalid or expired access token'),
                code='token_invalid'
            )
        
        # Get the user from the validated token
        try:
            user = self.get_user(validated_token)
        except Exception as e:
            logger.exception('Error while fetching user from validated token')
            raise AuthenticationFailed(
                _('User not found or inactive'),
                code='user_not_found'
            )
        
        return (user, validated_token)
