from multiprocessing import Process
import os,time

# 子进程要执行的代码
def run_proc(name,t):
    while True:
        print('Run child process %s (%s)...' % (name, os.getpid()))
        time.sleep(t)

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',1))
    p.start()
    t = Process(target=run_proc, args=('pppp', 1))
    t.start()
    print('Child process end.')