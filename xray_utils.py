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
    
class XRayLogfile(object):
    #
    # Wrapper object for logging - but can either point to a file-type object, or can be a no-op dummy.
    #
    # This lets us litter the code with calls to eg. logfile.write() without having to care if they do anything
    def __init__(self, logfile):
        self.logfile, self.fd = None, None
        
        self.switch_logfile(logfile)
    def write(self, data):
        if self.fd:
            self.fd.write(data)
    def writeln(self, data):
        #
        # A convenience function, prints 'data' followed by a newline.
        #
        if self.fd:
            self.fd.write(data)
            self.fd.write("\n")
    def close(self):
        if self.fd:
            self.fd.close()
    def flush(self):
        if self.fd:
            self.fd.flush()
    def switch_logfile(self, new_logfile):
        #
        # Switch between the current logfile and a new one.  
        #
        # Both can be either the name of a file or an empty string 
        # (an empty string equates to no logging, in which case
        # XRayLogfile will just throw the logging away silently)
        #
        if self.fd:
            self.fd.close()
        self.logfile = new_logfile
        if new_logfile:
            self.fd = open(self.logfile, "a")
        else:
            self.fd = None    