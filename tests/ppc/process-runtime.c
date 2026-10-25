/* Original PPC libSystem's fork/dyld hooks plus actual host child lifecycle.
 * Own test, also compiled i386 as an oracle. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <mach/mach.h>
static volatile int cow_value=42;
int main(void)
{
    pid_t parent=getpid(),child,result;
    int status;
    mach_port_t port;
    if(mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port)) return 1;
    child=fork();
    if(child<0) return 2;
    if(!child) {
        cow_value=99;
        if(getpid()==parent || getppid()!=parent) _exit(3);
        if(mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port)) _exit(4);
        if(setsid()!=getpid()) _exit(7);
        errno=0;if(setsid()!=-1 || errno!=EPERM) _exit(8);
        _exit(37);
    }
    result=waitpid(child,&status,0);
    if(result!=child || !WIFEXITED(status) || WEXITSTATUS(status)!=37 || cow_value!=42) return 5;
    errno=0;
    if(waitpid(child,&status,0)!=-1 || errno!=ECHILD) return 6;
    puts("libSystem fork hooks wait COW Mach child setsid OK");
    return 0;
}
