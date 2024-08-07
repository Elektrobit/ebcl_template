## Quick start
_(All paths relative to this directory)_

1. Create a new virtual environment with `python3 -m venv pyenv`
2. Activate the virtual environment with `source pyenv/bin/activate`
3. Install the required packages with `pip install -r requirements.txt`
4. Run all tests with `python -m robot .`

## Creating new Keywords
New Keywords can either be created inside the `CommManager` class or in the `*** Keywords ***` section of a robot file. The basic building blocks for new these keywords are
- `send_message` to send command line to the target
- `wait_for_line`, `wait_for_line_exact`, `wait_for_regex` to wait for a specific output
- `execute` to send a command to the target and return all of its output

In accordance with robots language rules, assertions contain the word "should" as in `Line should be    <some_value>`.

## Creating a new Interface
Interfaces are represented by a python class the provides a very minimal api to the `CommManager` and stores all needed internal state. 

Each interface must extend the `CommunicationInterface` base class found in the `interfaces` module.
Specifically it must override the `send_key`, `send_message` and `read_line` methods and **no others**.

Additionally the new interface must be added to the `match` statement in `CommManager`
```
match mode:
    case "SSH":
        self.interface = SshInterface(*args)
    case "Serial":
        self.interface = TmuxConsole(*args)
    case "MY_NEW_INTERFACE":
        self.interface = MyNewInterface(*args)
```
Interfaces are instantiated on a Test Suite level (`ROBOT_LIBRARY_SCOPE = 'SUITE'`)
