import os

def resource_path(relative_path:str) -> str:
    """
    バイナリフィルのパスを提供
    """
    base_path:str = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)