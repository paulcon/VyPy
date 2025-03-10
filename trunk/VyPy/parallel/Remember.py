
from VyPy.data import load as load_data
from VyPy.data import save as save_data
from VyPy.data import HashedDict, make_hashable

import os, sys, time
from copy import deepcopy

# ----------------------------------------------------------------------
#   Remember
# ----------------------------------------------------------------------
class Remember(object):
    
    def __init__( self, function, filename='', write_freq=1, name='Remember'):
           
        # store
        self.function   = function
        self.filename   = filename
        self.write_freq = write_freq
        self.name       = name
        
        # initialize cache from file
        if filename and os.path.exists(filename) and os.path.isfile(filename):
            self.load_cache()
            
        # initialize new cache
        else:
            self.__cache__ = HashedDict()
        
        return
        
    def __func__(self,inputs):
        outputs = self.function(inputs)
        return outputs
        
    def __call__(self,inputs):
            
        # hashable type for cache
        _inputs = make_hashable(inputs)
                
        # check cache
        if self.__cache__.has_key(_inputs): 
            #print 'PULLED FROM CACHE'
            outputs = deepcopy( self.__cache__[_inputs] )
        
        # evalute function
        else:
            outputs = self.__func__(inputs)
            self.__cache__[_inputs] = deepcopy(outputs)
        
        #: if cached
        
        # save cache
        if self.filename and ( len(self.__cache__) % self.write_freq ) == 0:
            self.save_cache()
        
        # done
        return outputs
    
    def load_cache(self):
        if not self.filename:
            raise AttributeError , 'no filename for loading cache'
        self.__cache__ = load_data(filename)
    
    def save_cache(self):
        if not self.filename:
            raise AttributeError , 'no filename for saving cache'
        save_data(self.__cache__,self.filename)
    




