"""
tmux implementation of CommunicationInterface
"""
import logging
import sys

from queue import Queue, Empty
from time import sleep
from threading import Thread
from typing import Optional

import libtmux

from . import CommunicationInterface


class TmuxSessionDoesNotExist(Exception):
    """ Raised if the expected tmux session is not found. """


class TmuxPaneNotInitialized(Exception):
    """ Raised if the tmux pane is none. """


ON_POSIX = 'posix' in sys.builtin_module_names

PROMPT = '##PROMPT##'
STOP_THREAD = '###STOP###THREAD###'
# static storage for last output line
# pylint: disable=C0103
last_line = None


def _find_last_line(lines: list[str]) -> int:
    """ Find the last not reported line. """
    # pylint: disable=W0602
    global last_line

    for i, line in enumerate(lines):
        if line == last_line:
            return i

    return -1


def _capture_pane(queue: Queue, server_name: str, session_name: str):
    """ Capture the pane and report the new lines. """
    # pylint: disable=W0602
    # pylint: disable=W0603
    global last_line
    global PROMPT
    global STOP_THREAD

    sleep(0.1)

    server = libtmux.Server(socket_name=server_name)
    if not server:
        raise TmuxSessionDoesNotExist('No server!')
    session = server.sessions.get(session_name=session_name)
    if not session:
        raise TmuxSessionDoesNotExist(f'No session {session_name}!')

    while server.has_session(session_name):
        sleep(0.1)  # Give some processing time to other processes

        session = server.sessions.get(session_name=session_name)
        if not session:
            raise TmuxSessionDoesNotExist(f'No session {session_name}!')
        window = session.active_window
        if not window:
            raise TmuxSessionDoesNotExist('No active window!')
        pane = window.active_pane
        if not pane:
            raise TmuxSessionDoesNotExist('No active pane!')

        if pane.height:
            height = int(pane.height)
        else:
            height = 100

        lines = pane.capture_pane(0, height)

        if not lines:
            continue

        if isinstance(lines, str):
            queue.put(lines)
        else:
            h = _find_last_line(lines) + 1

            for line in lines[h:]:
                if line:
                    if line.startswith(STOP_THREAD):
                        return
                    if line.startswith(PROMPT):
                        # Skip input lines
                        continue

                    last_line = line
                    queue.put(line)

    logging.warning('No tmux session with the expected name!')


class TmuxConsole(CommunicationInterface):
    """
    tmux implementation of CommunicationInterface
    """

    # TODO: test

    session_name: str
    kill_session: bool

    server: libtmux.Server
    session: Optional[libtmux.Session]
    window: Optional[libtmux.Window]
    pane: Optional[libtmux.Pane]

    queue: Queue[str]

    def __init__(self, session_name="console", kill_session: bool = True):
        super().__init__()

        self.session_name = session_name
        self.kill_session = kill_session

        self.server = libtmux.Server(socket_name="target")
        self.session = None
        self.window = None
        self.pane = None

        self.queue = Queue()

    def connect(self):
        """ Create or open the tmux session. """
        # pylint: disable=W0602
        global PROMPT

        if not self.server.has_session(self.session_name):
            logging.info('Creating tmux session %s.', self.session_name)

        self.session = self.server.sessions.get(session_name=self.session_name)
        if not self.session:
            raise TmuxSessionDoesNotExist(
                f'No tmux session {self.session_name} found!')

        self.window = self.session.active_window
        if not self.window:
            raise TmuxSessionDoesNotExist('No tmux window found!')

        self.pane = self.window.active_pane
        if not self.pane:
            raise TmuxSessionDoesNotExist('No active pane found!')

        # Resize to avoid line breaks and data loss
        self.window.resize(width=10000, height=1000)
        self.pane.resize(width=10000, height=1000)

        logging.info('Resized pane size: w: %s h: %s',
                     self.pane.width, self.pane.height)

        # Clear pane
        self.pane.clear()
        sleep(0.5)

        # Configure pane to detect prompt lines
        self.send_message('bash')
        self.send_message(f'export PS1="{PROMPT}"')

        t = Thread(target=_capture_pane, args=(
            self.queue, self.session_name, self.session_name))
        t.daemon = True  # thread dies with the program
        t.start()

    def disconnect(self):
        """ Terminate the tmux session and threads. """
        # pylint: disable=W0602
        global STOP_THREAD
        # Stop the output readin thread
        self.send_message(STOP_THREAD)
        sleep(1)

        if self.kill_session:
            try:
                self.server.kill_session(self.session_name)
                sleep(1)
            except Exception as e:
                logging.error('Killing tmux session failed! %s',
                              e, stack_info=True)

    def send_message(self, message: str):
        if not self.pane:
            raise TmuxPaneNotInitialized()

        self.pane.send_keys(message, enter=True, suppress_history=True)

    def send_key(self, key: str):
        if not self.pane:
            raise TmuxPaneNotInitialized()

        self.pane.send_keys(key, enter=False)

    def read_line(self, timeout: int = 1) -> Optional[str]:
        if not self.pane:
            raise TmuxPaneNotInitialized()

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

    def clear_lines(self):
        """ Clear the output queue. """
        # Give the threads some time to read all the output,
        sleep(0.5)
        # then clear the output queue.
        with self.queue.mutex:
            self.queue.queue.clear()
