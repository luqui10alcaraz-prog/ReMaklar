/* Native compiler ABI oracle for the actual EvGlobals bitfield declaration.
 * SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL bits %d %s\n",__LINE__,#x);return 1;}}while(0)
union bits {
 unsigned word;
 struct {unsigned reserved:27,wantPressure:1,wantPrecision:1,dontWantCoalesce:1,dontCoalesce:1,mouseRectValid:1;} fields;
};
int main(void) {
 union bits b;struct rm_field f={0,4,RM_HID_BITS};struct rm_view v;rm_u64 x;int i;
 v.base=(unsigned char *)&b;v.bytes=4;v.fields=&f;v.count=1;v.writable=1;
 for(i=0;i<5;i++) {
  memset(&b,0,sizeof(b));
  switch(i){case 0:b.fields.wantPressure=1;break;case 1:b.fields.wantPrecision=1;break;case 2:b.fields.dontWantCoalesce=1;break;case 3:b.fields.dontCoalesce=1;break;case 4:b.fields.mouseRectValid=1;break;}
  CHECK(!rm_read(&v,0,4,&x) && x==(16U>>i));
  CHECK(!rm_write(&v,0,4,16U>>i));CHECK(b.word==(1U<<(27+i)));
 }
 b.word=0;b.fields.reserved=0x1234567;
 CHECK(!rm_read(&v,0,4,&x) && x==(0x1234567U<<5));
 CHECK(!rm_write(&v,0,4,0x1234567U<<5) && b.fields.reserved==0x1234567);
 puts("native compiler EvGlobals ABI: each of five named flags reflected, reserved27 preserved PASS");return 0;
}
