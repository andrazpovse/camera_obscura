# Requirements for light sensor
sudo apt-get install python3-smbus (if not installed)
sudo modprobe i2c-dev
(check if enabled in bootconfig)

# Requirement for pydub
sudo apt-get install ffmpeg

# Requirements for running at boot
Run command:
```sudo crontab -e```
Inside add the following line:
```@reboot /home/pi/camera_obscura/run_at_boot.sh >> /home/pi/err.log 2>&1```
Make sure to give correct permission to run_at_boot.sh file
```chmod +x run_at_boot.sh ```

Pin connections for sensor <-> RPI

- ADDR - NC
- SDA - SDA (PIN3)
- SCL - SCL (PIN5)
- GND - GND (PIN6)
- VCC - 3.3V (PIN1)

[ThingSpeak graph](https://thingspeak.com/channels/942106)