# Farmation
A website for risk and profit analysis of farms

## Start up

First update the instance.
Use python3 and pipenv.

```
pip3 install --user pipenv
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
