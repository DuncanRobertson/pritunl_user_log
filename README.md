# pritunl_user_log

This is a simple python3 script to generate a log of connected clients for a [Pritunl](https://pritunl.com/) VPN system.

I recently moved from [OpenVPN Access Server](https://openvpn.net/access-server/) to the PRITUNL Premium subscription, and this has met all my requirements fairly well except for not having a running log of who has logged into the system. 

The Pritunl "Enterprise" subscription has a comprehensive auditing feature, but the Premium subscription and free version only shows the currently logged in users in the web UI.

This has been tested with the "Premium" subscription install but should work fine with the Free tier as well.

Tested with PRITUNL version 1.29.2664.67.

It uses a basic MongoDB query to gather the information, and assumes the pritunl mongoDB is running on locally with no authentication (default simple singler server install). The MongoDB login portion of the script can be adjusted for any other situation.

The script can run once off like a "who" command, or run continuously logging to standard out and/or syslog.

This has been tested on Rocky Linux 8.4 and Ubuntu 20.04.

Provided under the GPL v2 license with absolutely no warranty.

