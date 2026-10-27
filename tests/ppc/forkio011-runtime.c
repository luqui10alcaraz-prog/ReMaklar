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
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL IOKit fork line=%d\n",__LINE__);return 1;}}while(0)
int main(void){mach_port_t master=0,iter=0,service=0,conn=0;vm_address_t address[2]={0,0};vm_size_t bytes[2]={0,0};int i,pid,status;
 CHECK(!IOMasterPort(0,&master));CHECK(!IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iter));
 while((service=IOIteratorNext(iter))){if(!IOServiceOpen(service,mach_task_self(),0,&conn))break;mach_port_deallocate(mach_task_self(),service);}CHECK(service&&conn);
 CHECK(!IOConnectMethodScalarIScalarO(conn,0,3,0,0x00100003,64,64));
 for(i=0;i<2;i++){vm_address_t region;vm_size_t length;vm_region_basic_info_data_t info;mach_msg_type_number_t count=VM_REGION_BASIC_INFO_COUNT;mach_port_t object=0;
  CHECK(!io_connect_map_memory(conn,i?110:100,mach_task_self(),&address[i],&bytes[i],1));region=address[i];
  CHECK(!vm_region(mach_task_self(),&region,&length,VM_REGION_BASIC_INFO,(vm_region_info_t)&info,&count,&object));CHECK(region==address[i]&&info.inheritance==VM_INHERIT_NONE);if(object)mach_port_deallocate(mach_task_self(),object);
 }
 pid=fork();CHECK(pid>=0);if(!pid){for(i=0;i<2;i++){vm_address_t region=address[i];vm_size_t length;vm_region_basic_info_data_t info;mach_msg_type_number_t count=VM_REGION_BASIC_INFO_COUNT;mach_port_t object=0;kern_return_t kr=vm_region(mach_task_self(),&region,&length,VM_REGION_BASIC_INFO,(vm_region_info_t)&info,&count,&object);CHECK(kr||region!=address[i]);if(object)mach_port_deallocate(mach_task_self(),object);} _exit(0);}
 CHECK(waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0);CHECK(((volatile unsigned *)address[0])[14]==3);
 for(i=0;i<2;i++)CHECK(!io_connect_unmap_memory(conn,i?110:100,mach_task_self(),address[i]));CHECK(!IOServiceClose(conn));
 puts("original cursor and VRAM VM_INHERIT_NONE absent in real fork child parent remains valid OK");return 0;}
