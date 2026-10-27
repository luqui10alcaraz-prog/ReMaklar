#include <mach/mach.h>
#include <mach/semaphore.h>
#include <mach/thread_switch.h>
#include <sys/time.h>
#include <pthread.h>
#include <stdio.h>
static semaphore_t ready,go;static volatile mach_port_t target;static volatile unsigned count;
extern boolean_t swtch_pri(int);
static void *worker(void *p){unsigned i;target=mach_thread_self();semaphore_signal(ready);semaphore_wait(go);for(i=0;i<10000;i++)count++;return 0;}
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL thread_switch line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 mach_port_t self=mach_thread_self(),port;pthread_t thread;unsigned i;struct timeval before,after;long elapsed;boolean_t yielded;
 yielded=swtch_pri(0);CHECK(yielded==FALSE||yielded==TRUE);
 CHECK(thread_switch(self,SWITCH_OPTION_NONE,0)==KERN_SUCCESS);
 CHECK(thread_switch(0x7e000011,SWITCH_OPTION_DEPRESS,1)==KERN_SUCCESS);
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port));CHECK(!mach_port_insert_right(mach_task_self(),port,port,MACH_MSG_TYPE_MAKE_SEND));
 CHECK(gettimeofday(&before,0)==0);CHECK(thread_switch(port,SWITCH_OPTION_WAIT,10)==KERN_SUCCESS);CHECK(gettimeofday(&after,0)==0);
 elapsed=(after.tv_sec-before.tv_sec)*1000000+after.tv_usec-before.tv_usec;CHECK(elapsed>=1000);
 CHECK(thread_switch(self,99,0)==KERN_INVALID_ARGUMENT);CHECK(thread_switch(MACH_PORT_NULL,-1,0)==KERN_INVALID_ARGUMENT);
 CHECK(!semaphore_create(mach_task_self(),&ready,0,0)&&!semaphore_create(mach_task_self(),&go,0,0));
 CHECK(!pthread_create(&thread,0,worker,0));CHECK(!semaphore_wait(ready));CHECK(target!=MACH_PORT_NULL);
 CHECK(thread_switch(target,SWITCH_OPTION_DEPRESS,1)==KERN_SUCCESS);CHECK(!semaphore_signal(go));
 for(i=0;i<100;i++)CHECK(thread_switch(target,SWITCH_OPTION_NONE,0)==KERN_SUCCESS);
 CHECK(!pthread_join(thread,0)&&count==10000);CHECK(!semaphore_destroy(mach_task_self(),ready)&&!semaphore_destroy(mach_task_self(),go));CHECK(!mach_port_destroy(mach_task_self(),port));
 puts("real thread_switch: self/worker hints, invalid and non-thread hints, wait timing, invalid options and worker completion PASS");return 0;
}
