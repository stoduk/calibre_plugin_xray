from collections import OrderedDict

class OrderedDefaultdict(OrderedDict):
    """
    An ordered default dictionary, see OrderedDict or defaultdict in collections module.
    
    Taken from http://stackoverflow.com/questions/4126348/how-do-i-rewrite-this-function-to-implement-ordereddict/4127426#4127426 by martineau
    """
    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.iteritems()