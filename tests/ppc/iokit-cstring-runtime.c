/* The MIG c_string reserved offset is not an address. Real i386/PPC oracle.
 * SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <mach/ndr.h>
#include <stdio.h>
#include <string.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
int main(void) {
 struct request {mach_msg_header_t h;NDR_record_t ndr;unsigned int offset,count;char xml[512];} req;
 union {mach_msg_header_t h;char bytes[1024];} reply;
 mach_port_t master=0,local;unsigned int n;int j;mach_msg_return_t kr;
 if(IOMasterPort(0,&master))return 1;
 for(j=0;j<2;j++) {
  memset(&req,0,sizeof(req));strcpy(req.xml,"<dict><key>IOProviderClass</key><string>IOHIDSystem</string></dict>");n=strlen(req.xml)+1;req.count=n;req.offset=j?0x12345678:0;req.ndr=NDR_record;
  local=mach_reply_port();req.h.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,MACH_MSG_TYPE_MAKE_SEND_ONCE);req.h.msgh_size=40+((n+3)&~3);req.h.msgh_remote_port=master;req.h.msgh_local_port=local;req.h.msgh_id=2804;
  memcpy(&reply,&req,req.h.msgh_size);
  kr=mach_msg(&reply.h,MACH_SEND_MSG|MACH_RCV_MSG,req.h.msgh_size,sizeof(reply),local,0,0);
  if(kr){printf("cstring offset=%x mach_error=%u\n",req.offset,kr);return 2;}
  if(!(reply.h.msgh_bits&MACH_MSGH_BITS_COMPLEX)){unsigned int code;memcpy(&code,reply.bytes+32,4);printf("cstring offset=%x kernel_error=%u\n",req.offset,code);return 3;}
  {mach_msg_port_descriptor_t *d=(mach_msg_port_descriptor_t *)(reply.bytes+28);printf("cstring offset=%x real_iterator=%d\n",req.offset,d->name!=0);if(!d->name)return 4;if(mach_port_deallocate(mach_task_self(),d->name))return 5;}
  if(mach_port_destroy(mach_task_self(),local))return 6;
 }
 if(mach_port_deallocate(mach_task_self(),master))return 7;
 puts("IOKit real c_string reserved word accepted OK");return 0;
}
