from RestrictedPython import compile_restricted, Eval, Guards, safe_builtins, limited_builtins, utility_builtins

class Value(object):                                                                                                                                                            
   def __init__(self, value, properties={}, timestamp=0.0):
      self.value = value       
      self.properties = properties                                                                                                                                    
      self.timestamp = timestamp
      self._guarded_writes = True
           
   def _asdict(self):                                                                                                                                          
      return {
         "value": self.value,   
         "properties": self.properties,
         "timestamp": self.timestamp
      }   

class Context(object):
   def __init__(self, logger, state, blockParameters):
      self.logger = logger
      self._state = state
      self.blockParameters = [blockParameters['param1'], blockParameters['param2'], blockParameters['param3'], blockParameters['param4'], blockParameters['param5']]

   def getState(self, key, default=None):
      if key not in self._state:
         self._state[key] = default
      return self._state[key]

   def setState(self, key, value):
      self._state[key] = value

   def hasState(self, key):
      return key in self._state

def noop_getattr(obj, name):
    return getattr(obj, name)

def noop_setattr(obj, name, value):
    setattr(obj, name, value)

def noop_getitem(obj, key):
    return obj[key]

def noop_getiter(obj):
    return iter(obj)

def noop_iter_unpack_sequence(obj):
    return iter(obj)

def noop_unpack_sequence(obj):
    return tuple(obj)

def noop_write(*args):
    if len(args) == 1:
        return args[0]
    elif len(args) == 2:
        name, value = args
        globals()[name] = value
        return value
    elif len(args) == 3:
        obj, name, value = args
        setattr(obj, name, value)
        return value
    else:
        raise TypeError(f"unexpected number of arguments: {len(args)}")

def noop_setitem(obj, key, value):
    obj[key] = value
    return value

def practical_write(*args):
    if len(args) == 1:
        # sometimes called with just a single sentinel or value
        return args[0]

    elif len(args) == 2:
        # variable assignment: name, value
        name, value = args
        if isinstance(name, str) and name.startswith("_"):
            raise TypeError(f"assignment to private variable {name} is forbidden")
        globals()[name] = value
        return value

    elif len(args) == 3:
        # attribute assignment: obj, name, value
        obj, name, value = args
        if isinstance(name, str) and name.startswith("_"):
            raise TypeError(f"assignment to private attribute {name} is forbidden")
        try:
            setattr(obj, name, value)
        except AttributeError:
            # fallback for attribute-less objects (numpy scalars, pandas Index)
            obj[name] = value
        return value

    else:
        raise TypeError(f"unexpected number of arguments: {len(args)}")


code = """
import pandas as pd
import numpy as np
def onInput(inputs, context):
    
    if inputs[0].value != None:
        queue = context.getState('queue',{})
        queue[inputs[0].timestamp] = inputs[0].value
        context.setState('queue', queue)

    if(inputs[1].value):
        queue = context.getState('queue', {})
        s = dict(sorted(queue.items()))
        s = { round(k,3):s[k] for k in s }
        signal_ts = pd.DataFrame(data=s.values(), index=s.keys(), columns=['value'])
        signal_ts.index = np.array(list(map(lambda x: int(x*1000), sorted(s.keys()))), dtype='datetime64[ms]')
        context.setState('queue', {})
        return [Value(True,{'series': signal_ts.to_dict()})]
"""
bytecode = compile_restricted(code, '<string>', 'exec')


# 187       "__builtins__": {**safe_builtins, **limited_builtins, **utility_builtins,
#  188          "__name__": "restricted_python_block",
#  189          "__metaclass__": type,
#  190          "_getiter_": Eval.default_guarded_getiter,
#  191          "_getitem_": Eval.default_guarded_getitem,
#  192          "_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
#  193          "_unpack_sequence_": Guards.guarded_unpack_sequence,
#  194          "Value": Value,
#~ 195          "_write_": practical_write,
#  196          "__import__": PythonBlockPlugin.safe_import,
#  197          "dict": dict,
#  198          "map": map,
#  199          "filter": filter,
#  200          "enumerate": enumerate,
#  201          "reversed": reversed,


globals = dict({
	"__builtins__": {**safe_builtins, **limited_builtins, **utility_builtins, "__import__": __import__, "dict": dict, "map": map},
   "Value": Value,
   "_getiter_": Eval.default_guarded_getiter,
   "_getitem_": Eval.default_guarded_getitem,
   "_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
   "_unpack_sequence_": Guards.guarded_unpack_sequence,
	"_iter_unpack_sequence": Guards.guarded_iter_unpack_sequence,
   "_unpack_sequence_": Guards.guarded_unpack_sequence,
   "_write_": practical_write,
})
exec(bytecode, globals)
onInput = globals['onInput']
result = onInput([Value(1.0), Value(True)], Context(logger=None, state={}, blockParameters={'param1':None,'param2':None,'param3':None,'param4':None,'param5':None}))

print(str([x.properties for x in result]))


