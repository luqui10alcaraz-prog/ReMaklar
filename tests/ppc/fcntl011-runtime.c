#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL fcntl line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void){char path[128],data[5]={0};int fd,flags;
 sprintf(path,"/tmp/fcntl011-%ld",(long)getpid());fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(fd>=0);flags=fcntl(fd,F_GETFL);CHECK(flags>=0&&(flags&O_ACCMODE)==O_RDWR);CHECK(!(flags&(O_APPEND|O_NONBLOCK)));
 CHECK(write(fd,"abc",3)==3);CHECK(lseek(fd,0,SEEK_SET)==0);CHECK(!fcntl(fd,F_SETFL,flags|O_APPEND|O_NONBLOCK));flags=fcntl(fd,F_GETFL);CHECK((flags&(O_APPEND|O_NONBLOCK|O_ACCMODE))==(O_APPEND|O_NONBLOCK|O_RDWR));CHECK(write(fd,"X",1)==1);CHECK(lseek(fd,0,SEEK_SET)==0);CHECK(read(fd,data,4)==4&&!memcmp(data,"abcX",4));
 CHECK(!fcntl(fd,F_SETFL,flags&~(O_APPEND|O_NONBLOCK)));flags=fcntl(fd,F_GETFL);CHECK(!(flags&(O_APPEND|O_NONBLOCK)));CHECK(!fcntl(fd,F_SETFD,FD_CLOEXEC)&&fcntl(fd,F_GETFD)==FD_CLOEXEC);CHECK(!close(fd));errno=0;CHECK(fcntl(fd,F_GETFL)==-1&&errno==EBADF);CHECK(!unlink(path));puts("real F_GETFL F_SETFL access append nonblock actual file bytes closeexec EBADF OK");return 0;}
