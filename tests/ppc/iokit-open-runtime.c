/* Real IOPMrootDomain user client, native oracle and PPC caller. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern mach_port_t IORegistryEntryFromPath(mach_port_t,const char *);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
int main(void) {
    mach_port_t master=0,service=0,connection=0,bad=0;kern_return_t kr;unsigned int value=0;
    if(IOMasterPort(0,&master))return 1;
    service=IORegistryEntryFromPath(master,"IOPower:/IOPowerConnection/IOPMrootDomain");if(!service)return 2;
    kr=IOServiceOpen(service,mach_task_self(),0,&connection);
    printf("IOServiceOpen type=0 result=%u nonnull=%d\n",kr,connection!=0);
    if(kr || !connection)return 3;
    kr=IOConnectMethodScalarIScalarO(connection,1,1,1,0,&value);
    printf("GetAggressiveness result=%u value=%u\n",kr,value);if(kr)return 7;
    kr=IOConnectMethodScalarIScalarO(connection,0x7fffffff,0,0);
    printf("Invalid selector result=%u\n",kr);if(!kr)return 8;
    kr=IOServiceClose(connection);printf("IOServiceClose result=%u\n",kr);if(kr)return 4;
    kr=IOServiceOpen(service,mach_task_self(),0x7fffffff,&bad);
    printf("IOServiceOpen unusual-type result=%u nonnull=%d\n",kr,bad!=0);
    if(!kr && IOServiceClose(bad))return 5;
    bad=0;kr=IOServiceOpen(master,mach_task_self(),0,&bad);
    printf("IOServiceOpen wrong-service result=%u nonnull=%d\n",kr,bad!=0);if(!kr)return 9;
    if(mach_port_deallocate(mach_task_self(),service) || mach_port_deallocate(mach_task_self(),master))return 6;
    puts("IOKit original real open close scalar negative OK");return 0;
}
