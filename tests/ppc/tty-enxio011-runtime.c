/* Actual detached-session /dev/tty error, not an invented success.
 * SPDX-License-Identifier: MIT */
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL tty line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void) {
 int fd,i,err;
 fd=open("/dev/null",O_RDWR);CHECK(fd>=0);CHECK(close(fd)==0);
 for(i=0;i<2;i++) {
  errno=0;fd=open("/dev/tty",O_RDWR);err=errno;
  CHECK(fd==-1 && err==ENXIO);printf("real detached tty attempt=%d errno=%d ENXIO\n",i,err);
 }
 puts("real devfs /dev/null succeeds; /dev/tty without controlling terminal preserves native ENXIO PASS");return 0;
}
