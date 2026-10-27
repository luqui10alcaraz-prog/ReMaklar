#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL vm_copy line=%d\n",__LINE__);return 1;}}while(0)
int main(void){vm_address_t source=0,dest=0;unsigned char snapshot[8192];unsigned i;kern_return_t code;
 CHECK(!vm_allocate(mach_task_self(),&source,12288,1));CHECK(!vm_allocate(mach_task_self(),&dest,8192,1));
 for(i=0;i<12288;i++)((volatile unsigned char *)source)[i]=(i*37+i/4096)&255;memcpy(snapshot,(void *)source,8192);
 CHECK(!vm_copy(mach_task_self(),source,8192,dest));CHECK(!memcmp((void *)dest,snapshot,8192));((volatile unsigned char *)source)[0]^=255;CHECK(((volatile unsigned char *)dest)[0]==snapshot[0]);((volatile unsigned char *)dest)[1]^=255;CHECK(((volatile unsigned char *)source)[1]==snapshot[1]);
 memcpy(snapshot,(void *)source,8192);code=vm_copy(mach_task_self(),source,8192,source+4096);printf("overlap result=%u\n",code);CHECK(!code&&!memcmp((void *)(source+4096),snapshot,8192));
 CHECK(!vm_protect(mach_task_self(),dest,8192,0,VM_PROT_READ));code=vm_copy(mach_task_self(),source,8192,dest);printf("readonly result=%u\n",code);CHECK(code==KERN_PROTECTION_FAILURE);
 CHECK(!vm_deallocate(mach_task_self(),dest,8192));CHECK(!vm_deallocate(mach_task_self(),source,12288));puts("real kernel vm_copy overlap snapshot COW bidirectional isolation protection OK");return 0;}
