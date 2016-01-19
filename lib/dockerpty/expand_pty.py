# dockerpty: pty.py
#
# Copyright 2014 Chris Corbyn <chris@w3style.co.uk>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import signal
import socket
from ssl import SSLError

import dockerpty.io as io
import dockerpty.tty as tty


class WINCHHandler(object):
    """
    WINCH Signal handler to keep the PTY correctly sized.
    """

    def __init__(self, pty):
        """
        Initialize a new WINCH handler for the given PTY.

        Initializing a handler has no immediate side-effects. The `start()`
        method must be invoked for the signals to be trapped.
        """

        self.pty = pty
        self.original_handler = None


    def __enter__(self):
        """
        Invoked on entering a `with` block.
        """

        self.start()
        return self


    def __exit__(self, *_):
        """
        Invoked on exiting a `with` block.
        """

        self.stop()


    def start(self):
        """
        Start trapping WINCH signals and resizing the PTY.

        This method saves the previous WINCH handler so it can be restored on
        `stop()`.
        """

        def handle(signum, frame):
            if signum == signal.SIGWINCH:
                self.pty.resize()

        self.original_handler = signal.signal(signal.SIGWINCH, handle)


    def stop(self):
        """
        Stop trapping WINCH signals and restore the previous WINCH handler.
        """

        if self.original_handler is not None:
            signal.signal(signal.SIGWINCH, self.original_handler)


class ExpandPseudoTerminal(object):
    """
    Wraps the pseudo-TTY (PTY) allocated to a docker container.

    The PTY is managed via the current process' TTY until it is closed.

    Example:

        import docker
        from dockerpty import PseudoTerminal

        client = docker.Client()
        container = client.create_container(
            image='busybox:latest',
            stdin_open=True,
            tty=True,
            command='/bin/sh',
        )

        # hijacks the current tty until the pty is closed
        PseudoTerminal(client, container).start()

    Care is taken to ensure all file descriptors are restored on exit. For
    example, you can attach to a running container from within a Python REPL
    and when the container exits, the user will be returned to the Python REPL
    without adverse effects.
    """


    def __init__(self, client, exec_id, interactive=True, stdout=None, stderr=None, stdin=None):
        """
        Initialize the PTY using the docker.Client instance and container dict.
        """

        self.client = client
        self.exec_id = exec_id
        self.raw = None
        self.interactive = interactive
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.stdin = stdin or sys.stdin
        self.pty = None


    def start(self):
        """
        Present the PTY of the container inside the current process.

        This will take over the current process' TTY until the container's PTY
        is closed.
        """

        pty = self.sockets()

        try:
            with WINCHHandler(self):
                self._hijack_tty(pty)
        finally:
            pass


    def israw(self):
        """
        Returns True if the PTY should operate in raw mode.

        If the container was not started with tty=True, this will return False.
        """

        if self.raw is None:
            info = self.container_info()
            self.raw = self.stdout.isatty() and info['ProcessConfig']['tty']

        return self.raw


    def sockets(self):
        """
        Returns a tuple of sockets connected to the pty (stdin,stdout,stderr).

        If any of the sockets are not attached in the container, `None` is
        returned in the tuple.
        """

        info = self.container_info()

        def attach_socket(key):
            if info['Open{0}'.format(key.capitalize())]:
                return True
            return False

        if all(map(attach_socket, ('stdin', 'stdout', 'stderr'))):

            socket = self.client.exec_start(\
                self.exec_id,\
                tty=True,\
                socket=True\
            )

            stream = io.Stream(socket)

            if info['ProcessConfig']['tty']:
                return stream
            else:
                return io.Demuxer(stream)
        else:
            return None


    def resize(self, size=None):
        """
        Resize the container's PTY.

        If `size` is not None, it must be a tuple of (height,width), otherwise
        it will be determined by the size of the current TTY.
        """

        if not self.israw():
            return

        size = size or tty.size(self.stdout)

        if size is not None:
            rows, cols = size
            try:
                self.client.exec_resize(self.exec_id, height=rows, width=cols)
            except IOError: # Container already exited
                pass


    def container_info(self):
        """
        Thin wrapper around client.exec_inspect().
        """

        return self.client.exec_inspect(self.exec_id)


    def _hijack_tty(self, pty):
        with tty.Terminal(self.stdin, raw=self.israw()):
            self.resize()

            stdin, stdout = io.Stream(self.stdin), io.Stream(self.stdout)
            rlist = [ stdin ]
            wlist = [ stdout ]
            rlist.append(pty)

            while True:
                read_ready, write_ready = io.select(rlist, wlist, timeout=60)

                try:
                    if pty in read_ready:
                        stdout.write(pty.read())
                        while stdout.do_write() == 0:
                            break
                        rlist.remove(pty)
                        wlist.append(pty)
                    elif pty in write_ready:
                        read = stdin.read()
                        if read is None or len(read) == 0:
                            pty.close()
                            break
                        pty.write(read)
                        while pty.do_write() == 0:
                            break
                        wlist.remove(pty)
                        rlist.append(pty)

                except SSLError as e:
                    if 'The operation did not complete' not in e.strerror:
                        raise e
