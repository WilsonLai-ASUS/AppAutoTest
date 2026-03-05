# utils.py

"""
Utils
"""


from importlib.resources import path


class Utils:

    @staticmethod
    def delay(seconds:float=1.0):
        import time

        time.sleep(seconds)

    @staticmethod
    def get_absolute_path(path):
        import os

        if path is None:
            return None

        if os.path.isabs(path):
            return path

        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, path)
