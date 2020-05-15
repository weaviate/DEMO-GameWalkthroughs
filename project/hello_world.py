def say_hello(name):
    """

    :param name: of the person that should be greeted.
    :type name: str
    :return: A welcome message
    :rtype: str
    """
    return f"Hello {name}"


if __name__ == "__main__":
    say_hello("world")
