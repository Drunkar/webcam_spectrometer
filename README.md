# webcam spectrometer

## requirements
- raspberry pi: I used raspberry pi 2 model B.
- hdmi display
- usb webcam


## raspberry pi display setting

### display
OSOYOO HDMI 3.5 inch touch LCD display
https://www.amazon.co.jp/OSOYOO-%E3%82%AA%E3%82%BD%E3%83%A8%E3%83%BC-3-5%E3%82%A4%E3%83%B3%E3%83%81LCD%E3%83%87%E3%82%A3%E3%82%B9%E3%83%97%E3%83%AC%E3%82%A4-1920x1080%E3%83%8F%E3%82%A4%E3%83%93%E3%82%B8%E3%83%A7%E3%83%B3-Raspberry/dp/B01N5HW3BP/ref=sr_1_5?ie=UTF8&qid=1494432790&sr=8-5&keywords=raspberry+pi+%E3%83%87%E3%82%A3%E3%82%B9%E3%83%97%E3%83%AC%E3%82%A4

### setting

Modify `/boot/config.txt`

```
hdmi_group=2
hdmi_mode=4: 640 x 480 60hz
```

## Usage

### 1. Download

```
git clone https://github.com/Drunkar/webcam_spectrometer.git
```

### 2. autostart settings

Add below to `~/.config/lxsession/LXDE-pi/autostart`

```
@/path/to/webcam_spectrometer/application.linux-armv6hf/webcam_spectrometer
```
