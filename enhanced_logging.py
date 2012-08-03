import logging
import re
import sys
import opcode, types
from opcode import opmap

matcher1 = re.compile(r'\[\[\s*(\w+)\??\s*\]\]')
matcher2 = re.compile(r'{{\s*(\w+)\??\s*}}')

def replacer(f):
    def wrap(x):
        varname = x.group()
        vartype = varname[0]
        varname = varname[2:-2].strip()

        if varname.endswith('?'): 
            varname = varname[:-1]
            dump_varname = True
        else:
            dump_varname = False
        
        if varname in f.f_locals:        vobj = f.f_locals[varname]
        elif varname in f.f_globals:     vobj = f.f_globals[varname]
        else: 
            return varname

        if vartype=='[':    strvar = str(vobj)
        elif vartype=='{':  strvar = repr(vobj)

        if dump_varname: strvar = varname+":"+strvar
        return strvar
    return wrap

def generate_arg_str(arg_offset):
   if arg_offset > 65536: 
       raise NotImplementedError("FIXME in future")
   else:
       return chr(arg_offset & 0xFF) + chr(arg_offset >> 16)

class MyLogger(logging.getLoggerClass()):
    def __init__(self, *args, **kwargs):
        self._print_cache=[]
        super(MyLogger, self).__init__(*args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None, frame=None, tee_stdout=None):
        if frame is None:
            frame = sys._getframe().f_back.f_back

        msg = matcher1.sub(replacer(frame), msg)
        msg = matcher2.sub(replacer(frame), msg)

        if tee_stdout:     print msg

        return super(MyLogger, self)._log(level, msg, args, exc_info, extra)

    def SmartPrint(self, *args, **kwargs):
        def wrap(f, frame, default_level=None):
            code = f.func_code.co_code
            codeobj = f.func_code

            lnotab = [ord(x) for x in codeobj.co_lnotab] + [20000, 1] # add a dummy deadline
            nlnotab = lnotab[:]

            ncode = ''
            nconst = list(f.func_code.co_consts)
            last_pos = 0
            n = len(code)
            i = 0
            plnotab = 0
            lnotab_base = 0
            lnotab_deadline = lnotab_base + lnotab[(plnotab+1)*2]
            extended_arg = 0
            while i < n:
                now_pos = i
                c = code[i]
                op = ord(c)
                i = i+1
                if op >= opcode.HAVE_ARGUMENT:
                    oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
                    extended_arg = 0
                    i = i+2
                    if op == opcode.EXTENDED_ARG:
                        extended_arg = oparg*65536L

                if op in [opmap['PRINT_ITEM'], opmap['PRINT_NEWLINE']]:
                    ncode += code[last_pos:now_pos]
                    last_pos = i                    
                    ncode_len1 = len(ncode)
                    delta_adjust = 0


                    # LOAD_CONST _smart_print_helper
                    nconst_offset = len(nconst)
                    ncode += chr(opmap['LOAD_CONST']) + generate_arg_str(nconst_offset)

                    if op == opmap['PRINT_ITEM']:
                        ncode += chr(opmap['ROT_TWO'])

                        # LOAD_CONST level
                        nconst_offset = len(nconst)+1
                        ncode += chr(opmap['LOAD_CONST']) + generate_arg_str(nconst_offset)

                        # ROT_TWO
                        ncode += chr(opmap['ROT_TWO'])
                                            
                        # CALL_FUNCTION 2
                        ncode += chr(opmap['CALL_FUNCTION']) + generate_arg_str(2)
                    else: 
                        nconst_offset = len(nconst)+1
                        ncode += chr(opmap['LOAD_CONST']) + generate_arg_str(nconst_offset)

                        # CALL_FUNCTION 1
                        ncode += chr(opmap['CALL_FUNCTION']) + generate_arg_str(1) # print newline
                    ncode += chr(opmap['POP_TOP'])                    
                    ncode_len2 = len(ncode)

                    nlnotab[(plnotab+1)*2] += ncode_len2-ncode_len1 +delta_adjust
                
                if i>=lnotab_deadline:
                    plnotab+=1
                    lnotab_base = lnotab_deadline
                    lnotab_deadline = lnotab_base + lnotab[(plnotab+1)*2]

            ncode += code[last_pos:]
            nconst.append(self._smart_print_helper)
            nconst.append((default_level, frame))
            nconst = tuple(nconst)
            

            ncodeobj = types.CodeType(codeobj.co_argcount, codeobj.co_nlocals, codeobj.co_stacksize+4,
                                      codeobj.co_flags, ncode, nconst, codeobj.co_names,
                                      codeobj.co_varnames, codeobj.co_filename, codeobj.co_name,
                                      codeobj.co_firstlineno, "".join([chr(x) for x in nlnotab[:-2]]), codeobj.co_freevars,
                                      codeobj.co_cellvars)
                                      
            nfunc = types.FunctionType(ncodeobj, f.func_globals, f.func_name,
                                       f.func_defaults, f.func_closure)

            return nfunc

        frame = sys._getframe().f_back.f_back

        if len(args)==1:
            
            return wrap(args[0], frame)
        else:
            def wrap2(f):
                return wrap(f, frame, kwargs.get('default_level'))
            return wrap2

    def _smart_print_helper(self, level_and_frame, msg=None):
        """
        Msg redirected here from print expression
        """
        if msg is None:
            msg_val = " ".join(self._print_cache)
            self._print_cache=[]
            
            # make a type guess
            for name in logging._levelNames:
                if type(name) is types.StringType:
                    if msg_val.lower().startswith(name.lower()):
                        level = logging._levelNames[name]
                        break
            else:
                level = level_and_frame[0]

            # ensure level set
            if level is None:   # use default level
                level = self.level
            
            frame = level_and_frame[1]
            self._log(level, msg_val, {}, frame=frame)
        else:
            self._print_cache.append(msg)

logging.setLoggerClass(MyLogger)
from logging import *
