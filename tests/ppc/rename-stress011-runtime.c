#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL rename stress line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 mach_port_t names[256],port,renamed=0x52000000U;mach_port_type_t type;unsigned round,i;
 union{mach_msg_header_t h;unsigned char b[128];} msg;
 for(round=0;round<2;round++){
  for(i=0;i<256;i++){
   names[i]=0x51000000U+i*256;port=0;
   CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port));
   CHECK(!mach_port_insert_right(mach_task_self(),port,port,MACH_MSG_TYPE_MAKE_SEND));
   CHECK(!mach_port_rename(mach_task_self(),port,names[i]));
   CHECK(mach_port_type(mach_task_self(),port,&type)==KERN_INVALID_NAME);
  }
  for(i=0;i<256;i++)CHECK(!mach_port_type(mach_task_self(),names[i],&type)&&(type&MACH_PORT_TYPE_RECEIVE)&&(type&MACH_PORT_TYPE_SEND));
  CHECK(!mach_port_rename(mach_task_self(),names[255],renamed));names[255]=renamed;
  CHECK(mach_port_rename(mach_task_self(),names[254],renamed)==KERN_NAME_EXISTS);
  memset(&msg,0,sizeof(msg));msg.h.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);msg.h.msgh_remote_port=names[255];msg.h.msgh_size=24;msg.h.msgh_id=7900+round;
  CHECK(!mach_msg(&msg.h,MACH_SEND_MSG,24,0,0,0,0));
  CHECK(!mach_msg(&msg.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(msg),names[255],1000,0));CHECK(msg.h.msgh_id==7900+round);
  for(i=0;i<256;i++){CHECK(!mach_port_destroy(mach_task_self(),names[i]));CHECK(mach_port_type(mach_task_self(),names[i],&type)==KERN_INVALID_NAME);}
 }
 puts("real Mach explicit names: 256 concurrent, high-to-high rename, collision, delivery, destroy and reuse x2 PASS");return 0;
}
