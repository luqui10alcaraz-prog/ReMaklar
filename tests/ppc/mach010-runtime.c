/* Real Mach queues, port-set membership, rights, shared memory and bootstrap.
 * One source, i386 oracle and original PPC libSystem caller. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern mach_port_t bootstrap_port;
extern kern_return_t bootstrap_register(mach_port_t,const char *,mach_port_t);
extern kern_return_t bootstrap_look_up(mach_port_t,const char *,mach_port_t *);
extern kern_return_t mach_make_memory_entry_64(mach_port_t,unsigned long long *,unsigned long long,vm_prot_t,mach_port_t *,mach_port_t);
#define CHECK(x) do { if(!(x)){printf("FAIL line=%d condition=%s\n",__LINE__,#x);return __LINE__;} } while(0)
struct message {mach_msg_header_t h;unsigned int value;unsigned char trailer[128];};
static kern_return_t send_value(mach_port_t destination,mach_port_t reply,unsigned int disposition,unsigned int value)
{
 struct message m;memset(&m,0,sizeof(m));m.h.msgh_bits=MACH_MSGH_BITS(disposition,reply?MACH_MSG_TYPE_MAKE_SEND_ONCE:0);m.h.msgh_remote_port=destination;m.h.msgh_local_port=reply;m.h.msgh_size=28;m.h.msgh_id=0x5250;m.value=value;
 return mach_msg(&m.h,MACH_SEND_MSG|MACH_SEND_TIMEOUT,28,0,0,1000,0);
}
static kern_return_t receive_value(mach_port_t name,struct message *m)
{
 memset(m,0,sizeof(*m));return mach_msg(&m->h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(*m),name,30000,0);
}
static volatile sig_atomic_t signal_seen,signal_error;
static mach_port_t signal_reply;
static void ipc_signal(int s){if(s!=SIGUSR1 || !signal_reply || send_value(signal_reply,0,MACH_MSG_TYPE_MOVE_SEND_ONCE,0x1234abcd))signal_error=1;signal_seen++;}
static void pause_for_receiver(void){struct timeval start,now;long elapsed;gettimeofday(&start,0);do{gettimeofday(&now,0);elapsed=(now.tv_sec-start.tv_sec)*1000000+now.tv_usec-start.tv_usec;}while(elapsed<200000);}
int main(int argc,char **argv)
{
 mach_port_t task=mach_task_self(),p=0,q=0,a=0,b=0,entry=0,ro=0,service=0;struct message m;
 kern_return_t kr;vm_address_t original=0,alias=0,readonly=0;unsigned long long bytes;pid_t child;int status;char name[128],right[32];
 if(argc==4 && !strcmp(argv[1],"--child")) {
  q=strtoul(argv[3],0,10);
  {mach_port_urefs_t refs=0;CHECK(mach_port_get_refs(task,q,MACH_PORT_RIGHT_RECEIVE,&refs)==KERN_INVALID_NAME);CHECK(!mach_port_allocate(task,MACH_PORT_RIGHT_RECEIVE,&q));}
  CHECK(!bootstrap_look_up(bootstrap_port,argv[2],&service));
  CHECK(!send_value(service,q,MACH_MSG_TYPE_COPY_SEND,0xabcdef12));
  pause_for_receiver();CHECK(!kill(getppid(),SIGUSR1));CHECK(!receive_value(q,&m) && m.value==0x1234abcd);CHECK(!send_value(service,0,MACH_MSG_TYPE_COPY_SEND,0x98765432));
  CHECK(!mach_port_deallocate(task,service));CHECK(!mach_port_destroy(task,q));
  puts("Mach child exec clears ordinary rights, bootstrap IPC reply OK");return 0;
 }
 CHECK(!mach_port_allocate(task,MACH_PORT_RIGHT_RECEIVE,&p));
 CHECK(!mach_port_allocate(task,MACH_PORT_RIGHT_PORT_SET,&a));CHECK(!mach_port_allocate(task,MACH_PORT_RIGHT_PORT_SET,&b));
 CHECK(!mach_port_insert_right(task,p,p,MACH_MSG_TYPE_MAKE_SEND));
 CHECK(!mach_port_insert_member(task,p,a));CHECK(!mach_port_insert_member(task,p,b));
 CHECK(mach_port_insert_member(task,p,a)==KERN_ALREADY_IN_SET);
 CHECK(!send_value(p,0,MACH_MSG_TYPE_COPY_SEND,11));CHECK(!receive_value(a,&m) && m.value==11 && m.h.msgh_local_port==p);
 CHECK(!send_value(p,0,MACH_MSG_TYPE_COPY_SEND,22));CHECK(!receive_value(b,&m) && m.value==22);
 CHECK(!mach_port_extract_member(task,p,a));CHECK(mach_port_extract_member(task,p,a)==KERN_NOT_IN_SET);
 CHECK(!send_value(p,0,MACH_MSG_TYPE_COPY_SEND,33));
 kr=mach_msg(&m.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(m),a,1,0);CHECK(kr==MACH_RCV_TIMED_OUT);
 CHECK(!receive_value(b,&m) && m.value==33);
 {mach_port_name_array_t members;mach_msg_type_number_t count=0;CHECK(!mach_port_get_set_status(task,b,&members,&count) && count==1 && members[0]==p);vm_deallocate(task,(vm_address_t)members,count*sizeof(*members));}
 puts("Mach real multi-set send receive duplicate extract timeout status OK");
 CHECK(!mach_port_allocate(task,MACH_PORT_RIGHT_RECEIVE,&q));
 {
  struct transfer {mach_msg_header_t h;mach_msg_body_t body;mach_msg_port_descriptor_t port;unsigned char trailer[128];} t;
  memset(&t,0,sizeof(t));t.h.msgh_bits=MACH_MSGH_BITS_COMPLEX|MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);t.h.msgh_remote_port=p;t.h.msgh_size=40;t.h.msgh_id=0x5251;t.body.msgh_descriptor_count=1;t.port.name=q;t.port.disposition=MACH_MSG_TYPE_MAKE_SEND;t.port.type=MACH_MSG_PORT_DESCRIPTOR;
  CHECK(!mach_msg(&t.h,MACH_SEND_MSG,40,0,0,0,0));
  CHECK(!mach_msg(&t.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(t),b,1000,0));CHECK(t.port.name==q && t.port.disposition==MACH_MSG_TYPE_PORT_SEND);
  CHECK(!send_value(t.port.name,0,MACH_MSG_TYPE_COPY_SEND,44));CHECK(!receive_value(q,&m) && m.value==44);
  CHECK(!mach_port_deallocate(task,t.port.name));
 }
 CHECK(!mach_port_destroy(task,q));puts("Mach real transferred send right and release OK");
 CHECK(!vm_allocate(task,&original,8192,1));CHECK(!vm_msync(task,original,8192,2));CHECK(vm_msync(task,original,8192,3)==KERN_INVALID_ARGUMENT);((unsigned int *)original)[1024]=0x11223344;
 bytes=8192;CHECK(!mach_make_memory_entry_64(task,&bytes,original,VM_PROT_READ|VM_PROT_WRITE,&entry,0) && entry && bytes==8192);
 CHECK(!vm_map(task,&alias,4096,0,1,entry,4096,0,VM_PROT_READ|VM_PROT_WRITE,VM_PROT_READ|VM_PROT_WRITE,VM_INHERIT_SHARE));
 CHECK(*(unsigned int *)alias==0x11223344);*(unsigned int *)alias=0x55667788;CHECK(((unsigned int *)original)[1024]==0x55667788);
 ((unsigned int *)original)[1024]=0x778899aa;CHECK(*(unsigned int *)alias==0x778899aa);
 bytes=4096;CHECK(!mach_make_memory_entry_64(task,&bytes,original+4096,VM_PROT_READ,&ro,0));
 kr=vm_map(task,&readonly,4096,0,1,ro,0,0,VM_PROT_READ|VM_PROT_WRITE,VM_PROT_READ|VM_PROT_WRITE,VM_INHERIT_NONE);printf("read-only entry RW map kr=%u\n",kr);CHECK(kr==KERN_INVALID_RIGHT);
 readonly=0;CHECK(!vm_map(task,&readonly,4096,0,1,ro,0,0,VM_PROT_READ,VM_PROT_READ,VM_INHERIT_NONE));CHECK(*(unsigned int *)readonly==0x778899aa);CHECK(vm_protect(task,readonly,4096,0,VM_PROT_READ|VM_PROT_WRITE)==KERN_PROTECTION_FAILURE);
 CHECK(!mach_port_deallocate(task,entry));CHECK(!mach_port_deallocate(task,ro));
 *(unsigned int *)alias=0xaabbccdd;CHECK(*(unsigned int *)readonly==0xaabbccdd && ((unsigned int *)original)[1024]==0xaabbccdd);
 CHECK(!vm_deallocate(task,readonly,4096));CHECK(!vm_deallocate(task,alias,4096));CHECK(!vm_deallocate(task,original,8192));
 puts("Mach real memory entry shared aliases offsets protection lifetime OK");
 CHECK(argc==2);sprintf(name,"org.remaklar.mach010.%ld",(long)getpid());
 CHECK(!bootstrap_register(bootstrap_port,name,p));
 CHECK(signal(SIGUSR1,ipc_signal)!=SIG_ERR);child=fork();CHECK(child>=0);
 if(!child){CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&q));sprintf(right,"%u",q);execl(argv[1],"mach010","--child",name,right,(char *)0);_exit(99);}
 CHECK(!receive_value(b,&m) && m.value==0xabcdef12 && m.h.msgh_remote_port);
 signal_reply=m.h.msgh_remote_port;CHECK(!receive_value(b,&m) && m.value==0x98765432 && signal_seen==1 && !signal_error);
 CHECK(waitpid(child,&status,0)==child && WIFEXITED(status) && !WEXITSTATUS(status));
 CHECK(!mach_port_destroy(task,p));CHECK(!mach_port_destroy(task,a));CHECK(!mach_port_destroy(task,b));
 puts("Mach real bootstrap IPC signal during receive fork exec send-once cleanup OK");return 0;
}
