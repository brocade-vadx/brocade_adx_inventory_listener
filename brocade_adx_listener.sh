PATHAPP="/root/PycharmProjects/adx_inventory/brocade_adx_device_inventory/nova_listener.py &"
PIDAPP="/var/brocade_nova_listener.pid"
case $1 in
        start)
                echo "starting"
                $(python $PATHAPP)
        ;;
        stop)
                echo "stoping"
                PID=$(cat $PIDAPP)
                kill $PID
        ;;

esac