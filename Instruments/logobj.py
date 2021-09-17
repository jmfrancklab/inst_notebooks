class logobj(object):
    def __init__(self,
            array_len = 1000 # just the size of the buffer
            ):
        self.log_list = []
        # {{{ this is a structured array
        self.log_dtype = dtype([('time','f8'),('Rx','f8'),('power','f8'),('cmd','i8')])
        self.log_array = empty(array_len, dtype=self.log_dtype)
        self.log_dict = {0:""} # use hash to convert commands to a number, and this to look up the meaning of the hashes
        # }}}
        self.currently_logging = False
        self.log_pos = 0
        self.array_len = array_len
        return
    def add(time=None,
            Rx=None,
            power=None,
            cmd=None):
        if time is None:
            time = time.time()
        if cmd is None:
            self.log_array[self.log_pos]['cmd'] = 0
        else:
            thehash = hash(cmd)
            self.log_dict[thehash] = cmd
            self.log_array[self.log_pos]['cmd'] = thehash
        assert Rx is not None
        self.log_array[self.log_pos]['Rx'] = Rx
        assert power is not None
        self.log_array[self.log_pos]['power'] = power
        # {{{ done for all additions
        self.log_pos += 1
        if self.log_pos == self.array_len:
            self.log_pos = 0
            self.log_list.append(self.log_array)
            self.log_array = empty(self.array_len, dtype=self.log_dtype)
        # }}}
        return self
    @property
    def total_log(self):
        "the log is stored internally as a list of arrays -- here return a single array for the whole log"
        if hasattr(self,'_totallog'):
            return self._totallog
        else:
            return concatenate(self.log_list+[self.log_array[:self.log_pos]])
    @total_log.setter
    def total_log(self,result):
        self._totallog = result
    def __getstate__(self):
        """return a picklable object -- I go with a dictionary that contains the message dict and the total array"""
        retval = {}
        retval["dict"] = self.log_dict
        retval["array"] = self.total_log
        return retval
    def __setstate__(self,inputdict):
        self.log_dict = inputdict["dict"]
        self.total_log = inputdict["array"]