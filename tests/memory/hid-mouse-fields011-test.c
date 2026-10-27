/* Real production descriptor access to explicit fixture bytes, no device model.
 * SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL %d %s\n",__LINE__,#x);return 1;}}while(0)
static unsigned data[5098];
int main(void) {
 unsigned slot,type,k,entry;unsigned char *base=(unsigned char *)data;
 struct rm_field f;struct rm_view v;rm_u64 x;
 v.base=base;v.bytes=sizeof(data);v.fields=&f;v.count=1;v.writable=1;
 for(slot=0;slot<240;slot+=239)for(type=1;type<=7;type++) {
  entry=232+84*slot;memset(data,0,sizeof(data));*(unsigned *)(base+entry+8)=type;
  if(type<=4) {
   base[entry+36]=0x12;base[entry+37]=0x34;*(unsigned short *)(base+entry+38)=0x5678;
   *(int *)(base+entry+40)=-3;
   CHECK(rm_hid_mouse_field(base,sizeof(data),entry+36,&f));
   CHECK(!rm_read(&v,entry+36,4,&x) && x==0x12345678);
   CHECK(!rm_read(&v,entry+38,2,&x) && x==0x5678);
   CHECK(!rm_write(&v,entry+36,4,0xabcd1122));
   CHECK(base[entry+36]==0xab && base[entry+37]==0xcd && *(unsigned short *)(base+entry+38)==0x1122);
   CHECK(!rm_write(&v,entry+38,2,0xaabb));
   CHECK(base[entry+36]==0xab && base[entry+37]==0xcd && *(unsigned short *)(base+entry+38)==0xaabb);
   CHECK(!rm_write(&v,entry+36,1,0x11) && base[entry+36]==0x11 && base[entry+37]==0xcd);
   CHECK(rm_hid_mouse_field(base,sizeof(data),entry+40,&f));
   CHECK(!rm_read(&v,entry+40,4,&x) && x==0xfffffffdU);
  } else {
   *(int *)(base+entry+36)=-123;*(int *)(base+entry+40)=456;
   CHECK(rm_hid_mouse_field(base,sizeof(data),entry+36,&f));
   CHECK(!rm_read(&v,entry+36,4,&x) && x==(unsigned)-123);
   CHECK(rm_hid_mouse_field(base,sizeof(data),entry+40,&f));
   CHECK(!rm_read(&v,entry+40,4,&x) && x==456);
  }
  base[entry+44]=0x5a;base[entry+45]=0x11;base[entry+46]=0;base[entry+47]=0x22;
  CHECK(rm_hid_mouse_field(base,sizeof(data),entry+44,&f));
  CHECK(!rm_read(&v,entry+44,4,&x) && x==0x5a110022);
  for(k=52;k<84;k++)base[entry+k]=k;
  CHECK(rm_hid_mouse_field(base,sizeof(data),entry+52,&f));
  CHECK(!rm_read(&v,entry+52,4,&x) && x==0x34353637);
  base[entry+46]=1;
  CHECK(!rm_hid_mouse_field(base,sizeof(data),entry+52,&f));
  CHECK(rm_hid_mouse_field(base,sizeof(data),entry+36,&f));
  *(unsigned *)(base+entry+8)=14;
  CHECK(!rm_hid_mouse_field(base,sizeof(data),entry+36,&f));
 }
 puts("production mouse descriptors: seven types, first/last slot, mixed byte/uint16 prefix, signed deltas, partial RMW, opaque inactive bytes and fail-closed tablet/unknown types OK");return 0;
}
