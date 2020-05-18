# Installing on VCL

* Create ssh key `ssh-keygen`
* Add key to github: copy _~/.ssh/id-rsa.pub_
* Login to VCL
* Update the instance
```
sudo apt update
sudo apt upgrade
```
For some reason it tends to hang at 79% on `linux-headers`.
It will eventually continue; patience.
* Get source
```
git clone git@github.ncsu.edu:vwfreeh/farmation.git
```
* Install pip, et al
```
sudo apt install python3-pip
pip3 install --user pipenv
```
pipenv, et al are install in `.local/bin`
```
$ pipenv
pipenv: command not found
$ .local/bin/pipenv --version
pipenv, version 2018.11.26
```
* Add `~/.local/bin` to path
```
$ cat >> .bashrc

PATH=~/.local/bin:$PATH
^D
$ source .bashrc
```
* Create environment
```
cd farmation
pipenv sync
```
* Create env file, which holds values we will not put in the
repo. Initially, this is only the SECRET_KEY.

* Get a key from online generator, such as
[this](https://www.miniwebtool.com/django-secret-key-generator/).
```
$ cat > env
export SECRET_KEY="--------------------------------------------------"
^D
$ source env
```

## Initialize django

* `./manage.py migrate`
* `./manage.py collectstatic`
* `./manage.py createsuperuser`

Now test the system.
```
./manage.py runserver 0.0.0.0:8000 &
wget -O - http://localhost:8000 > /dev/null
```

## Setup nginx & gunicorn

### First open port 80 on VCL

```
sudo iptables -I INPUT 9 -i eth1 -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
sudo iptables-save > /tmp/a
sudo mv /tmp/a /etc/sysconfig/iptables
```

### Gunicorn

* Install (from within the environment):
```
pip3 install gunicorn
```

* Test
```
gunicorn farmation.wsgi:application --bind 0.0.0.0:8000 &
wget -O - http://localhost:8000 > /dev/null
```


In host browser, load `localhost:8000`.
If that works, then setup gunicorn to run on startup.

Set up gunicorn as a service.
Create two files.

__/etc/systemd/system/gunicorn.service__
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
PIDFile=/run/gunicorn/pid
User=vwfreeh
Group=vwfreeh
RuntimeDirectory=gunicorn
WorkingDirectory=/home/vwfreeh/farmation
ExecStart=/home/vwfreeh/farmation/gunicorn.sh
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
PIDFile=/run/gunicorn/pid
User=vagrant
Group=vagrant
RuntimeDirectory=gunicorn
WorkingDirectory=/vagrant/slider
ExecStart=/vagrant/.env/bin/gunicorn --pid /run/gunicorn/pid   \
          --bind unix:/run/gunicorn/socket farmation.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

__/etc/systemd/system/gunicorn.socket__
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn/socket

[Install]
WantedBy=sockets.target
```

Start gunicorn with ```sudo systemctl start gunicorn```

### nginx

* Install `sudo apt install nginx`
Create one file

__/etc/nginx/sites-available/farmation__
```
server {
        listen 80;
        server_name 127.0.0.1;

        # location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
             root /home/vwfreeh/farmation;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn/socket;
        }
}
```

* Make link `sudo ln -s /etc/nginx/sites-available/farmation /etc/nginx/sites-enabled`
* Remove _default_ `sudo rm /etc/nginx/sites-enabled/default`

* Start nginx with ```sudo systemctl start nginx```.
