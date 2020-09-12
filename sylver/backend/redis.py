"""Redis key-value store backend."""

from .backend import BaseBackend

import yaml
import redis


class RedisBackend(BaseBackend):

    def __init__(self, **kwargs):
        """Initialise Redis client by passing **kawrgs to `redis.Redis`.
        """
        self.redis = redis.Redis(**kwargs)
    
    def set(self, key, dictionary):
        """Set a python dictionary as a YAML string in Redis. Note that YAML
        is used because it supports sets.
        """
        yaml_dictionary = yaml.dump(dictionary)
        self.redis.set(key, yaml_dictionary)

    def get(self, key):
        """Retrieve a python dictionary from a YAML string in Redis. Note that 
        YAML is used because it supports sets.
        """
        yaml_dictionary = self.redis.get(key)
        return yaml.safe_load(yaml_dictionary) if yaml_dictionary else None

    def save(self, position, status, replies):
        """Redis implementation of BaseBackend method.
        """
        key = self.get_id(position)
        existing = self.get(key) or {}
        entry = {
            **position.to_dict(),
            "status": status,
            "replies": existing.get("replies", set()).union(replies),
        }
        self.set(key, entry)
    
    def get_status(self, position):
        """Redis implementation of BaseBackend method.
        """
        key = self.get_id(position)
        existing = self.get(key) or {}
        return existing.get("status", None)
