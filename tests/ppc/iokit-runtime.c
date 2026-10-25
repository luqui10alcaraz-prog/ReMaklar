/* Original IOKit IOMasterPort plus real-kernel capability retrieval.
 * Own caller only. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
int main(void)
{
    mach_port_t master=MACH_PORT_NULL,iterator,framebuffer;
    if(IOMasterPort(MACH_PORT_NULL,&master) || master==MACH_PORT_NULL)return 1;
    if(IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iterator))return 2;
    framebuffer=IOIteratorNext(iterator);if(!framebuffer)return 3;
    if(mach_port_deallocate(mach_task_self(),framebuffer) || mach_port_deallocate(mach_task_self(),iterator) || mach_port_deallocate(mach_task_self(),master))return 4;
    puts("Original IOKit native framebuffer registry OK");return 0;
}
