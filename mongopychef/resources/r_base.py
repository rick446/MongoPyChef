class Resource(dict):

    def allow_access(self, permission):
        return permission == 'read' or self.request.client.admin
