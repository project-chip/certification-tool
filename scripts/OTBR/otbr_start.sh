#! /usr/bin/env bash

 #
 # Copyright (c) 2023 Project CHIP Authors
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 # http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
ROOT_DIR=$(realpath $(dirname "$0")/../..)

DEFAULT_OTBR_INTERFACE="eth0"
BR_INTERFACE=${1:-$DEAFULT_OTBR_INTERFACE}
BR_VARIANT="35"
BR_CHANNEL=25
BR_IMAGE_BASE="nrfconnect/otbr"
BR_IMAGE_TAG="9185bda"
BR_IMAGE=$BR_IMAGE_BASE":"$BR_IMAGE_TAG

docker rm otbr-chip > /dev/null 2>&1

if docker images | grep $BR_IMAGE_BASE | grep $BR_IMAGE_TAG;
then
	echo "otbr image "$BR_IMAGE" already installed"
else
	echo "pulling otbr image "$BR_IMAGE
	docker pull $BR_IMAGE || exit 1
fi
AVAHI_PATH=$ROOT_DIR/backend/app/otbr_manager/avahi
sudo modprobe ip6table_filter || exit 1
sudo docker run --privileged -d --network host --name otbr-chip -e NAT64=1 -e DNS64=0 -e WEB_GUI=0 -v $AVAHI_PATH:/etc/avahi -v /dev/ttyACM0:/dev/radio $BR_IMAGE --radio-url spinel+hdlc+uart:///dev/radio?uart-baudrate=115200 -B $BR_INTERFACE || exit 1

echo "waiting 10 seconds to give the the docker container enough time to start up..."

sleep 10

BR_CHANNEL_HEX=$(printf '%02x' $BR_CHANNEL)
BR_PANID="5b${BR_VARIANT}"
BR_EXTPANID="5b${BR_VARIANT}dead5b${BR_VARIANT}beef"
BR_NETWORKNAME="5b${BR_VARIANT}"
BR_IPV6PREFIX="fd11:${BR_VARIANT}::/64"
BR_NETWORKKEY="00112233445566778899aabbccddeeff"

BR_PARAMS=(
"dataset init new"
"dataset channel ${BR_CHANNEL}"
"dataset panid 0x${BR_PANID}"
"dataset extpanid ${BR_EXTPANID}"
"dataset networkname ${BR_NETWORKNAME}"
"dataset networkkey ${BR_NETWORKKEY}"
"dataset commit active"
"prefix add ${BR_IPV6PREFIX} pasor"
"ifconfig up"
"thread start"
"netdata register"
"dataset active -x"
)

for i in "${BR_PARAMS[@]}"
do
        echo "Param: '"$i"'"
        sudo docker exec -t otbr-chip ot-ctl $i || exit 1
done

BR_SIMPLE_DATASET="00030000"${BR_CHANNEL_HEX}"0208"${BR_EXTPANID}"0510"${BR_NETWORKKEY}"0102"${BR_PANID}
sudo echo ${BR_SIMPLE_DATASET} > /tmp/otbr_simple_dataset.txt
echo "Simple Dataset: " ${BR_SIMPLE_DATASET}

# Also make sure to restart the Raspi avahi to have it in a clean state
sudo service avahi-daemon restart
