# Farmation
A website for risk and profit analysis of farms

## Start up

First update the instance.
Use python3 and pipenv.

```
sudo apt update && sudo apt upgrade
sudo apt install python3-pip
pip3 install --user pipenv
```

After last line, pip is broken:
```
$ pip3
Traceback (most recent call last):
  File "/usr/bin/pip3", line 9, in <module>
    from pip import main
ImportError: cannot import name 'main'
```
This is explained in
[SO post](https://superuser.com/questions/1432768/how-to-properly-install-pipenv-on-wsl-ubuntu-18-04).
Solution is:
```
$ cat >> .bashrc
# set PATH so it includes user's private bin if it exists                                 
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
$ source .bashrc
```

Test if `pip3` is found.

Get the code
```
git@github.ncsu.edu:vwfreeh/farmation.git
```

Enter the environment (if it doesn't exist _shell_ command will create
it) and install required software.

```
pipenv shell
pipenv sync
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
