#!/bin/bash
sshpass -p 1qaz2wsx rsync -avz --exclude-from='exclude.list' -e ssh -r ../UAMS ts@106.12.27.16:/home/ts
sshpass -p zuzhewaner123! ssh root@106.12.27.16 'service apache2 restart'