class Resource(dict):

    def allow_access(self, client, permission):
        return permission == 'read' or client.admin
