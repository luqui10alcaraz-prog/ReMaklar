/* XNU ultra-fast TLS trap must permit progress of an atomic retry sequence. */
#include <stdio.h>
static volatile unsigned word;
int main(void)
{
 unsigned i,cr=0;
 for(i=0;i<1000;i++){
  register volatile unsigned *address __asm__("r6")=&word;
  register unsigned value __asm__("r7")=1;
  __asm__ __volatile__("lwarx r8,0,r6\n\tli r0,32754\n\tsc\n\tstwcx. r7,0,r6\n\tmfcr %0"
   : "=r"(cr) : "r"(address),"r"(value) : "r0","r3","r8","cr0","memory");
  if(cr&0x20000000)break;
 }
 if(i==1000 || word!=1){fprintf(stderr,"FAIL fast trap atomic retries=%u\n",i);return 1;}
 puts("ultra-fast TLS trap atomic retry progress OK");return 0;
}
