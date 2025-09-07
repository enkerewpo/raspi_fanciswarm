#!/bin/bash

# Script to check ROS node status and logs
# Usage: ./check_ros_nodes.sh

echo "========================= ROS Node Status Check ========================="

# Check if ROS is running
if pgrep -f "rosmaster" > /dev/null; then
    echo "ROS Master is running"
else
    echo "ROS Master is not running"
    exit 1
fi

# Check ROS nodes
echo ""
echo "Active ROS Nodes:"
rosnode list 2>/dev/null || echo "No ROS nodes found or ROS not properly sourced"

# Check ROS topics
echo ""
echo "Active ROS Topics:"
rostopic list 2>/dev/null || echo "No ROS topics found or ROS not properly sourced"

# Check specific FCU nodes
echo ""
echo "FCU Core Nodes Status:"
for node in fcu_bridge_001 fcu_command_server fcu_mission; do
    if rosnode info $node >/dev/null 2>&1; then
        echo "$node is running"
    else
        echo "$node is not running"
    fi
done

# Check FCU command server port
echo ""
echo "FCU Command Server Port Check:"
if netstat -tlnp 2>/dev/null | grep :8888 > /dev/null; then
    echo "Port 8888 is listening (FCU Command Server)"
else
    echo "Port 8888 is not listening"
fi

# Check ROS logs
echo ""
echo "Recent ROS Logs:"
echo "Note: ROS logs are now displayed directly in the terminal without duplication"
echo "For detailed logs, check the ROS log directory below"

# Check ROSout logs (actual ROS node output)
echo ""
echo "ROSout Logs (Node Output):"
if [ -d ~/.ros/log/latest ]; then
    echo "ROSout log content:"
    cat ~/.ros/log/latest/rosout.log 2>/dev/null || echo "No rosout log found"
else
    echo "No ROS log directory found"
fi

echo ""
echo "=========================================================================="
