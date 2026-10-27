#include <sys/types.h>
#include <sys/sysctl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL kinfo line=%d errno=%d\n",__LINE__,errno);return 1;}}while(0)
int main(void){int mib[4]={CTL_KERN,KERN_PROC,KERN_PROC_PID,0};struct {struct kinfo_proc p;unsigned char tail[32];} out;size_t n;int result,i;
 mib[3]=getpid();n=0;CHECK(!sysctl(mib,4,0,&n,0,0));CHECK(n==6*sizeof(out.p));
 memset(&out,0xa5,sizeof(out));n=sizeof(out.p);CHECK(!sysctl(mib,4,&out.p,&n,0,0));CHECK(n==sizeof(out.p));
 CHECK(out.p.kp_proc.p_pid==getpid());CHECK(out.p.kp_eproc.e_ppid==getppid());CHECK(out.p.kp_eproc.e_pcred.p_ruid==getuid());CHECK(out.p.kp_eproc.e_ucred.cr_uid==geteuid());CHECK(out.p.kp_eproc.e_pcred.p_rgid==getgid());CHECK(out.p.kp_proc.p_comm[0]);
 for(i=0;i<32;i++)CHECK(out.tail[i]==0xa5);
 n=1;errno=0;result=sysctl(mib,4,&out.p,&n,0,0);CHECK(result==-1&&errno==ENOMEM&&n==0);
 mib[3]=200000;n=sizeof(out.p);CHECK(!sysctl(mib,4,&out.p,&n,0,0)&&n==0);
 puts("native KERN_PROC_PID self pid parent credentials length-query missing short-buffer sentinels OK");return 0;}
