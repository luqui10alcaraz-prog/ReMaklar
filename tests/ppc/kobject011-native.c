#include <mach/mach.h>
#include <stdio.h>
#include <unistd.h>
extern kern_return_t mach_port_kernel_object(mach_port_t,mach_port_t,unsigned *,vm_offset_t *);
int main(void){mach_port_t app;unsigned type=0;vm_offset_t address=0;kern_return_t r;
 r=mach_port_kernel_object(mach_task_self(),mach_task_self(),&type,&address);printf("task query result=%u type=%u\n",r,type);{int pid=-1;kern_return_t kr=pid_for_task(mach_task_self(),&pid);printf("task pid query result=%u pid=%d self=%d\n",kr,pid,getpid());if(kr || pid!=getpid())return 1;}
 if(mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&app))return 2;
 type=99;r=mach_port_kernel_object(mach_task_self(),app,&type,&address);printf("application query result=%u type=%u\n",r,type);{int pid=-1;kern_return_t kr=pid_for_task(app,&pid);printf("application pid query result=%u\n",kr);if(!kr)return 3;}
 return mach_port_destroy(mach_task_self(),app)!=0;}
