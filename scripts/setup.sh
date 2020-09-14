#!/bin/bash
echo "-------------------- Updates and Installs ------------------------------"
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip
pip3 install --user pipenv

echo "--------------------- Cloning Repository -------------------------------"
git clone https://github.ncsu.edu/vwfreeh/farmation.git

echo "----------------------- Updating PATH ----------------------------------"
echo "PATH=~/.local/bin:$PATH" >> ~/.bashrc
source .bashrc
echo "----------------- Entering project environment -------------------------"
cd farmation
pipenv shell

echo "------------------------------------------------------------------------"
echo "Finished! Now run \"source setup2.sh\""

