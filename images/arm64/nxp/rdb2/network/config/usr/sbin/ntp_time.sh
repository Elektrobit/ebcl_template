#!/usr/bin/sh

while ! ping -c 1 google.de > /dev/null 2>&1
do
  sleep 1
done

ntpdate -s time.nist.gov
