class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def join(self, other):
        """
        Creates a new bunch with the attributes of self and other copied into the same dictionary.
        This is intended to be used with reactive programming so that observables transformed by 
        select, scan etc. can carry through previous values by joining two bunches together.

        This is essentially a named tuple type with concatenation.
        
        :param other: the dictionary to join with this dictionary
        :return: a new Bunch with the elements of self and other
        """
        
        joined = Bunch()
        joined.__dict__ = dict(self.__dict__, **other.__dict__)
        return joined

def join(a, b=[]):
    return a.join(b)

def join_list(bunches):
    joined = Bunch()
    for bunch in bunches:
        joined = joined.join(bunch)
    return joined

