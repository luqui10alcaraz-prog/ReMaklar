#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL trailer line=%d\n",__LINE__);return 1;}}while(0)
int main(void) {
 union {mach_msg_header_t h;unsigned char b[256];unsigned words[64];} m;
 mach_port_t p;unsigned i,j,expected;
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&p));
 CHECK(!mach_port_insert_right(mach_task_self(),p,p,MACH_MSG_TYPE_MAKE_SEND));
 for(i=0;i<3;i++) {
  memset(&m,0xa5,sizeof(m));m.h.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);
  m.h.msgh_size=28;m.h.msgh_remote_port=p;m.h.msgh_local_port=0;m.h.msgh_reserved=0;m.h.msgh_id=31000+i;m.words[6]=0x12345678;
  CHECK(!mach_msg(&m.h,MACH_SEND_MSG,28,0,0,0,0));
  memset(&m,0xa5,sizeof(m));
  CHECK(!mach_msg(&m.h,MACH_RCV_MSG|MACH_RCV_TRAILER_ELEMENTS(i),0,sizeof(m),p,0,0));
  expected=i==0?8:(i==1?12:20);
  CHECK(m.h.msgh_size==28 && m.h.msgh_id==31000+i && m.words[6]==0x12345678);
  CHECK(m.words[7]==0 && m.words[8]==expected);
  if(i)CHECK(m.words[9]==i);
  if(i==2)CHECK(m.words[10]==geteuid() && m.words[11]==getegid());
  for(j=28+expected;j<sizeof(m);j++)CHECK(m.b[j]==0xa5);
 }
 CHECK(!mach_port_destroy(mach_task_self(),p));
 puts("real Mach trailers minimum8 sequence12 sender20 endian body and bounds OK");return 0;
}
