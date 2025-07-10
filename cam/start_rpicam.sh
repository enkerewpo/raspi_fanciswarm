rpicam-vid --timeout 0 --inline --listen -o tcp://0.0.0.0:8000 --vflip --width 1920 --height 1080 --framerate 60

# on your local machine
# ffplay -fflags nobuffer -flags low_delay -framedrop -strict experimental tcp://100.105.182.31:8000