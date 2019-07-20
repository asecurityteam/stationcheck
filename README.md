<a id="markdown-SecDev Check" name="SecDev Check"></a>
# SecDev Workstation Check - A simple workstation setup tool

<https://github.com/asecurityteam/secdev-check>

<a id="markdown-overview" name="overview"></a>
SecDev Workstation Check
Determines if a machine has SecDev's recommended language and software requirements installed.
In cases where a requirement is missing or out-of-date, Workstation Checker will install the
software via brew.

How to add new requirements:

1) Create a variable under the "Requirement Versions" section below, like so:

```bash
    PYTHON="3.6"
```

2) Add a new command call for the req_checker function in the "Requirement Checks" section near the bottom
of the script. req_checker takes 5 arguments:

```bash
    req_checker <requirement name> <command> <version extraction manipulations> <required version> <installation command>
```

    For instance, if you wanted to add a Python 3.6 requirement, you would add the command:

```bash
      req_checker "Python" "python" "--version | cut -d ' ' -f2 2>&1" $PYTHON "brew install python3"
```

Why on earth is this written as a clunky bash script?

The Workstation Check is designed to work on fresh systems. It's fair to assume any new system
will have bash by default, and not much else. This was written to purposefully be a self-reliant file, thus it doesn't require any configuration from the end-user.

To make matters worse, there is no standard method to extract an isolated version number so each, individual installation will
require its own string manipulations.
