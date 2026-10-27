#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL OOL line=%d\n",__LINE__);return 1;}}while(0)
struct message {mach_msg_header_t h;mach_msg_body_t body;mach_msg_ool_descriptor_t ool;};
int main(void){mach_port_t port=0;int iteration,j;CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port));CHECK(!mach_port_insert_right(mach_task_self(),port,port,MACH_MSG_TYPE_MAKE_SEND));
 for(iteration=0;iteration<2;iteration++){vm_address_t source=0;struct message send;union {struct message m;unsigned char bytes[128];} receive;volatile unsigned char *p;
  CHECK(!vm_allocate(mach_task_self(),&source,4096,1));p=(volatile unsigned char *)source;for(j=0;j<4096;j++)p[j]=(j*37+iteration)&255;
  memset(&send,0,sizeof(send));send.h.msgh_bits=MACH_MSGH_BITS_COMPLEX|MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);send.h.msgh_size=sizeof(send);send.h.msgh_remote_port=port;send.h.msgh_id=6100+iteration;send.body.msgh_descriptor_count=1;send.ool.address=(void *)source;send.ool.size=4096;send.ool.type=MACH_MSG_OOL_DESCRIPTOR;send.ool.copy=MACH_MSG_VIRTUAL_COPY;send.ool.deallocate=iteration;
  CHECK(!mach_msg(&send.h,MACH_SEND_MSG,sizeof(send),0,0,0,0));
  if(iteration){vm_address_t region=source;vm_size_t size;vm_region_basic_info_data_t info;mach_msg_type_number_t count=VM_REGION_BASIC_INFO_COUNT;mach_port_t object=0;kern_return_t kr=vm_region(mach_task_self(),&region,&size,VM_REGION_BASIC_INFO,(vm_region_info_t)&info,&count,&object);CHECK(kr||region!=source);if(object)mach_port_deallocate(mach_task_self(),object);}
  memset(&receive,0,sizeof(receive));CHECK(!mach_msg(&receive.m.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(receive),port,1000,0));CHECK(receive.m.h.msgh_id==6100+iteration&&receive.m.ool.size==4096&&receive.m.ool.type==MACH_MSG_OOL_DESCRIPTOR);p=receive.m.ool.address;for(j=0;j<4096;j++)CHECK(p[j]==((j*37+iteration)&255));
  CHECK(!vm_deallocate(mach_task_self(),(vm_address_t)receive.m.ool.address,4096));if(!iteration)CHECK(!vm_deallocate(mach_task_self(),source,4096));
 }
 CHECK(!mach_port_destroy(mach_task_self(),port));puts("real Mach application OOL bytes descriptor conversion copy deallocate receive unmap OK");return 0;}
