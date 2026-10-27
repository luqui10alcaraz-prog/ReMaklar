#!/usr/bin/perl
# Keep original services alive together, then terminate only verified children.
# SPDX-License-Identifier: MIT
use strict;
use POSIX qw(:sys_wait_h setsid);
my ($out,$exe,$root)=@ARGV;
die 'usage: output-dir executor Jaguar-root' unless $root;
mkdir $out or die $!;
my(%owned,%leader,%exited,%trace_offset,%trace_pending);my @stems;my $backend_seen=0;
my $installer_samples=$ENV{REMAKLAR_JOINT_SAMPLES} || 42;
die 'REMAKLAR_JOINT_SAMPLES must be 1..120' unless $installer_samples=~/^\d+$/ && $installer_samples>=1 && $installer_samples<=120;
sub start {
 my ($name,@args)=@_;
 my $guest_argv0=$args[0];$guest_argv0=substr($guest_argv0,length($root)) if index($guest_argv0,"$root/")==0;
 unshift @args,'--exec-argv0',$guest_argv0;
 my $stem="$out/$name";push @stems,$stem;
 open CMD,'>',"$stem.command" or die $!;print CMD join(' ',$exe,'--root',$root,@args),"\n";close CMD;
 my $pid=fork();die $! unless defined $pid;
 if(!$pid){setsid()>=0 or die $!;open STDOUT,'>',"$stem.stdout" or die $!;open STDERR,'>',"$stem.stderr" or die $!;$ENV{OS_INSTALL}=1;exec $exe,'--root',$root,@args;die $!;}
 $owned{$pid}=1;$leader{$name}=$pid;
}
sub scan_traces {
 for my $stem (@stems){if(open TRACE,'<',"$stem.stderr"){
  seek(TRACE,$trace_offset{$stem} || 0,0) or die $!;
  my $pending=$trace_pending{$stem} || '';
  while(1){my $chunk;my $n=read(TRACE,$chunk,65536);die $! unless defined $n;last unless $n;
   my @lines=split(/\n/,$pending.$chunk,-1);$pending=pop @lines;
   for my $line (@lines){
    if($line=~/fork real host_pid=\d+ child_pid=(\d+) branch=parent/){$owned{$1}=1;}
    if($line=~/^remaklar: |^unsupported |^unverified |^invalid / || $line=~/could not establish the default connection|failed assertion|fork .*requires|unsupported sysctl/){$backend_seen=1;}
   }
  }
  $trace_offset{$stem}=tell(TRACE);$trace_pending{$stem}=$pending;close TRACE;
 }}
}
sub sample {
 scan_traces();
 open PS,'ps -axww |' or die $!;open SNAP,'>>',"$out/processes.txt" or die $!;
 print SNAP "sample=",time(),"\n";while(<PS>){print SNAP $_;}close SNAP;close PS;
 for my $pid(keys %owned){my $w=waitpid($pid,WNOHANG);if($w==$pid){$exited{$pid}=1;open STATUS,'>>',"$out/leaders.status" or die $!;print STATUS "pid=$pid raw=$?\n";close STATUS;}}
}
sub backend_block {
 return $backend_seen;
}
my $ats='/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/ATS.framework/Versions/A/Support/StartATSServer';
start('ats',"$root$ats");sleep 5;sample();
start('windowserver',"$root/System/Library/CoreServices/WindowServer");
my $ready=0;my $backend_block=0;
for(1..60){sleep 5;sample();
 if(backend_block()){$backend_block=1;last;}
 if(open READY,'<',"$out/windowserver.stderr"){
  while(<READY>){$ready=1 if /native Mach message error=10004003 options=2000102 send=0 receive=32768/;}
  close READY;
 }
 last if $ready;
}
open READY_STATUS,'>',"$out/windowserver-ready.status" or die $!;
print READY_STATUS "server_receive_loop_observed=$ready\n";close READY_STATUS;

if($ready){
start('pbs',"$root/System/Library/CoreServices/pbs");sleep 5;sample();
start('installer',"$root/Applications/Utilities/Installer.app/Contents/MacOS/Installer");
my $sampled=0;my $reason='installer_sample_budget';
for(1..$installer_samples){sleep 5;sample();$sampled++;
 $backend_block=backend_block();
 if($backend_block){$reason='backend_error';last;}
 if($exited{$leader{installer}}){$reason='installer_exited';last;}
}
open LIMIT,'>',"$out/installer-budget.status" or die $!;print LIMIT "samples=$sampled maximum=$installer_samples interval_guest_seconds=5 reason=$reason\n";close LIMIT;
}
if($backend_block){open BLOCK,'>',"$out/backend-block.status" or die $!;print BLOCK "backend_block_observed=1\n";close BLOCK;}

open PS,'ps -axww |' or die $!;
while(<PS>){if(/^\s*(\d+)\s+\S+\s+\S+\s+\S+\s+(.*)$/ && $owned{$1} && index($2,$exe)>=0){kill 9,$1;}}
close PS;sample();
open END,'>',"$out/completion.status" or die $!;print END "bounded_joint_trial_complete=1\n";close END;
