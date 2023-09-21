
# Install matter SDK dependencies & extra dependencies needed by the pi
sudo apt-get install -y git gcc g++ python pkg-config libssl-dev libdbus-1-dev \
     libglib2.0-dev libavahi-client-dev ninja-build python3-venv python3-dev \
     python3-pip unzip libgirepository1.0-dev libcairo2-dev avahi-utils \
     linux-modules-extra-raspi
if [ $? -eq 0 ]; then
   echo "*** Successfully installed matter dependencies ***"
else
   echo "*** Failed to install matter dependencies ***"
   exit 1
fi

# Install extra deps
sudo apt-get install -y avahi-utils linux-modules-extra-raspi
if [ $? -eq 0 ]; then
   echo "*** Successfully installed test harness dependencies ***"
else
   echo "*** Failed to install test harness dependencies ***"
   exit 1
fi

# Check if docker is installed, using convenience script could cause issues if
# docker is already installed
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found, attempting to install"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    # Install docker
    if [ $? -eq 0 ]; then
        echo "*** Successfully installed docker ***"
    else
        echo "*** Failed to install docker ***"
        rm get-docker.sh
        exit 1
    fi
    rm get-docker.sh
else
    echo "Docker already installed"
fi


# Install docker-compose
echo "Attempting to install docker compose"
pip install docker-compose
if [ $? -eq 0 ]; then
   echo "*** Successfully installed docker-compose ***"
else
   echo "*** Failed to install docker-compose ***"
   exit 1
fi

# Add user to docker group
sudo gpasswd -a $USER docker

echo "*** Please reboot the machine ***"