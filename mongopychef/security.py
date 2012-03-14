import logging

from pyramid.authorization import ACLAuthorizationPolicy

log = logging.getLogger(__name__)


class ChefAuthorizationPolicy(ACLAuthorizationPolicy):
    """ An object representing a Pyramid authorization policy. """

    def permits(self, context, principals, permission):
        """ Return ``True`` if any of the ``principals`` is allowed the
        ``permission`` in the current ``context``, else return ``False``
        """
        if hasattr(context, 'allow_access'):
            return context.allow_access(permission)
        return True
