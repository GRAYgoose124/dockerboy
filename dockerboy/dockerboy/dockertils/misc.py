# misc util helpers
def portcheck(port: tuple[int, int]):
    """ Ports can be malformed: (a,a) (a,) (,b) (a,b) """
    if isinstance(port[0], int) or isinstance(port[1], int):
        if port[0] is None:
            port = (port[1], port[1])
        elif port[1] is None:
            port = (port[0], port[0])

    return port