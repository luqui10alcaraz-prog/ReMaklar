/* Production descriptor selection and endian access; fixture data only.
 * SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL %d %s\n",__LINE__,#x);return 1;}}while(0)
static unsigned data[5098];
int main(void) {
 unsigned slots[]={0,1,239},types[]={10,11,12},i,j,k;struct rm_field dummy;
 unsigned char *base=(unsigned char *)data;
 for(i=0;i<3;i++)for(j=0;j<3;j++) {
  unsigned entry=232+slots[i]*84;struct rm_field f;struct rm_view view;rm_u64 value;
  memset(data,0,sizeof(data));*(unsigned *)(base+entry+8)=types[j];
  *(unsigned short *)(base+entry+36)=0x1122;
  *(unsigned short *)(base+entry+38)=0xfffe;
  *(unsigned short *)(base+entry+40)=0x3344;
  *(unsigned short *)(base+entry+42)=0x5566;
  *(unsigned short *)(base+entry+44)=0x7788;
  *(unsigned short *)(base+entry+46)=0x99aa;
  for(k=48;k<84;k+=4)*(unsigned *)(base+entry+k)=0x12345600+k;
  view.base=base;view.bytes=sizeof(data);view.fields=&f;view.count=1;view.writable=1;
  CHECK(rm_hid_key_field(base,sizeof(data),entry+36,&f) && f.size==2);
  CHECK(!rm_read(&view,entry+36,2,&value) && value==0x1122);
  CHECK(!rm_read(&view,entry+36,1,&value) && value==0x11);
  CHECK(!rm_read(&view,entry+37,1,&value) && value==0x22);
  CHECK(rm_hid_key_field(base,sizeof(data),entry+38,&f));
  CHECK(!rm_read(&view,entry+38,2,&value) && value==0xfffe);
  CHECK(rm_hid_key_field(base,sizeof(data),entry+52,&f) && f.size==4);
  CHECK(!rm_read(&view,entry+52,4,&value) && value==0x12345634);
  CHECK(rm_hid_key_field(base,sizeof(data),entry+80,&f));
  CHECK(!rm_read(&view,entry+80,4,&value) && value==0x12345650);
  CHECK(!rm_write(&view,entry+80,4,0xaabbccdd));
  CHECK(*(unsigned *)(base+entry+80)==0xaabbccdd);
  CHECK(!rm_hid_key_field(base,sizeof(data),entry+35,&f));
  *(unsigned *)(base+entry+8)=5;
  CHECK(!rm_hid_key_field(base,sizeof(data),entry+36,&f));
  *(unsigned *)(base+entry+8)=0x12345678;
  CHECK(!rm_hid_key_field(base,sizeof(data),entry+36,&f));
 }
 CHECK(!rm_hid_key_field(base,sizeof(data),sizeof(data),&dummy));
 puts("real production HID key descriptors: 3 event types x first/second/last slot, signed shorts, bytes, native words, writes and fail-closed unknown types OK");return 0;
}
