/* Real signals through Apple's sigtramp, context and fork/exec semantics.
 * Same source compiled i386 and PPC. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <sys/ucontext.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static volatile sig_atomic_t seen,failed,second;
static void other(int s){if(s==SIGUSR2)second++;else failed=1;}
static void handler(int sig,siginfo_t *info,void *context)
{
    sigset_t mask;
    if(sig!=SIGUSR1)failed=2;
#ifdef __ppc__
    if(info->si_signo!=SIGUSR1 || !context)failed=2;
#endif
    if(sigprocmask(SIG_SETMASK,NULL,&mask) || !sigismember(&mask,SIGUSR1) || !sigismember(&mask,SIGUSR2))failed=3;
    seen++;
    if(kill(getpid(),SIGUSR2) || second)failed=4;
#ifdef __ppc__
    {
        ucontext_t *uc=context;
        if(uc->uc_mcsize!=456 || uc->uc_mcontext->ss.r14!=0x12345678)failed=5;
        uc->uc_mcontext->ss.r14=0x23456789;
        uc->uc_mcontext->fs.fpregs[14]=7.5;
    }
#endif
}
static void simple(int sig){handler(sig,NULL,NULL);}
int main(int argc,char **argv)
{
    struct sigaction a,b;sigset_t mask,pending,old;pid_t pid;int status;
#ifdef __ppc__
    register unsigned long marker __asm__("r14")=0x12345678;
    register double floating __asm__("f14")=1.25;
#endif
    if(argc==2 && !strcmp(argv[1],"--exec-child")) {
        if(sigaction(SIGUSR1,NULL,&a) || a.sa_handler!=SIG_DFL || sigaction(SIGUSR2,NULL,&a) || a.sa_handler!=SIG_IGN)return 40;
        if(sigprocmask(SIG_SETMASK,NULL,&mask) || !sigismember(&mask,SIGUSR2))return 41;
        puts("signal exec caught-reset ignored-mask-preserved OK");return 0;
    }
    memset(&a,0,sizeof(a));a.sa_handler=other;sigemptyset(&a.sa_mask);
    if(sigaction(SIGUSR2,&a,NULL))return 1;
    memset(&a,0,sizeof(a));
#ifdef __ppc__
    a.sa_sigaction=handler;a.sa_flags=SA_SIGINFO|SA_RESTART;
#else
    a.sa_handler=simple;a.sa_flags=SA_RESTART;
#endif
    sigemptyset(&a.sa_mask);sigaddset(&a.sa_mask,SIGUSR2);
    if(sigaction(SIGUSR1,&a,NULL) || sigaction(SIGUSR1,NULL,&b) || b.sa_handler!=a.sa_handler || b.sa_flags!=a.sa_flags || memcmp(&a.sa_mask,&b.sa_mask,sizeof(a.sa_mask)))return 2;
    sigemptyset(&mask);sigaddset(&mask,SIGUSR1);
    if(sigprocmask(SIG_BLOCK,&mask,&old) || kill(getpid(),SIGUSR1) || seen || sigpending(&pending) || !sigismember(&pending,SIGUSR1))return 3;
#ifdef __ppc__
    __asm__ volatile("" : "+r"(marker), "+f"(floating));
#endif
    if(sigprocmask(SIG_UNBLOCK,&mask,NULL))return 4;
#ifdef __ppc__
    __asm__ volatile("" : "+r"(marker), "+f"(floating));
    if(marker!=0x23456789 || floating!=7.5)return 5;
#endif
    if(seen!=1 || second!=1 || failed)return 10+failed;
    /* Caught action survives fork and blocked pending does not. */
    sigemptyset(&mask);sigaddset(&mask,SIGUSR2);if(sigprocmask(SIG_BLOCK,&mask,NULL))return 20;
    if(kill(getpid(),SIGUSR2))return 21;
    pid=fork();if(pid<0)return 22;
    if(!pid) {
        if(sigpending(&pending) || sigismember(&pending,SIGUSR2) || sigaction(SIGUSR1,NULL,&b) || b.sa_handler!=a.sa_handler)_exit(23);
        memset(&a,0,sizeof(a));a.sa_handler=SIG_IGN;sigemptyset(&a.sa_mask);
        if(sigaction(SIGUSR2,&a,NULL))_exit(24);
        if(argc<2)_exit(25);
        execl(argv[1],"signal009","--exec-child",(char *)0);_exit(26);
    }
    if(waitpid(pid,&status,0)!=pid || !WIFEXITED(status) || WEXITSTATUS(status))return 27;
    memset(&a,0,sizeof(a));a.sa_handler=SIG_IGN;sigemptyset(&a.sa_mask);if(sigaction(SIGUSR2,&a,NULL) || sigprocmask(SIG_SETMASK,&old,NULL))return 28;
    errno=0;if(sigaction(SIGKILL,&a,NULL)!=-1 || errno!=EINVAL)return 29;
    #ifdef __ppc__
    puts("signals real masked pending context GPR FPR fork exec sigreturn OK");
#else
    puts("signals real masked pending fork exec legacy sigreturn OK");
#endif
    return 0;
}
