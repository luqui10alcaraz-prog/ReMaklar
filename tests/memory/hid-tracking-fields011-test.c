/* Production descriptor against native compiler tracking fields. SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL tracking %d\n",__LINE__);return 1;}}while(0)
static unsigned data[5098];
int main(void){
 unsigned slot,type,entry;unsigned char *base=(unsigned char *)data;
 struct rm_field f;struct rm_view v;rm_u64 x;
 v.base=base;v.bytes=sizeof(data);v.fields=&f;v.count=1;v.writable=1;
 for(slot=0;slot<240;slot+=239)for(type=8;type<=9;type++){
  entry=232+slot*84;memset(data,0,sizeof(data));*(unsigned *)(base+entry+8)=type;
  *(unsigned short *)(base+entry+36)=0x1122;*(unsigned short *)(base+entry+38)=0x3344;
  *(int *)(base+entry+40)=-42;
  CHECK(rm_hid_tracking_field(base,sizeof(data),entry+36,&f));
  CHECK(!rm_read(&v,entry+36,4,&x) && x==0x11223344);
  CHECK(!rm_write(&v,entry+38,2,0xaabb) && *(unsigned short *)(base+entry+38)==0xaabb);
  CHECK(rm_hid_tracking_field(base,sizeof(data),entry+40,&f));
  CHECK(!rm_read(&v,entry+40,4,&x) && x==(unsigned)-42);
  *(unsigned *)(base+entry+8)=14;CHECK(!rm_hid_tracking_field(base,sizeof(data),entry+40,&f));
 }
 puts("native tracking type8/9 pair16 header, signed tracking number, real reserved bytes, first/last slots PASS");return 0;
}
