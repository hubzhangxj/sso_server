#!/bin/bash
sshpass -p tzy@123 rsync -avz --exclude-from='exclude.list' -e ssh -r ../UAMS root@114.119.11.94:/home/ts
sshpass -p tzy@123 ssh root@114.119.11.94 'chown -R www-data /home/ts/UAMS'
#sshpass -p tzy@123 ssh root@114.119.11.94 'python /home/ts/UAMS/manage.py compilemessages'
#sshpass -p tzy@123 ssh root@114.119.11.94 'service apache2 restart'