REQUIRED_PKG="sshpass"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo Checking for $REQUIRED_PKG: $PKG_OK
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get --yes install $REQUIRED_PKG
else
  echo "Package already installed"
fi

if [ "$HOSTNAME" = Sowsterpad ]; then
    sshpass -p 'asdasdasd' rm -rf /home/pi/Thymio & scp -r /mnt/c/users/jakub/desktop/ITU\ sem\ 3/Advanced\ robotics/Effervesence/Thymio/ pi@192.168.4.1:/home/pi/Thymio
else
    sshpass -p 'asdasdasd' rm -rf /home/pi/Thymio & scp -r /mnt/c/users/osman/Documents/github/Effervesence/Thymio/ pi@192.168.4.1:/home/pi/Thymio
fi
