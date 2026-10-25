/* Exercise real exec replacement, including native-loader environment isolation.
 * Own code; compile for PPC and i386. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
int main(int argc,char **argv)
{
    char work[100],pid[32],kept[32],closed[32],cwd[200],data[8]={0};
    int fd,extra;
    char *arguments[7],*environment[]={"REMAKLAR_EXEC_TOKEN=original environment",NULL};
    if(argc==6 && !strcmp(argv[1],"child")) {
        if(strcmp(argv[0],"ReMaklar-exec-probe") || getpid()!=atoi(argv[2]))return 1;
        if(!getenv("REMAKLAR_EXEC_TOKEN") || strcmp(getenv("REMAKLAR_EXEC_TOKEN"),"original environment") || getenv("PATH"))return 2;
        if(!getcwd(cwd,sizeof(cwd)) || strcmp(cwd,argv[5]))return 3;
        fd=atoi(argv[3]);extra=atoi(argv[4]);
        if(read(fd,data,6)!=6 || memcmp(data,"before",6))return 4;
        errno=0;if(fcntl(extra,F_GETFD)!=-1 || errno!=EBADF)return 5;
        if(close(fd) || unlink("data") || chdir("/") || rmdir(argv[5]))return 6;
        puts("exec PID argv env cwd inheritedfd CLOEXEC OK");return 0;
    }
    if(argc!=2)return 10;
    arguments[0]="missing";arguments[1]=NULL;
    errno=0;execve("/remaklar-does-not-exist",arguments,environment);if(errno!=ENOENT)return 11;
    sprintf(work,"/tmp/remaklar-exec-%d",getpid());
    if(mkdir(work,0700) || chdir(work))return 12;
    /* Darwin's /tmp is a symlink to /private/tmp; compare canonical cwd. */
    if(!getcwd(work,sizeof(work)))return 19;
    fd=open("not-executable",O_CREAT|O_EXCL|O_WRONLY,0755);
    if(fd<0 || write(fd,"plain text",10)!=10 || close(fd))return 13;
    errno=0;execve("not-executable",arguments,environment);if(errno!=ENOEXEC)return 14;
    if(unlink("not-executable"))return 15;
    fd=open("data",O_CREAT|O_EXCL|O_RDWR,0600);
    if(fd<0 || write(fd,"before",6)!=6 || lseek(fd,0,SEEK_SET))return 16;
    extra=open("data",O_RDONLY,0);
    if(extra<0 || fcntl(extra,F_SETFD,FD_CLOEXEC))return 17;
    sprintf(pid,"%d",getpid());sprintf(kept,"%d",fd);sprintf(closed,"%d",extra);
    arguments[0]="ReMaklar-exec-probe";arguments[1]="child";arguments[2]=pid;
    arguments[3]=kept;arguments[4]=closed;arguments[5]=work;arguments[6]=NULL;
    execve(argv[1],arguments,environment);
    perror("execve test image");return 18;
}
