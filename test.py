from enhanced_logging import getLogger, StreamHandler, Formatter, WARNING

log = getLogger('a')
console = StreamHandler()
log.addHandler(console)
formatter = Formatter('%(asctime)s %(levelname)s %(message)s')
console.setFormatter(formatter)

def test_interpolation():
    var1 = 123
    var2 = 'abc'
    var_complex = {'a':1, 2:'c', 3:[1,'a','b','c']}
    log.warn("str:[[var1]], [[var2]]")
    log.warn("repr:{{var1}}, {{var2}}")
    log.fatal("str with name:[[var1?]], [[var2?]]")
    log.critical("repr with name:{{var1?}}, {{var2?}}")
    log.warn("complex: {{ var_complex? }}")
    log.warn("tee to stdout: [[var2]]", tee_stdout=True)

@log.SmartPrint
def test_print():
    abc = 1234
    print "hello",
    print 'world',
    print '...'
    print "info, this is info {{abc?}}"
    print "error, this is error"

@log.SmartPrint(default_level=WARNING)
def test_print2():
    a='local value test'
    d= {1:2,3:None, '5':[7]}

    print "hello2, {{a?}}"
    print "info2, this is info, {{d?}}"
    print "error2, this is error"


test_interpolation()
test_print()
test_print2()