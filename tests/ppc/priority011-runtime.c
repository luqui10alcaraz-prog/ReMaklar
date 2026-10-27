#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL priority line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void){int before,pid,status,value;errno=0;before=getpriority(PRIO_PROCESS,0);CHECK(!errno);pid=fork();CHECK(pid>=0);
 if(!pid){CHECK(!setpriority(PRIO_PROCESS,0,10));errno=0;value=getpriority(PRIO_PROCESS,0);CHECK(value==10&&!errno);CHECK(!setpriority(PRIO_PROCESS,0,-1));errno=0;value=getpriority(PRIO_PROCESS,0);CHECK(value==-1&&!errno);CHECK(!setpriority(PRIO_PROCESS,0,20));errno=0;value=getpriority(PRIO_PROCESS,0);CHECK(value==20&&!errno);errno=0;CHECK(setpriority(99,0,0)==-1&&errno==EINVAL);errno=0;CHECK(setpriority(PRIO_PROCESS,200000,0)==-1&&errno==ESRCH);_exit(0);}
 CHECK(waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0);errno=0;CHECK(getpriority(PRIO_PROCESS,0)==before&&!errno);puts("real Darwin priority child nice10 negative1 nice20 errors parent unchanged OK");return 0;}
