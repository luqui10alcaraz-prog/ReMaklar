#!/usr/bin/perl
# Keep original services alive together, then terminate only verified children.
# SPDX-License-Identifier: MIT
use strict;
use POSIX qw(:sys_wait_h setsid);
my ($out,$exe,$root)=@ARGV;
die 'usage: output-dir executor Jaguar-root' unless $root;
mkdir $out or die $!;
my %owned;my @stems;
sub start {
 my ($name,@args)=@_;my $stem="$out/$name";push @stems,$stem;
 open CMD,'>',"$stem.command" or die $!;print CMD join(' ',$exe,'--root',$root,@args),"\n";close CMD;
 my $pid=fork();die $! unless defined $pid;
 if(!$pid){setsid()>=0 or die $!;open STDOUT,'>',"$stem.stdout" or die $!;open STDERR,'>',"$stem.stderr" or die $!;$ENV{OS_INSTALL}=1;exec $exe,'--root',$root,@args;die $!;}
 $owned{$pid}=1;
}
sub sample {
 for my $stem (@stems){if(open TRACE,'<',"$stem.stderr"){while(<TRACE>){if(/fork real host_pid=\d+ child_pid=(\d+) branch=parent/){$owned{$1}=1;}}close TRACE;}}
 open PS,'ps -axww |' or die $!;open SNAP,'>>',"$out/processes.txt" or die $!;
 print SNAP "sample=",time(),"\n";while(<PS>){print SNAP $_;}close SNAP;close PS;
 for my $pid(keys %owned){my $w=waitpid($pid,WNOHANG);if($w==$pid){open STATUS,'>>',"$out/leaders.status" or die $!;print STATUS "pid=$pid raw=$?\n";close STATUS;}}
}
my $ats='/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/ATS.framework/Versions/A/Support/StartATSServer';
start('ats',"$root$ats");sleep 5;sample();
start('windowserver',"$root/System/Library/CoreServices/WindowServer");sleep 10;sample();
start('pbs',"$root/System/Library/CoreServices/pbs");sleep 5;sample();
start('splash',"$root/System/Installation/CDIS/splash",'/Applications/Utilities/Installer.app/Contents/MacOS/Installer');
for(1..18){sleep 5;sample();}
open PS,'ps -axww |' or die $!;
while(<PS>){if(/^\s*(\d+)\s+\S+\s+\S+\s+\S+\s+(.*)$/ && $owned{$1} && index($2,$exe)>=0){kill 9,$1;}}
close PS;sample();
open END,'>',"$out/completion.status" or die $!;print END "bounded_joint_trial_complete=1\n";close END;
