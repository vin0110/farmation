* Run first setup script in home directory.
```
$ source setup.sh
```

* Create ```env``` file
```
$ echo "export SECRET_KEY=' ... '" > ./env
```

* Run second setup script in project directory.
``` 
$ source setup2.sh
```

* Determine Gunicorn exectuable's absolute path. 
```
$ which gunicorn
/home/yourusername/.local/share/virtualenvs/farmation-ABC123/bin/gunicorn
```

* Replace path in ```gunicorn.sh``` with this path.
```
#!/bin/bash
source ./env
/home/yourusername/.local/share/virtualenvs/farmation-ABC123/bin/gunicorn \
    --pid /run/gunicorn/pid   \
    --bind unix:/run/gunicorn/socket farmation.wsgi
```

* Create ```/etc/systemd/system/gunicorn.service```
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
PIDFile=/run/gunicorn/pid
User=yourusername
Group=vcl
RuntimeDirectory=gunicorn
WorkingDirectory=/home/yourusername/farmation
ExecStart=/home/yourusername/farmation/gunicorn.sh
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

* Create ```/etc/systemd/system/gunicorn.service```
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn/socket

[Install]
WantedBy=sockets.target
```

* Start gunicorn service and check that it started successfully.
```
$ sudo systemctl start gunicorn
$ sudo systemctl status gunicorn
● gunicorn.service - gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
   Active: active (running) since Thu 2019-08-29 14:35:30 EDT; 1min 17s ago
 Main PID: 25735 (gunicorn.sh)
    Tasks: 6 (limit: 4681)
   CGroup: /system.slice/gunicorn.service
           ├─25735 /bin/bash /home/yourusername/farmation/gunicorn.sh
           ├─25736 /home/yourusername/.local/share/virtualenvs/farmation-ABC123/bin/python3.6 /ho
           └─25739 /home/yourusername/.local/share/virtualenvs/farmation-ABC123/bin/python3.6 /ho

Aug 29 14:35:30 vm18-228.vcl.ncsu.edu systemd[1]: Started gunicorn daemon.
Aug 29 14:35:30 vm18-228.vcl.ncsu.edu gunicorn.sh[25735]: [2019-08-29 14:35:30 -0400] [25736] 
Aug 29 14:35:30 vm18-228.vcl.ncsu.edu gunicorn.sh[25735]: [2019-08-29 14:35:30 -0400] [25736] 
Aug 29 14:35:30 vm18-228.vcl.ncsu.edu gunicorn.sh[25735]: [2019-08-29 14:35:30 -0400] [25736] 
Aug 29 14:35:30 vm18-228.vcl.ncsu.edu gunicorn.sh[25735]: [2019-08-29 14:35:30 -0400] [25739] 

```
