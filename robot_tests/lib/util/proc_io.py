"""
Generic subprocess communication.
"""
import logging

from queue import Queue, Empty
from subprocess import Popen, TimeoutExpired, check_output, run, CalledProcessError, DEVNULL
from threading import Thread
from time import sleep, time
from typing import Tuple, Optional


def kill_process_tree(pid: str):
    """ Kill all processes belonging to the subtree of the given pid. """
    # Get child processes
    try:
        out = check_output(['pgrep', '-P', str(pid)])
        out_txt = out.decode("utf-8")
        processes = [ p.strip() for p in out_txt.split('\n') ]
        # Remove empty entries
        processes = list(filter(None, processes))
    except CalledProcessError:
        # pgrep returns 1 in case of no childs
        processes = []

    if processes:
        # List is not empty, recursion for child processes
        logging.debug('Process %s has sub processes %s.', str(pid), str(processes))
        for cpid in processes:
            kill_process_tree(cpid)

    logging.info('Killing process %s...', str(pid))
    run(f'kill -9 {pid}', shell=True, check=False, stderr=DEVNULL)


def _enqueue_output(out, queue: Queue, label: str):
    """ Read and queue line. """
    for line in iter(out.readline, ''):
        queue.put((line, label, time()))
    out.close()


class ProcIO:
    """
    Implements subprocess communication.
    """
    def __init__(self, process: Popen, channel_prefix=False, timestamp_prefix=False):
        self.process = process
        self.channel_prefix = channel_prefix
        self.timestamp_prefix = timestamp_prefix

        self.err_thread = None
        self.out_thread = None

        self.queue: Queue[Tuple[str, str, float]] = Queue()

    def connect(self):
        """ Run input threads. """
        logging.info('Starting IO threads...')

        self.err_thread = Thread(target=_enqueue_output, args=(
            self.process.stderr, self.queue, 'ERR'))
        self.err_thread.daemon = True
        self.err_thread.start()

        self.out_thread = Thread(target=_enqueue_output, args=(
            self.process.stdout, self.queue, 'OUT'))
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
            return

        logging.info('Shutting down shell with PID %d...', self.process.pid)
        logging.info('Sending exit command...')

        try:
            self.process.stdin.write('exit\n')
        except Exception as e:
            logging.info('Sending exit failed. %s', e)

        logging.info('Waiting for the shell to exit...')
        try:
            self.process.wait(timeout=30)
        except TimeoutExpired as e:
            logging.info(
                'Waiting for bash to terminate after exit failed: %s', e)

        rc = self.process.poll()
        logging.info('Shell return code: %s', rc)

        if rc is not None:
            logging.info('Shell session ended with returncode %d.', rc)
        else:
            logging.info('Killing shell and subprocesses...')
            kill_process_tree(self.process.pid)

        self.process = None

    def write(self, message: str) :
        """ Write a message to the process. """
        if not self.process:
            logging.error('ProcIO: write: No process!')
            return

        if not self.process.stdin:
            logging.error('ProcIO: write: No stdin!')
            return

        try:
            self.process.stdin.write(message)
        except Exception as e:
            logging.error('Writing to process failed! %s', e)

    def read_line(self, timeout: int = 1) -> Optional[str]:
        """
        Read next line of process output.
        """
        res = self.read_line_raw(timeout)

        if res:
            (line, label, ts) = res

            if self.channel_prefix:
                line = f'{label}: {line}'

            if self.timestamp_prefix:
                ts *= 1000000
                ts = int(ts)
                line = f'{ts}: {line}'

            return line
        else:
            return None

    def read_line_raw(self, timeout: int = 1) -> Optional[Tuple[str, str, float]]:
        """
        Read next line of process output.
        """
        if not self.process:
            logging.error('ProcIO: read_line: No process!')
            return None

        line: Tuple[str, str, float]
        try:
            if timeout > 0:
                line = self.queue.get(timeout=timeout)
            else:
                line = self.queue.get()
        except Empty:
            logging.info('No line, queue is empty (timeout: %d)...', timeout)
            return None

        logging.debug('%s', str(line))
        return line

    def clear_lines(self):
        """ Clear the output queue. """
        # Give the threads some time to read all the output,
        sleep(0.5)
        # then clear the output queue.
        with self.queue.mutex:
            self.queue.queue.clear()
