#!/bin/bash
sshpass -p huawei@123 rsync -avz --exclude-from='/home/litao/UAMS/exclude.list' -e ssh -r /home/litao/UAMS root@192.168.10.203:/home/huawei/
sshpass -p huawei@123 ssh root@192.168.10.203 'python /home/huawei/UAMS/manage.py compilemessages'
sshpass -p huawei@123 ssh root@192.168.10.203 'rm -rf /home/huawei/UAMS/log/*'
sshpass -p huawei@123 ssh root@192.168.10.203 'service apache2 restart'
sshpass -p huawei@123 ssh root@192.168.10.203 'chown -R www-data /home/huawei/UAMS'