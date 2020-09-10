echo "----------------------- Syncing Environment ----------------------"
pipenv sync

echo "------------------------ Sourcing ENV file -----------------------"
_ENV_FILE='./env'
if [ ! -f $_ENV_FILE ]; then
    read -p "Create file \"$_ENV_FILE\" with secret key, then press enter to continue!"
    if [ ! -f $_ENV_FILE ]; then
        echo "You didn't create the file! Exiting."
        exit
    fi
fi
source $_ENV_FILE

echo "------------------------- Django Setup ---------------------------"
./manage.py migrate
./manage.py collectstatic
./manage.py createsuperuser

echo "---------------------- Iptables Config ---------------------------"
sudo iptables -I INPUT 9 -i eth1 -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
sudo iptables-save > /tmp/a
sudo mv /tmp/a /etc/sysconfig/iptables

echo "-------------------- Installing Gunicorn -------------------------"
pip3 install gunicorn

echo "Finished! Now configure Gunicorn!" 
