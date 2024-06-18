class TrustedPeople:
    def __init__(self, trusted_ids):
        self.trusted_ids = trusted_ids

    def is_trusted(self, user_id):
        return user_id in self.trusted_ids
