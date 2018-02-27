#!/bin/bash
sshpass -p litao rsync -avz --exclude-from='exclude.list' -e 'ssh -p 222' -r ../UAMS litao@htsat.vicp.cc:~/
