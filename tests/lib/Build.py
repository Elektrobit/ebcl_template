from utils import cont_cmd

class Build:
    
    def build_containers(self):
        """Build the SDK containers."""
        cont_cmd('python3 build_container.py')
