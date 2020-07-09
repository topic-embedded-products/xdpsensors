PIDFILE=/var/run/xdpsensors.pid
case "$1" in
    start)
        cp /var/www/camera.jpg /tmp/frame.jpg
        xdp-dyplo-app -c 2 -k 5 -w 960 -h 540 -f - | \
        gst-launch-1.0 fdsrc fd=0 blocksize=2073600 do-timestamp=true ! \
        rawvideoparse use-sink-caps=false width=960 height=540 format=bgrx framerate=10/1 ! \
        videoconvert ! jpgenc ! multifilesink location=/tmp/frame.jpg &
        sleep 1
        dyploroute 0,0-0,0
        dyploroute 1,0-2,0
        twistd --pidfile $PIDFILE -o -y /var/www/xdpsensors.tac
        ;;
    stop)
        if [ -e $PIDFILE ]
        then
            kill `cat $PIDFILE`
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
