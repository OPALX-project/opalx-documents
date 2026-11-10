import gdb

gdb.execute('set pagination off')
gdb.execute('set confirm off')
gdb.execute('set breakpoint pending on')

class FirstThrow(gdb.Breakpoint):
    def stop(self):
        gdb.write('\nPROBE_MPI_FIRST_THROW\n')
        for command in ['p/x $rdi', 'info symbol $rsi', 'x/s *(char**)($rdi+8)', 'bt 40']:
            try:
                gdb.execute(command)
            except gdb.error as error:
                gdb.write(str(error) + '\n')
        return True

FirstThrow('__cxa_throw')
gdb.execute('run')
gdb.execute('quit 0')
