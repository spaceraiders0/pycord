"""This is used to easily communicate between the client, and the server. It
uses the multiprocessing module's wrappers around the socket module.
"""


from multiprocessing.connection import Client, Listener


def create_server(address: tuple = ("127.0.0.1", 5832)) -> Listener:
    """Creates a new server that will listen for requests on a port.

    :param address: a tuple containing the IP address, and port
    :type address: tuple
    :return: a new Listener object bound to a specific address
    :rtype: Listener
    """

    return Listener(address)


def create_client(address: tuple = ("127.0.0.1", 5832)) -> Client:
    """Creates a new client that can be used to send requests to a server. 

    :param address: a tuple containing the IP address, and port
    :type address: tuple
    :return: a new Client object bound to a specific address
    :rtype: Listener
    """

    return Client(address)
