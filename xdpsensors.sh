PIDFILE=/var/run/xdpsensors.pid
case "$1" in
    start)
        gst-launch-1.0 videotestsrc ! video/x-raw,width=720,height=480,framerate=5/1 ! theoraenc ! oggmux ! tcpserversink host=0.0.0.0 port=9991 &
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
