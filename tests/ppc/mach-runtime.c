/* Stateful IPC/clock contracts, compiled natively and for PPC. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <mach/mach_time.h>
#include <stdio.h>
int main(void)
{
    mach_port_t port,set;
    mach_port_limits_t limits;
    mach_msg_type_number_t count;
    mach_port_urefs_t refs;
    kern_return_t r;
    mach_timebase_info_data_t info;
    unsigned long long before,after;
    if (mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port)) return 1;
    if (mach_port_insert_right(mach_task_self(),port,port,MACH_MSG_TYPE_MAKE_SEND)) return 2;
    if (mach_port_get_refs(mach_task_self(),port,MACH_PORT_RIGHT_SEND,&refs) || refs!=1) return 3;
    limits.mpl_qlimit=1;
    if (mach_port_set_attributes(mach_task_self(),port,MACH_PORT_LIMITS_INFO,(mach_port_info_t)&limits,MACH_PORT_LIMITS_INFO_COUNT)) return 4;
    limits.mpl_qlimit=0;count=MACH_PORT_LIMITS_INFO_COUNT;
    if (mach_port_get_attributes(mach_task_self(),port,MACH_PORT_LIMITS_INFO,(mach_port_info_t)&limits,&count) || limits.mpl_qlimit!=1) return 5;
    limits.mpl_qlimit=MACH_PORT_QLIMIT_MAX+1;
    r=mach_port_set_attributes(mach_task_self(),port,MACH_PORT_LIMITS_INFO,(mach_port_info_t)&limits,MACH_PORT_LIMITS_INFO_COUNT);
    if (r!=KERN_INVALID_VALUE) return 6;
    if (mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_PORT_SET,&set)) return 7;
    if (mach_port_insert_member(mach_task_self(),port,set)) return 8;
    if (mach_port_insert_member(mach_task_self(),port,set)!=KERN_ALREADY_IN_SET) return 9;
    before=mach_absolute_time();
    do { after=mach_absolute_time(); } while(after==before);
    if (after<before || mach_timebase_info(&info) || !info.numer || !info.denom) return 10;
    puts("Mach runtime contracts OK");
    return 0;
}
