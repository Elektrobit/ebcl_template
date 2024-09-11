#!/usr/bin/sh

for m in $(cat /etc/kernel/runtime_modules.conf); do
    /usr/sbin/modprobe $m
done
