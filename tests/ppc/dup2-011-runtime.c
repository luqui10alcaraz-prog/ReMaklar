/* Actual kernel descriptor duplication and stdio redirection oracle.
 * SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL dup2 line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void) {
 char path[256],c;int a,b,channel[2],saved;
 setbuf(stdout,0);sprintf(path,"/var/tmp/jaguar/.dup2-011-%d",getpid());
 a=open(path,O_RDWR|O_CREAT|O_EXCL,0600);CHECK(a>=0);
 CHECK(write(a,"abc",3)==3 && lseek(a,0,SEEK_SET)==0);
 b=open(path,O_RDONLY);CHECK(b>=0);
 CHECK(fcntl(a,F_SETFD,FD_CLOEXEC)==0 && fcntl(b,F_SETFD,FD_CLOEXEC)==0);
 CHECK(dup2(a,a)==a && fcntl(a,F_GETFD)==FD_CLOEXEC);
 CHECK(dup2(a,b)==b && fcntl(b,F_GETFD)==0 && fcntl(a,F_GETFD)==FD_CLOEXEC);
 CHECK(read(a,&c,1)==1 && c=='a');CHECK(read(b,&c,1)==1 && c=='b');
 errno=0;CHECK(dup2(-1,b)==-1 && errno==EBADF);
 CHECK(read(b,&c,1)==1 && c=='c');
 errno=0;CHECK(dup2(a,-1)==-1 && errno==EBADF);
 CHECK(close(a)==0 && write(b,"d",1)==1 && close(b)==0);
 CHECK(pipe(channel)==0);
 CHECK(dup2(1,70)==70 && dup2(2,71)==71);
 CHECK(dup2(channel[1],1)==1 && write(1,"P",1)==1);
 CHECK(read(channel[0],&c,1)==1 && c=='P');CHECK(dup2(70,1)==1);
 CHECK(dup2(channel[1],2)==2 && write(2,"E",1)==1);
 CHECK(read(channel[0],&c,1)==1 && c=='E');CHECK(dup2(71,2)==2);
 CHECK(dup2(channel[0],0)==0 && write(channel[1],"I",1)==1);
 CHECK(read(0,&c,1)==1 && c=='I');
 CHECK(close(70)==0 && close(71)==0 && close(channel[0])==0 && close(channel[1])==0);
 CHECK(unlink(path)==0);
 puts("real dup2: replaced target, shared offset/status, CLOEXEC clear/self preserve, EBADF without target damage, closed source and stdin/stdout/stderr redirection PASS");return 0;
}
