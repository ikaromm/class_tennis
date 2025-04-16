import pickle as pk


class CacheInterface:
    """
    Interface for caching data.
    """

    def __init__(self, file_name: str):
        self.file_name = file_name

    def check_exists(self) -> bool:
        """
        Check if the cache file exists.
        """
        return self.file_name.exists()

    def load(self) -> dict:
        with open(self.file_name, "rb") as f:
            return pk.load(f)

    def save(self, data: dict):
        with open(self.file_name, "wb") as f:
            pk.dump(data, f)
