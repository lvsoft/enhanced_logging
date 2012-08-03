Enhanced_logging
================

An enhanced version of python logging module:

 - String interpolation supported
 - SmartPrint: redirect from print expression to logging

Usage
=====

String interpolation
--------------------

```
def test_interpolation():
    var1 = 123
    var2 = 'abc'
    var_complex = {'a':1, 2:'c', 3:[1,'a','b','c']}
    log.warn("str:[[var1]], [[var2]]")       # => str:123, abc
    log.warn("repr:{{var1}}, {{var2}}")      # => repr:123, 'abc'
    log.fatal("str with name:[[var1?]], [[var2?]]")      # => str with name:var1:123, var2:abc
    log.critical("repr with name:{{var1?}}, {{var2?}}")  # => repr with name:var1:123, var2:'abc'
    log.warn("complex: {{ var_complex? }}")  # => complex: var_complex:{'a': 1, 2: 'c', 3: [1, 'a', 'b', 'c']}
    log.warn("tee to stdout: [[var2]]", tee_stdout=True)
```

Redirect from print expression
------------------------------

```
@log.SmartPrint
def test_print():
    abc = 1234
    print "hello",
    print 'world',
    print '...'                          # => NOTSET hello world ...
    print "info, this is info {{abc?}}"  # => INFO info, this is info abc:1234
    print "error, this is error"         # => ERROR error, this is error
```

The log level will be guessed according to first printed word.  

String interpolation also works, and you can override default log
level temporarily:

```
@log.SmartPrint(default_level=WARNING)
def test_print2():
    a='local value test'
    d= {1:2,3:None, '5':[7]}
    print "hello2, {{a?}}"              # => WARNING hello2, a:'local value test'
    print "info2, this is info, {{d?}}" # => INFO info2, this is info, d:{1: 2, 3: None, '5': [7]}
    print "error2, this is error"       # => ERROR error2, this is error
```

Known issues
============

SmartPrint will not works in very complex situations:

 - nested function
 - nested ", tee_stdout=True)
 - Python2.x only, never tested on Python 3.x(And SmartPrint will definitely not working in Python3.x)

Example
-------

```
@decoration1
@log.SmartPrint
@decoration2
def func(bla bla bla) ...
```
----------

```
@log.SmartPrint
def func(bla bla bla) ...
    print "This will work"
    def func_nested(bla bla bla)...
        print "This will not"
``` 
 