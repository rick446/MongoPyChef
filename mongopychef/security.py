import logging

from pyramid.authorization import ACLAuthorizationPolicy

from . import model as M

log = logging.getLogger(__name__)


class ChefAuthorizationPolicy(ACLAuthorizationPolicy):
    """ An object representing a Pyramid authorization policy. """

    def permits(self, context, principals, permission):
        """ Return ``True`` if any of the ``principals`` is allowed the
        ``permission`` in the current ``context``, else return ``False``
        """
        for p in principals:
            if isinstance(p, M.Client):
                if p.admin: return True
        return super(ChefAuthorizationPolicy, self).permits(context, principals, permission)

