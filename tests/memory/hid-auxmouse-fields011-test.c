/* Production selection for native system-defined auxiliary mouse reports.
 * Fixture vectors only; no fabricated GUI events. SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL %d %s\n",__LINE__,#x);return 1;}}while(0)
static unsigned data[5098];
int main(void){
 unsigned slot,entry;unsigned char *base=(unsigned char *)data;struct rm_field f;struct rm_view v;rm_u64 x;
 v.base=base;v.bytes=sizeof(data);v.fields=&f;v.count=1;v.writable=1;
 for(slot=0;slot<240;slot+=239){
  memset(data,0,sizeof(data));entry=232+slot*84;
  *(unsigned *)(base+entry+8)=14;
  *(unsigned short *)(base+entry+36)=0x1234;*(unsigned short *)(base+entry+38)=7;
  *(unsigned *)(base+entry+40)=0x80000005;*(unsigned *)(base+entry+44)=5;
  CHECK(rm_hid_auxmouse_field(base,sizeof(data),entry+36,&f));
  CHECK(!rm_read(&v,entry+36,4,&x) && x==0x12340007);
  CHECK(!rm_read(&v,entry+38,2,&x) && x==7);
  CHECK(rm_hid_auxmouse_field(base,sizeof(data),entry+40,&f));
  CHECK(!rm_read(&v,entry+40,4,&x) && x==0x80000005);
  CHECK(rm_hid_auxmouse_field(base,sizeof(data),entry+44,&f));
  CHECK(!rm_write(&v,entry+44,4,0x55667788));
  CHECK(*(unsigned *)(base+entry+44)==0x55667788);
  *(unsigned short *)(base+entry+38)=8;CHECK(!rm_hid_auxmouse_field(base,sizeof(data),entry+40,&f));
  *(unsigned short *)(base+entry+38)=7;*(unsigned *)(base+entry+8)=15;
  CHECK(!rm_hid_auxmouse_field(base,sizeof(data),entry+40,&f));
 }
 puts("production auxiliary mouse: native type14/subtype7, pair16 header, real numeric button words, RMW and fail-closed other compound variants OK");return 0;
}
