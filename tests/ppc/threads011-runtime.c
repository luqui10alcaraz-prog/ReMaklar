/* Real Mach-created PPC threads, original user stubs and native kernel queues. */
#include <mach/mach.h>
#include <mach/semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
extern int IOTrySpinLock(volatile int *);
extern void IOSpinUnlock(volatile int *);
struct state40 {unsigned pc,msr,r[32],cr,xer,lr,ctr,mq,vrsave;};
union Message {mach_msg_header_t h;unsigned char buffer[128];};
static volatile unsigned lock,count,entered,waiting,reading;
static mach_port_t parent_port,worker_port;
static semaphore_t sem;
static int channel[2];
static void worker(void)
{
 union Message packet;mach_msg_header_t *msg=&packet.h;unsigned i;
 ++entered;
 memset(msg,0,sizeof(packet));msg->msgh_local_port=worker_port;
 if(mach_msg(msg,MACH_RCV_MSG,0,sizeof(packet),worker_port,0,0))abort();
 waiting=1;if(semaphore_wait(sem))abort();
 {char token;reading=1;if(read(channel[0],&token,1)!=1 || token!='x')abort();}
 for(i=0;i<20000;i++){
  while(!IOTrySpinLock((volatile int *)&lock)){}
  ++count;IOSpinUnlock((volatile int *)&lock);
 }
 memset(msg,0,sizeof(packet));msg->msgh_bits=MACH_MSGH_BITS(19,0);msg->msgh_remote_port=parent_port;msg->msgh_size=sizeof(*msg);msg->msgh_id=42;
 if(mach_msg(msg,MACH_SEND_MSG,sizeof(*msg),0,0,0,0))abort();
 thread_terminate(mach_thread_self());abort();
}
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL thread line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 struct state40 s;vm_address_t stack=0;mach_port_t thread;union Message packet;mach_msg_header_t *msg=&packet.h;unsigned i;
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&parent_port));
 CHECK(!mach_port_insert_right(mach_task_self(),parent_port,parent_port,MACH_MSG_TYPE_MAKE_SEND));
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&worker_port));
 CHECK(!mach_port_insert_right(mach_task_self(),worker_port,worker_port,MACH_MSG_TYPE_MAKE_SEND));
 CHECK(!pipe(channel));
 CHECK(!semaphore_create(mach_task_self(),&sem,0,0));
 CHECK(!vm_allocate(mach_task_self(),&stack,65536,1));
 memset(&s,0,sizeof(s));s.pc=(unsigned)worker;s.r[1]=(stack+65536-64)&~15;
 CHECK(!thread_create_running(mach_task_self(),1,(thread_state_t)&s,40,&thread));
 while(!entered){} /* Requires preemption of a PPC spin, without syscalls. */
 memset(msg,0,sizeof(packet));msg->msgh_bits=MACH_MSGH_BITS(19,0);msg->msgh_remote_port=worker_port;msg->msgh_size=sizeof(*msg);
 CHECK(!mach_msg(msg,MACH_SEND_MSG,sizeof(*msg),0,0,0,0));
 while(!waiting){}
 CHECK(!semaphore_signal(sem));
 while(!reading){}
 CHECK(write(channel[1],"x",1)==1);
 for(i=0;i<20000;i++){
  while(!IOTrySpinLock((volatile int *)&lock)){}
  ++count;IOSpinUnlock((volatile int *)&lock);
 }
 CHECK(!mach_msg(msg,MACH_RCV_MSG,0,sizeof(packet),parent_port,0,0));
 CHECK(msg->msgh_id==42 && count==40000);
 {mach_timespec_t zero;zero.tv_sec=zero.tv_nsec=0;CHECK(semaphore_timedwait(sem,zero)==KERN_OPERATION_TIMED_OUT);}
 CHECK(!semaphore_destroy(mach_task_self(),sem));
 CHECK(!close(channel[0]) && !close(channel[1]));
 printf("real PPC threads spin preemption kernel Mach wait semaphore timedwait pipe shared-lock count=%u OK\n",count);
 return 0;
}
