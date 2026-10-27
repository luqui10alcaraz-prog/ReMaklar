/* Preserve actual opaque null-union bytes, refuse unknown active variants.
 * SPDX-License-Identifier: MIT */
#include <typed-live.h>
#include <string.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL null %d\n",__LINE__);return 1;}}while(0)
static unsigned data[5098];
int main(void){unsigned slot,entry,k;unsigned char *base=(unsigned char *)data;struct rm_field f;struct rm_view v;rm_u64 x;
 v.base=base;v.bytes=sizeof(data);v.fields=&f;v.count=1;v.writable=1;
 for(slot=0;slot<240;slot+=239){
  entry=232+slot*84;memset(data,0,sizeof(data));
  for(k=36;k<84;k+=4){CHECK(rm_hid_null_field(base,sizeof(data),entry+k,&f));CHECK(!rm_read(&v,entry+k,4,&x) && x==0);}
  base[entry+36]=0x12;base[entry+37]=0x34;base[entry+38]=0x56;base[entry+39]=0x78;
  base[entry+83]=1;CHECK(rm_hid_null_field(base,sizeof(data),entry+36,&f));
  CHECK(!rm_read(&v,entry+36,4,&x) && x==0x12345678);
  CHECK(!rm_write(&v,entry+36,4,0) && !base[entry+36] && base[entry+83]==1);
  *(unsigned *)(base+entry+8)=15;CHECK(!rm_hid_null_field(base,sizeof(data),entry+36,&f));
 }
 puts("actual type0 bytes preserved, including nonzero consumed data; unknown active types rejected PASS");return 0;}
