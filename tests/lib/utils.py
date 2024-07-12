import subprocess
import os
import docker
import docker.errors


def cont_cmd(command, check=True):
    """Run shell command in container folder."""
    workdir = os.path.abspath(os.path.join((os.path.abspath(__file__)), os.path.pardir, os.path.pardir, os.path.pardir, 'container'))
    print(f'WORKDIR: {workdir}')
    subprocess.run(
        command,
        cwd=workdir,
        shell=True,
        check=check
    ) 


def run_container():
    """Run the SDK container."""
    cont_cmd('./run_background')

    if 'RUNNER' not in os.environ or os.environ['RUNNER'] is None:
        # wait for the container to start
        client = docker.from_env()
        while(True):
            try:
                client.containers.get('ebcl_sdk')
                break
            except docker.errors.NotFound:
                pass


def stop_container():
    """Stop the SDK container."""
    # kill the sleep to stop the container
    run_command('pkill -9 -f sleep', check=False, no_error=False)
    # just to ensure it's really stopped
    cont_cmd('./stop_container', check=False)


def run_command(command, check=True, no_error=True):
        """Exec command in SDK container."""
        runner = 'docker'
        if 'RUNNER' in os.environ:
             runner = os.environ['RUNNER']

        result = subprocess.run(
            f'{runner} exec -it ebcl_sdk bash -c "source ~/.bashrc; {command}"',
            shell=True,
            capture_output=True,
            check=False
        )

        stderr = result.stderr.decode('utf8')
        stdout = result.stdout.decode('utf8')

        if check:
            assert result.returncode == 0

        lines = [line.strip() for line in stdout.split('\n')]
        
        if no_error:
            assert stderr == ''

        return (lines, stdout, stderr)
