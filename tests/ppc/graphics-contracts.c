/* Native/PPC oracle of the non-rendering boundaries used by Quartz.
 * SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/sysctl.h>
#include <sys/mman.h>
#include <sys/un.h>
#include <net/if.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    int fd,ip,r,mib[2]={CTL_KERN,KERN_HOSTNAME};
    struct sockaddr_un address;
    struct ifconf conf;
    char interfaces[4096],hostname[256],name[64];
    size_t length=sizeof(hostname);
    fd=socket(AF_UNIX,SOCK_DGRAM,0);if(fd<0) return 1;
    if(fcntl(fd,F_SETFD,FD_CLOEXEC) || fcntl(fd,F_GETFD)!=FD_CLOEXEC) return 2;
    memset(&address,0,sizeof(address));address.sun_family=AF_UNIX;address.sun_len=sizeof(address);
    sprintf(address.sun_path,"/tmp/remaklar-absent-%d",getpid());
    errno=0;r=connect(fd,(struct sockaddr *)&address,sizeof(address));
    if(r!=-1 || errno!=ENOENT) return 3;
    if(close(fd)) return 4;
    errno=0;r=sendto(-1,"x",1,0,NULL,0);if(r!=-1 || errno!=EBADF) return 5;
    ip=socket(AF_INET,SOCK_DGRAM,0);if(ip<0) return 6;
    memset(interfaces,0,sizeof(interfaces));conf.ifc_len=sizeof(interfaces);conf.ifc_buf=interfaces;
    if(ioctl(ip,SIOCGIFCONF,&conf) || conf.ifc_len<0 || conf.ifc_len>sizeof(interfaces)) return 7;
    if(close(ip)) return 8;
    if(sysctl(mib,2,hostname,&length,NULL,0) || length>=sizeof(hostname) || hostname[length] || strlen(hostname)!=length) return 9;
    sprintf(name,"/remaklar-absent-%d",getpid());
    errno=0;r=shm_open(name,O_RDONLY,0);if(r!=-1 || errno!=ENOENT) return 10;
    puts("Graphics boundary contracts OK");return 0;
}
