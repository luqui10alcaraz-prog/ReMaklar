/* Real Jaguar filesystem limits and kernel scheduler ABI. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <mach/mach.h>
#include <string.h>
int main(void) {
 long a,b;int fd;mach_port_t host;host_sched_info_data_t info;mach_msg_type_number_t count=HOST_SCHED_INFO_COUNT;kern_return_t kr;
 a=pathconf("/usr/lib/libSystem.B.dylib",_PC_NAME_MAX);
 fd=open("/usr/lib/libSystem.B.dylib",O_RDONLY);if(fd<0)return 1;
 b=fpathconf(fd,_PC_NAME_MAX);close(fd);if(a<=0 || a!=b)return 2;
 printf("PATHCONF name_max=%ld\n",a);
 errno=0;if(pathconf("/remaklar-009-missing",_PC_NAME_MAX)!=-1 || errno!=ENOENT)return 3;
 errno=0;if(fpathconf(-1,_PC_NAME_MAX)!=-1 || errno!=EBADF)return 4;
 host=mach_host_self();kr=host_info(host,HOST_SCHED_INFO,(host_info_t)&info,&count);mach_port_deallocate(mach_task_self(),host);
 printf("HOST_SCHED_INFO kr=%u count=%u timeout=%d quantum=%d\n",kr,count,info.min_timeout,info.min_quantum);
 if(kr || count!=2 || info.min_timeout<=0 || info.min_quantum<=0)return 5;
 kr=thread_switch(MACH_PORT_NULL,1,1);printf("THREAD_SWITCH kr=%u\n",kr);if(kr)return 6;
 {mach_msg_header_t message;memset(&message,0,sizeof(message));message.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,MACH_MSG_TYPE_MAKE_SEND_ONCE);message.msgh_size=sizeof(message);message.msgh_remote_port=MACH_PORT_NULL;message.msgh_local_port=mach_reply_port();message.msgh_id=29033;
 kr=mach_msg(&message,MACH_SEND_MSG|MACH_RCV_MSG,sizeof(message),sizeof(message),message.msgh_local_port,0,MACH_PORT_NULL);
 printf("MACH_NULL_DEST kr=%u\n",kr);if(kr!=MACH_SEND_INVALID_DEST)return 7;
}
 puts("pathconf fpathconf native scheduler OK");return 0;
}
