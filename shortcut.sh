#!/bin/bash
#
# create shortcut on desktop
#
DIR=$(pwd)

cat <<EOF > weather.desktop
[Desktop Entry]
Name=Openweather
Type=Application
Exec=lxterminal -t "WEATHER" --working-directory=$DIR -e ./weather.sh
Icon=${DIR}/OpenLogo.png
Comment=OpenWeather
Terminal=true
EOF

chmod 755 weather.desktop
mv weather.desktop ~/Desktop
