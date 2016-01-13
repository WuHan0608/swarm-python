# dockerpty.
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

from dockerpty.pty import PseudoTerminal
from dockerpty.expand_pty import ExpandPseudoTerminal


def start(client, container, interactive=True, stdout=None, stderr=None, stdin=None, logs=None):
    """
    Present the PTY of the container inside the current process.

    This is just a wrapper for PseudoTerminal(client, container).start()
    """

    PseudoTerminal(client, container, interactive=interactive, stdout=stdout, stderr=stderr, stdin=stdin, logs=logs).start()

def exec_start(client, exec_id, interactive=True, stdout=None, stderr=None, stdin=None):
    """
    Present the PTY of the exec command inside the current process.

    This is just a wrapper for ExpandPseudoTerminal(client, container).start(cmd)
    """

    ExpandPseudoTerminal(client, exec_id, interactive=interactive, stdout=stdout, stderr=stderr, stdin=stdin).start()