import socket

def get_domain_name():
    try:
        hostname = socket.gethostbyaddr("127.0.0.1")[0]
        return hostname
    except socket.herror:
        return None

domain_name = get_domain_name()
if domain_name:
    print("Domain name associated with localhost: ", domain_name)
else:
    print("No domain name associated with localhost.")
