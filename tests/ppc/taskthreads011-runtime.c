#include <mach/mach.h>
#include <mach/semaphore.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
struct state40 {unsigned pc,msr,r[32],cr,xer,lr,ctr,mq,vrsave;};
static volatile unsigned entered;static volatile mach_port_t worker_port;static semaphore_t finish;
static void worker(void){worker_port=mach_thread_self();entered=1;semaphore_wait(finish);thread_terminate(mach_thread_self());}
#ifndef __ppc__
static void *native_worker(void *p){worker();return p;}
#endif
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL task_threads line=%d\n",__LINE__);return 1;}}while(0)
int main(void){thread_act_array_t list=0;mach_msg_type_number_t count=0;mach_port_t self=mach_thread_self(),thread;unsigned i,found_self,found_worker;
 CHECK(!semaphore_create(mach_task_self(),&finish,0,0));
#ifdef __ppc__
 {struct state40 s;vm_address_t stack=0;CHECK(!vm_allocate(mach_task_self(),&stack,65536,1));memset(&s,0,sizeof(s));s.pc=(unsigned)worker;s.r[1]=(stack+65536-64)&~15;CHECK(!thread_create_running(mach_task_self(),1,(thread_state_t)&s,40,&thread));}
#else
 {pthread_t p;CHECK(!pthread_create(&p,0,native_worker,0));}
#endif
 while(!entered){};
 for(i=0;i<2;i++){unsigned j;found_self=found_worker=0;CHECK(!task_threads(mach_task_self(),&list,&count));CHECK(count>=2);for(j=0;j<count;j++){mach_port_type_t type=0;CHECK(!mach_port_type(mach_task_self(),list[j],&type)&&(type&MACH_PORT_TYPE_SEND));if(list[j]==self)found_self=1;if(list[j]==worker_port)found_worker=1;CHECK(!mach_port_deallocate(mach_task_self(),list[j]));}CHECK(found_self&&found_worker);CHECK(!vm_deallocate(mach_task_self(),(vm_address_t)list,count*sizeof(*list)));}
 CHECK(!semaphore_signal(finish));puts("real task_threads current and worker identities repeated OOL rights release OK");return 0;}
