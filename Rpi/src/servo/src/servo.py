import RPi.GPIO as GPIO
import rospy
import mavros
import mavros_msgs
import nav_msgs
from std_msgs.msg import String

servoPIN = 17

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz (it depends on servo motor)

rate = rospy.Rate(10)

isRotated = False
current_mission = 0
mission_data = []

class Mission:
    def __init__(self, mission_id, cycle, lat, lon, height):
        self.mission_id = mission_id
        self.cycle = cycle
        self.lat = lat
        self.lon = lon
        self.height = height


class ServoHandle(Mission):
    #Cycle should be int.Therefore be aware of what data you are passing from ros

    def rotate_by_value(self, cycle):
        p.ChangeDutyCycle(cycle)

    def rotate_by_location(self, cycle, lat, lon, height):
        #Get Location data

        #Get Mission data

        #Compare Values

        #Change DutyCycle
        self.rotate_by_value(cycle)


class subscriberListener(rospy.SubscribeListener):
    def peer_subscribe(self, topic_name, topic_publish, peer_publish):
        print("a peer subscribed to topic [%s]"%topic_name)
        str = "Joined topic "+topic_name
        print(str)
        peer_publish(String(str))
        
    def peer_unsubscribe(self, topic_name, numPeers):
        print("a peer unsubscribed from topic [%s]"%topic_name)
        if numPeers == 0:
            print("Topic has no subscriber")

pub = rospy.Publisher('/rpi/mission/servoCom', String, queue_size=20, subscriber_listener=subscriberListener())


def ros_start(node):
    rospy.init_node(node , anonymous=True)
   

def getMission(data):
    #Data format should be [mission.id-cycle-lat-lon-height]
    rawData = data.data
    splitted = rawData.split("-")
    mission_id = int(splitted[0])
    cycle = int(splitted[1])
    lat = float(splitted[2])
    lon = float(splitted[3])
    height = int(splitted[4])
    mission_data.append(Mission(mission_id,cycle, lat, lon, height))



if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    GPIO.setwarnings(False)
    p.start(2.5)

    ros_start("servo")
    rospy.Subscriber("/ground/mission/servoCom", String, getMission)
    rospy.spin()
