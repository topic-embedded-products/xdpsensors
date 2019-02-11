PIDFILE=/var/run/xdpsensors.pid
case "$1" in
    start)
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
