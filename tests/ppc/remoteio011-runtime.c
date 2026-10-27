/* Real framebuffer object mapped by parent into child's task. */
#include <mach/mach.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
extern kern_return_t io_connect_map_memory(mach_port_t,int,mach_port_t,vm_address_t *,vm_size_t *,int);
extern kern_return_t io_connect_unmap_memory(mach_port_t,int,mach_port_t,vm_address_t);
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL remote IOKit line=%d\n",__LINE__);return 1;}}while(0)
int main(void){int to[2],from[2],pid,status;mach_port_t master=0,iter=0,service=0,conn=0,task=0;vm_address_t local=0,view=0;vm_size_t bytes=0;unsigned saved,value,version;char token='R';
 CHECK(!pipe(to)&&!pipe(from));pid=fork();CHECK(pid>=0);
 if(!pid){volatile unsigned *words;close(to[1]);close(from[0]);
  CHECK(!vm_allocate(mach_task_self(),&view,0x100000,1));CHECK(!vm_deallocate(mach_task_self(),view,0x100000));
  CHECK(write(from[1],&view,4)==4);CHECK(read(to[0],&token,1)==1);words=(volatile unsigned *)view;
  CHECK(words[14]==3);value=words[20];CHECK(value==0x13579bdf);words[20]=0x2468ace0;
  CHECK(write(from[1],&value,4)==4);CHECK(read(to[0],&token,1)==1);_exit(0);
 }
 close(to[0]);close(from[1]);CHECK(read(from[0],&view,4)==4);
 CHECK(!task_for_pid(mach_task_self(),pid,&task));CHECK(!IOMasterPort(0,&master));
 CHECK(!IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iter));
 while((service=IOIteratorNext(iter))){if(!IOServiceOpen(service,mach_task_self(),0,&conn))break;mach_port_deallocate(mach_task_self(),service);}
 CHECK(service&&conn);CHECK(!IOConnectMethodScalarIScalarO(conn,0,3,0,0x00100003,64,64));
 CHECK(!io_connect_map_memory(conn,100,mach_task_self(),&local,&bytes,1));
 version=((volatile unsigned *)local)[14];saved=((volatile unsigned *)local)[20];CHECK(version==3);((volatile unsigned *)local)[20]=0x13579bdf;
 bytes=0;CHECK(!io_connect_map_memory(conn,100,task,&view,&bytes,0));CHECK(bytes==278764);
 CHECK(write(to[1],&token,1)==1);CHECK(read(from[0],&value,4)==4&&value==0x13579bdf);
 CHECK(((volatile unsigned *)local)[20]==0x2468ace0);((volatile unsigned *)local)[20]=saved;
 CHECK(!io_connect_unmap_memory(conn,100,task,view));CHECK(write(to[1],&token,1)==1);
 CHECK(waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0);
 CHECK(!io_connect_unmap_memory(conn,100,mach_task_self(),local));CHECK(!IOServiceClose(conn));
 puts("original IOKit remote task map typed cursor bidirectional physical bytes and remote unmap OK");return 0;}
