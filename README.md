# False Positive Markup

This script is designed using Python 3, and Python 3 Requests.  Those must be available
for this script to operate properly.

## Overall Operation

Marking a finding inside of Code Dx as a `False Positive` is the beginning of a cycle of
activities that surround approval, and perhaps steps of approval.  Any finding inside of
Code Dx is modified when encountered in the target project to assign it to a user or
state determined by two flags in the configuration file.  Generally, a user is the better
choice as the name for the user is selectable, and may be used to include any number
of steps to go from `False Positive` to `Authorized False Positive`.

This script only uses two.  They are defined in the configuration file as:

* status-fp-auth
* status-fp-unauth

These strings may be any of the existant statuses inside of your Code Dx server.
They are place inside of your configuration file as part of the `FPmarkup` section.
Configuration options are described in the next section.

## Configuration

Here is an example of the first section of a configuration file.  Two sections are used
as part of the default script, but can be extended by script modification.  Order is not
a concern either.  Either section can appear in any order

```
[CodeDx]
transport = https
ip        = demo.codedx.tech
api-key   = f3453a48-ff13-4c53-a1ad-47302066cf5c

```

This section defines parameters for accessing the Code Dx server.  Our example does not
show it, but another parameter named `port` can be added to use any transport over any
port.  If excluded, the port will be set to `transport` default defined below:

* HTTP defaults to port 80
* HTTPS defaults to port 443

The `ip` may be any defining canonical address.  That includes dotted-ip notation, as well
as DNS name.  

Finally, the `api-key` defines an access key to the Code Dx server to set permissions
of the script.

A second part defines the available statuses to the script.  An example is below:

```
[FPmarkup]
status-fp-unauth = auth:fp_unauthorized
status-fp-auth   = auth:fp_authorized
```

This section shows the available steps, and the Code Dx status that would be used to
move there.  Our example script simply modifies the `False Positive` setting to either
`status-fp-auth` or `status-fp-unauth` depending on a subroutine call in the script.
That information is described in the next section.

## Script Operation

Testing of the `fpmarkup.py` script was performed on a secure-HTTP server (HTTPS).
Using the `requests` package throws a bunch of warnings about the certificate service
that was being used, but those objections were silenced since this is an example.
See below for more information on how this was accomplished.

Execution of the script is simple.

```bash
python fpauth.py --config myconfig.ini --proj "The Project"
```

Fixed values for any server are contained in the `myconfig.ini` configuration file.
A call for each affected project would be performed with the parameter for `--proj` changing.

Operationally, the script will check to see that the server is responsive by creating a
`CodeDx` object from the configuration file.  A check is then performed to see that the following
items exist on the server:

- The project specified by the `--proj` parameter
- A user that has the same name as specified by `status-fp-unauth`
- A user that has the same name as specified by `status-fp-auth`

If those checks are successful, all of the False Positives are gathered from the given
project.  Each is examined by the user modifiable subroutine `checkAuthorization`.  If
that routine returns `true`, then the False Positive marking is accepted, and the status
on the Code Dx server is modified to the name specified by `status-fp-auth`.
A False return marks the finding as `status-fp-unauth`.

The script in this version is stubbed by a simple routine that always returns False.

## Special Notes

A special addition to the script allows connections to HTTPS servers (the certificate authentication)
to *not* report the authority for the cert being unrecognized.  This is accomplished by the lines:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
...
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
```

These lines may be found inside of `CodeDx.py`.

If the certificate authority is recognized, or your server for Code Dx only uses HTTP, these
lines are not needed.





