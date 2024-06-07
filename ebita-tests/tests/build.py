from ebita.api.test_class_base import TestClassBase
from utils import cont_cmd

class Build(TestClassBase):

    def build_containers(self):
        """Build the SDK containers."""
        cont_cmd('./build_container')
