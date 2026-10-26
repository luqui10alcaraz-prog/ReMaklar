/* App message IDs must not select a kernel adapter without capability type. */
#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL capability line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 static const int ids[]={4002,4003,4004,3616,2824,1000,3412,3801,3802,3812,3826};
 union {struct {mach_msg_header_t h;unsigned value;} msg;unsigned char buffer[128];} packet;
 mach_port_t port,name,control;unsigned i;
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port));
 CHECK(!mach_port_insert_right(mach_task_self(),port,port,MACH_MSG_TYPE_MAKE_SEND));
 for(i=0;i<sizeof(ids)/sizeof(ids[0]);i++){
  memset(&packet,0,sizeof(packet));packet.msg.h.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);
  packet.msg.h.msgh_remote_port=port;packet.msg.h.msgh_size=28;packet.msg.h.msgh_id=ids[i];packet.msg.value=0x12345678;
  CHECK(!mach_msg(&packet.msg.h,MACH_SEND_MSG|MACH_RCV_MSG,28,sizeof(packet),port,0,0));
  CHECK(packet.msg.h.msgh_id==ids[i] && packet.msg.value==0x12345678);
 }
 CHECK(!processor_set_default(mach_host_self(),&name));
 CHECK(!host_processor_set_priv(mach_host_self(),name,&control));
 {kern_return_t result=processor_set_policy_enable(control,1);printf("real processor-set policy result=%u\n",result);}
 CHECK(!mach_port_deallocate(mach_task_self(),name) && !mach_port_deallocate(mach_task_self(),control));
 CHECK(!mach_port_destroy(mach_task_self(),port));
 puts("capability provenance: app IDs preserved, real processor-set policy OK");return 0;
}
