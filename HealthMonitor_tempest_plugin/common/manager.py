from tempest import clients
from tempest.common import credentials_factory as common_creds

class Manager(clients.Manager):

    def __init__(self, credentials=None, request_type=None):
            if not credentials:
                credentials = common_creds.get_configured_credentials(
                    'identity_admin')
            super(Manager, self).__init__(credentials)