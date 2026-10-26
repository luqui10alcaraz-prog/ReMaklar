/* Original timer stubs, native expiry messages, absolute clock and cancellation. */
#include <mach/mach.h>
#include <mach/mach_time.h>
extern mach_port_t mk_timer_create(void);
extern kern_return_t mk_timer_destroy(mach_port_t);
extern kern_return_t mk_timer_arm(mach_port_t,unsigned long long);
extern kern_return_t mk_timer_cancel(mach_port_t,unsigned long long *);
typedef struct {
 mach_msg_header_t header;
 unsigned long long time_of_arming,armed_time,time_of_posting;
} rm_timer_expire_msg;
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL timer line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 union {rm_timer_expire_msg event;unsigned char bytes[128];} msg;
 mach_port_t port;uint64_t deadline,armed=0,now;mach_timebase_info_data_t info;
 CHECK(!mach_timebase_info(&info) && info.numer==1 && info.denom==1);
 port=mk_timer_create();CHECK(port);
 now=mach_absolute_time();deadline=now+100000000ULL;
 CHECK(!mk_timer_arm(port,deadline));memset(&msg,0,sizeof(msg));
 CHECK(!mach_msg(&msg.event.header,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(msg),port,3000,0));
 CHECK(msg.event.header.msgh_size==48 && msg.event.armed_time==deadline);
 CHECK(msg.event.time_of_arming<=deadline && msg.event.time_of_posting>=deadline);
 deadline=mach_absolute_time()+1000000000ULL;
 CHECK(!mk_timer_arm(port,deadline));CHECK(!mk_timer_cancel(port,&armed) && armed==deadline);
 deadline=mach_absolute_time()+10000000ULL;CHECK(!mach_wait_until(deadline));CHECK(mach_absolute_time()>=deadline);
 CHECK(!mk_timer_destroy(port));
 puts("native Mach timer expiry64 endian arm cancel absolute wait timebase1/1 OK");return 0;
}
