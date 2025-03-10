
# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import VyPy
from VyPy.data import ibunch
from VyPy.optimize.drivers import Driver
import numpy as np
from time import time

try:
    import scipy
    import scipy.optimize  
except ImportError:
    pass


# ----------------------------------------------------------------------
#   Sequential Least Squares Quadratic Programming
# ----------------------------------------------------------------------

class SLSQP(Driver):
    def __init__(self):
        
        # import check
        import scipy.optimize  
        
        Driver.__init__(self)
        
        self.verbose        = True
        self.max_iterations = 1000
    
    def run(self,problem):
        
        # store the problem
        self.problem = problem
        
        # single objective
        assert len(problem.objectives) == 1 , 'too many objectives'
        
        # optimizer
        import scipy.optimize  
        optimizer = scipy.optimize.fmin_slsqp
        
        # inputs
        func           = self.func
        x0             = problem.variables.scaled.initials_array()
        f_eqcons       = self.f_eqcons
        f_ieqcons      = self.f_ieqcons
        bounds         = problem.variables.scaled.bounds_array()
        fprime         = self.fprime
        fprime_ieqcons = self.fprime_ieqcons
        fprime_eqcons  = self.fprime_eqcons  
        iprint         = 2
        iters          = self.max_iterations
        
        # printing
        if not self.verbose: iprint = 0
        
        # gradients?
        dobj,dineq,deq = problem.has_gradients()
        if not dobj : fprime         = None
        if not dineq: fprime_ieqcons = None
        if not deq  : fprime_eqcons  = None
        
        # start timing
        tic = time()
        
        # run the optimizer
        x_min,f_min,its,imode,smode = optimizer( 
            func           = func           ,
            x0             = x0             ,
            f_eqcons       = f_eqcons       ,
            f_ieqcons      = f_ieqcons      ,
            bounds         = bounds         ,
            fprime         = fprime         ,
            fprime_ieqcons = fprime_ieqcons ,
            fprime_eqcons  = fprime_eqcons  ,
            iprint         = iprint         ,
            full_output    = True           ,
            iter           = iters          ,
            **self.other_options.to_dict()
        )
        
        # stop timing
        toc = time() - tic
        
        # get final variables
        vars_min = self.problem.variables.scaled.unpack_array(x_min)
        
        # pack outputs
        outputs = self.pack_outputs(vars_min)
        outputs.success               = imode == 0
        outputs.messages.exit_flag    = imode
        outputs.messages.exit_message = smode
        outputs.messages.iterations   = its
        outputs.messages.run_time     = toc
        
        # done!
        return outputs
            
    
    def func(self,x):
        objective = self.problem.objectives[0]
        result = objective.function(x)
        result = np.squeeze(result)
        return result
        
    def f_ieqcons(self,x):
        inequalities = self.problem.inequalities
        result = []
        for inequality in inequalities:
            res = inequality.function(x)
            res = -1 * res
            result.append(res)
        if result:
            result = np.vstack(result)
            result = np.squeeze(result)
        return result
    
    def f_eqcons(self,x):
        equalities = self.problem.equalities
        result = []
        for equality in equalities:
            res = equality.function(x)
            result.append(res)
        if result:
            result = np.vstack(result)
            result = np.squeeze(result)
        return result

    def fprime(self,x):
        objective = self.problem.objectives[0]
        result = objective.gradient(x)
        result = result.T
        result = np.vstack(result)
        result = np.squeeze(result)
        return result
    
    def fprime_ieqcons(self,x):
        inequalities = self.problem.inequalities
        result = []
        for inequality in inequalities:
            res = inequality.gradient(x)
            res = res.T
            res = -1 * res
            result.append(res)
        if result:
            result = np.vstack(result)
            result = np.squeeze(result)
        return result
    
    def fprime_eqcons(self,x):
        equalities = self.problem.equalities
        result = []
        for equality in equalities:
            res = equality.gradient(x)
            res = res.T
            result.append(res)
        if result:
            result = np.vstack(result)
            result = np.squeeze(result)
        return result
