#!/bin/bash
SSH_PREFIX=""
SSH_PORT=22
SSH_USER=root
SSH_TARGET=localhost
KNOWN_HOSTS="/home/ebcl/.ssh/known_hosts"

while [[ $# -gt 0 ]] ; do
key="$1"
case $key in
    --prefix)
    SSH_PREFIX=$2
    shift ; shift
    ;;
    --port)
    SSH_PORT=$2
    shift ; shift
    ;;
    --user)
    SSH_USER=$2
    shift ; shift
    ;;
    --target)
    SSH_TARGET=$2
    shift ; shift
    ;;
    --known-hosts)
    KNOWN_HOSTS=$2
    shift ; shift
    ;;
    *)
    echo "Parameter \"$key\" unknown"
    exit
    ;;
esac
done

SSH_CMD="$SSH_PREFIX ssh"
SSH_COMMON_PARM="-p $SSH_PORT $SSH_USER@$SSH_TARGET true"
[ -z "$KNOWN_HOSTS" ] && KNOWN_HOSTS=

$SSH_CMD $SSH_COMMON_PARM || { \
    echo "SSH key not found or outdated, performing update!" ; \
    ssh-keygen -f "$KNOWN_HOSTS" -R "[$SSH_TARGET]:$SSH_PORT"; \
    $SSH_CMD -o StrictHostKeyChecking=accept-new $SSH_COMMON_PARM; \
}
