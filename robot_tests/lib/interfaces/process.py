"""
tmux implementation of CommunicationInterface
"""
import logging
import sys

from queue import Queue, Empty
from subprocess import PIPE, Popen
from threading import Thread
from time import sleep
from typing import Optional

from . import CommunicationInterface


ON_POSIX = 'posix' in sys.builtin_module_names


class ProcessNotInitialized(Exception):
    """ Raised if shell process is not initialized. """


class ProcessIsDead(Exception):
    """ Raised if communicate fails. """


def _enqueue_output(out, queue: Queue, prefix: str = ''):
    """ Read and queue line. """
    for line in iter(out.readline, ''):
        if prefix and line:
            line = prefix + line

        logging.info('Adding: %s', line)

        queue.put(line)
    out.close()


class ShellSubprocess(CommunicationInterface):
    """
    Subprocess implementation of CommunicationInterface
    """
    shell: str
    queue: Queue[str]
    process: Optional[Popen]
    out_thread: Thread
    err_thread: Thread

    def __init__(self, shell="bash"):
        super().__init__()

        self.shell = shell
        self.queue = Queue()
        self.process = None

    def __del__(self):
        if self.process:
            self.process.kill()

    def _process_command(self) -> list[str]:
        """ Get the command to execute. """
        return [self.shell]

    def connect(self):
        """ Open shell process. """
        if self.process:
            logging.info(
                'Old shell session found. Closing old shell session...')
            self.disconnect()

        logging.info('Running shell %s...', self.shell)

        self.process = Popen(self._process_command(), stdout=PIPE, stderr=PIPE, stdin=PIPE,
                             bufsize=1, close_fds=ON_POSIX, shell=True, encoding='utf-8')

        logging.info('Starting IO threads...')

        self.err_thread = Thread(target=_enqueue_output, args=(
            self.process.stderr, self.queue, 'ERR: '))
        self.err_thread.daemon = True
        self.err_thread.start()

        self.out_thread = Thread(target=_enqueue_output, args=(
            self.process.stdout, self.queue))
        self.out_thread.daemon = True
        self.out_thread.start()

    def disconnect(self):
        """ Close shell process. """
        if not self.process:
            return

        rc = self.process.poll()
        if rc:
            logging.info(
                'Nothing to do. Shell session ended with returncode %d.', rc)

        logging.info('Shutting down shell with PID %d...', self.process.pid)

        logging.info('Sending exit command...')
        self.send_message('exit')

        logging.info('Waiting for the shell to exit...')
        try:
            self.process.wait(timeout=30)
        except Exception as e:
            logging.info(
                'Waiting for bash to terminate after exit failed: %s', e)

        rc = self.process.poll()
        logging.info('Shell return code: %s', rc)
        if rc is not None:
            logging.info('Shell session ended with returncode %d.', rc)
        else:
            logging.warning('Killing shell...')
            self.process.kill()

        self.process = None

    def send_message(self, message: str):
        if not message.endswith('\n'):
            message += '\n'

        self.send_keys(message)

    def send_key(self, key: str):
        if not self.process:
            raise ProcessNotInitialized()

        assert self.process.stdin

        logging.info('Sending key \'%s\'.', key)

        self.process.stdin.write(key)

    def send_keys(self, keys: str):
        if not self.process:
            raise ProcessNotInitialized()

        assert self.process.stdin

        logging.info('Sending keys \'%s\'.', keys)

        self.process.stdin.write(keys)

    def read_line(self, timeout: int = 1) -> Optional[str]:
        if not self.process:
            raise ProcessNotInitialized()

        line: str
        try:
            if timeout > 0:
                line = self.queue.get(timeout=timeout)
            else:
                line = self.queue.get()
        except Empty:
            logging.info('No line, queue is empty (timeout: %d)...', timeout)
            return None

        logging.info('Line: %s', line)
        return line + '\n'

    def create_session(self):
        """ Nothing to do. """

    def clear_lines(self):
        """ Clear the output queue. """
        # Give the threads some time to read all the output,
        sleep(0.5)
        # then clear the output queue.
        with self.queue.mutex:
            self.queue.queue.clear()
