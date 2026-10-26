/* Real kernel map into another process, and physical bidirectional alias. */
#include <mach/mach.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
extern kern_return_t mach_make_memory_entry_64(mach_port_t,unsigned long long *,unsigned long long,vm_prot_t,mach_port_t *,mach_port_t);
extern kern_return_t vm_map_64(mach_port_t,vm_address_t *,vm_size_t,vm_address_t,int,mach_port_t,unsigned long long,boolean_t,vm_prot_t,vm_prot_t,vm_inherit_t);
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL remote line=%d\n",__LINE__);return 1;}}while(0)
int main(void){int to[2],from[2],pid,status,childpid;vm_address_t source=0,view=0;unsigned long long bytes=4096;mach_port_t task=0,entry=0;unsigned value=0;char ready;
 CHECK(!pipe(to) && !pipe(from));pid=fork();CHECK(pid>=0);
 if(!pid){volatile unsigned *p;close(to[1]);close(from[0]);ready='R';if(write(from[1],&ready,1)!=1)_exit(2);if(read(to[0],&view,4)!=4 || !view)_exit(3);p=(volatile unsigned *)view;if(p[0]!=0x13579bdf)_exit(4);p[1]=0x2468ace0;value=p[0];if(write(from[1],&value,4)!=4)_exit(5);_exit(0);}
 close(to[0]);close(from[1]);CHECK(read(from[0],&ready,1)==1 && ready=='R');
 CHECK(!task_for_pid(mach_task_self(),pid,&task));CHECK(!pid_for_task(task,&childpid) && childpid==pid);
 CHECK(!vm_allocate(mach_task_self(),&source,4096,1));((volatile unsigned *)source)[0]=0x13579bdf;
 CHECK(!mach_make_memory_entry_64(mach_task_self(),&bytes,source,3,&entry,0));
 CHECK(!vm_map_64(task,&view,4096,0,1,entry,0,0,3,3,VM_INHERIT_NONE));CHECK(view && view<0xc0000000U);
 CHECK(write(to[1],&view,4)==4);CHECK(read(from[0],&value,4)==4 && value==0x13579bdf);
 CHECK(waitpid(pid,&status,0)==pid && WIFEXITED(status) && WEXITSTATUS(status)==0);
 CHECK(((volatile unsigned *)source)[1]==0x2468ace0);
 CHECK(!mach_port_deallocate(mach_task_self(),task) && !mach_port_deallocate(mach_task_self(),entry) && !vm_deallocate(mach_task_self(),source,4096));
 puts("real remote task classification vm_map64 bidirectional shared bytes OK");return 0;}
