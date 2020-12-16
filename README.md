# Farmation
A website for risk and profit analysis of farms

## Start up

First update the instance.
Use python3 and pipenv.

```
pip3 install --user pipenv
```

Second time (or at least after the text above was written)
the `pipenv` command was not found.
The install proceeded without error -- but command was not found.
The second time solution was to execute the command below.
```
sudo -H pip install -U pipenv
```

If `pip3` is not found:
```
sudo apt install python3-pip
```

Get the code
```
git@github.ncsu.edu:vwfreeh/farmation.git
```

May have to create public key (`ssh-keygen`) and upload (`.ssh/id-rsa.pub`)
to github.

Enter the environment (if it doesn't exist _shell_ command will create
it) and install required software.

```
pipenv shell
pipenv update
```

Before you run django on your install, you need a secret key.
Best practices suggest (demand) that the key is not in the repo.
Generate a key.
(Here is a
[page](https://www.miniwebtool.com/django-secret-key-generator/).)
Save it to a file and source the file as shown:

```
$ cat > env
export SECRET_KEY='--------------------------------------------------'
$ source ./env
$ printenv | grep KEY
SECRET_KEY=--------------------------------------------------
```

Finishing touches for django.

```
./manage.py migrate
./manage.py createsuperuser
```

Load crop data.
```
./manage loaddata fixtures/fake-cropdata.json
```

Run the server.
```
$ ./manage.py runserver &
```

Test it.
```
$ wget http://localhost:8000 -qO /dev/null
[01/Aug/2019 21:17:07] "GET / HTTP/1.1" 302 0
[01/Aug/2019 21:17:07] "GET /accounts/login/?next=/ HTTP/1.1" 200 3842
$
```
The home page is requires a login, so it was redirected to the login
page.

## Pip install error
Found on some site that your are to update pip as
```
python3 -m pip install --user --upgrade pip
```
**Don't do that**.
Causes the following error.
```
$ pip3
Traceback (most recent call last):
  File "/usr/bin/pip3", line 9, in <module>
    from pip import main
ImportError: cannot import name 'main'
```

If that happens, unupgrade:
```
python3 -m pip uninstall pip
```

# Gunicorn + Nginx

```
pipenv install gunicorn
sudo apt-get install -y nginx
```

Edit gunicorn config file
```
cat /etc/systemd/system/gunicorn.service 
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/home/vwfreeh/farmation
ExecStart=/home/vwfreeh/farmation/gunicorn.sh

[Install]
WantedBy=multi-user.target
```

Create directory for gunicorn: `sudo mkdir /run/gunicorn`

Change permissions: `chmod +x gunicorn.sh`

Edit nginx config file.

# Edit iptables

The command below opens the firewall on VCL.
```
sudo iptables -I INPUT 9 -i eth1 -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
```

Check connection.
```
sudo iptables -nvL
```

Should see a line similar to:
```
    0     0 ACCEPT     tcp  --  eth1   *       0.0.0.0/0            0.0.0.0/0            tcp dpt:80 state NEW,ESTABLISHED
```

