
class ReorderBuffer:
    def __init__(self):
        self.tag = None
        self.repr = None
        self.ready = False
        self.busy = False
        self.wb_complete = False
        self.type = None
        self.fi = self.fj = self.fk = None        
        self.di = self.dj = self.dk = None #For common data bus
        self.qj = self.qk = False
        self.rj = self.rk = None 
    
    def clear(self):
        self.ready = False
        self.busy = False
        self.type = None
        self.fi = self.fj = self.fk = None
        self.qj = self.qk = None
        self.rj = self.rk = None
        
    def new_entry(self, fu, pc, dj, dk):
        self.repr = fu.repr
        self.type = fu.type
        self.dj = dj
        self.dk = dk
        self.tag = str(fu.repr[0].replace('.', ''))+ '.' + str(pc)
        if self.repr[0] == 'L.D':
            self.fj = None
            self.fk = None
        else:
            self.fj = fu.fj
            self.fk = fu.fk
        self.busy = True        
        self.fi = fu.fi
        return self.tag
        
    def printout(self):
        return(str(self.tag)  + ' '+ str(self.ready) + ' ' + str(self.fi) + ' ' + \
            str(self.dj) + ' ' + str(self.dk) + ' ' + str(self.qj) + ' ' + str(self.qk))
    
    def commit(self, mem, reg):
        return
