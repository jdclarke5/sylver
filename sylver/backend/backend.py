"""Backends for storage of positions."""

class BaseBackend():
    
    def __init__(self):
        pass
    
    def save(self, position, status, replies):
        """Save a position (specified by its `to_dict()` method), determined 
        `status`, and add the `replies`.
        """
        raise NotImplementedError()
    
    def get_status(self, position):
        """Get the status of a position.
        """
        raise NotImplementedError()
    
    def get_id(self, position):
        """Get the ID for a position (default to position name).
        """
        return position.name

class LocalBackend(BaseBackend):

    def __init__(self):
        self.positions = {}

    def save(self, position, status, replies):
        key = self.get_id(position)
        existing = self.positions.get(key, {})
        self.positions[key] = {
            **position.to_dict(),
            "status": status,
            "replies": existing.get("replies", set()).union(replies),
        }
    
    def get_status(self, position):
        key = self.get_id(position)
        return self.positions.get(key, {}).get("status")
