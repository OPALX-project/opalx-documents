import gdb
import json
import os

registered = {}
queries = []
throws = []

def address(register):
    return int(gdb.parse_and_eval(register))

def describe(pointer):
    try:
        symbol = gdb.execute('info symbol 0x%x' % pointer, to_string=True).strip()
    except gdb.error as error:
        symbol = str(error)
    return {'address': hex(pointer), 'module': gdb.solib_name(pointer) or 'executable', 'symbol': symbol}

class Registration(gdb.Breakpoint):
    def stop(self):
        pointer = address('$rsi')
        try:
            name = gdb.parse_and_eval('(char*)$rcx').string()
        except (gdb.error, UnicodeError):
            name = '<unreadable>'
        registered[pointer] = name
        if 'cyclotron_probe' in name and 'ViewCopy' in name:
            item = describe(pointer)
            item['device_name'] = name
            print('REGISTERED_STATE_COPY ' + json.dumps(item))
        return False

class Attributes(gdb.Breakpoint):
    def stop(self):
        pointer = address('$rsi')
        item = describe(pointer)
        item['registered'] = pointer in registered
        item['registration_name'] = registered.get(pointer)
        queries.append(item)
        if 'cyclotron_probe' in item['symbol'] and 'ViewCopy' in item['symbol']:
            print('QUERY_STATE_COPY ' + json.dumps(item))
        return False

class Throw(gdb.Breakpoint):
    def stop(self):
        item = {'last_query': queries[-1] if queries else None,
                'backtrace': gdb.execute('bt 20', to_string=True)}
        throws.append(item)
        print('FIRST_THROW ' + json.dumps(item))
        return True

gdb.execute('set pagination off')
gdb.execute('set confirm off')
gdb.execute('set breakpoint pending on')
Registration('__cudaRegisterFunction')
Attributes('cudaFuncGetAttributes')
Throw('__cxa_throw')
gdb.execute('run')
result = {'registered_count': len(registered), 'queries': queries, 'throws': throws,
          'registered_state_copy': [dict(describe(pointer), device_name=name)
                                    for pointer, name in registered.items()
                                    if 'cyclotron_probe' in name and 'ViewCopy' in name]}
with open(os.environ['PROBE_TRACE_JSON'], 'w') as stream:
    json.dump(result, stream, indent=2)
gdb.execute('quit')
