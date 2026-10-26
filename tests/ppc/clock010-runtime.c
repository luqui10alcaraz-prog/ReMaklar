/* Jaguar PPC register-result clock and target byte order. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/time.h>
#include <sys/sysctl.h>
#include <stdio.h>
int main(void) {
 struct timeval first,now;unsigned long calls=0;long elapsed;int order=0,mib[2]={CTL_HW,HW_BYTEORDER};size_t n=sizeof(order);
 if(gettimeofday(&first,0) || first.tv_sec<1000000000 || first.tv_usec<0 || first.tv_usec>=1000000)return 1;
 do{if(gettimeofday(&now,0))return 2;elapsed=(now.tv_sec-first.tv_sec)*1000000+now.tv_usec-first.tv_usec;if(++calls>2000000)return 3;}while(elapsed<10000);
 if(sysctl(mib,2,&order,&n,0,0) || n!=4)return 4;
#ifdef __ppc__
 if(order!=4321)return 5;
#else
 if(order!=1234)return 5;
#endif
 mib[1]=HW_PHYSMEM;n=sizeof(order);if(sysctl(mib,2,&order,&n,0,0) || n!=4 || order<=0)return 6;printf("real physical memory bytes=%d\n",order);
 puts("real advancing clock and architecture byte order OK");return 0;
}
