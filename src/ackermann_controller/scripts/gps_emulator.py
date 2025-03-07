#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import PoseStamped, Quaternion, Twist, TransformStamped
from gazebo_msgs.msg import ModelStates
import math
import tf_transformations 
from tf2_ros import TransformBroadcaster
from nav2_msgs.srv import SetInitialPose
import random

class DummyNode(Node):
    def __init__(self):
        super().__init__('dummy_node')
        self.ground_truth_subscriber = self.create_subscription(ModelStates, '/gazebo/model_states', self.ground_truth_callback, 10)
        self.gps_pub = self.create_publisher(PoseStamped, '/gps', 10)

        # Define noise standard deviations (adjust these values as needed)
        self.position_noise_stddev = 0.05  # Standard deviation for position noise (meters)
        self.orientation_noise_stddev = 0.01  # Standard deviation for quaternion noise

    def ground_truth_callback(self, msg: ModelStates):
        index = msg.name.index("ackbot")
        posX = msg.pose[index].position.x
        posY = msg.pose[index].position.y
        posZ = msg.pose[index].position.z

        q1 = msg.pose[index].orientation.x
        q2 = msg.pose[index].orientation.y
        q3 = msg.pose[index].orientation.z
        q4 = msg.pose[index].orientation.w

        # Add Gaussian noise to position
        noisy_posX = posX + random.gauss(0, self.position_noise_stddev)
        noisy_posY = posY + random.gauss(0, self.position_noise_stddev)
        noisy_posZ = posZ + random.gauss(0, self.position_noise_stddev)

        # Add Gaussian noise to orientation
        noisy_q1 = q1 + random.gauss(0, self.orientation_noise_stddev)
        noisy_q2 = q2 + random.gauss(0, self.orientation_noise_stddev)
        noisy_q3 = q3 + random.gauss(0, self.orientation_noise_stddev)
        noisy_q4 = q4 + random.gauss(0, self.orientation_noise_stddev)

        # Normalize the quaternion to maintain a valid rotation
        norm = math.sqrt(noisy_q1**2 + noisy_q2**2 + noisy_q3**2 + noisy_q4**2)
        noisy_q1 /= norm
        noisy_q2 /= norm
        noisy_q3 /= norm
        noisy_q4 /= norm

        # Publish noisy GPS data
        msg = PoseStamped()
        msg.header.frame_id = 'odom'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = noisy_posX
        msg.pose.position.y = noisy_posY
        msg.pose.position.z = noisy_posZ
        msg.pose.orientation.x = noisy_q1
        msg.pose.orientation.y = noisy_q2
        msg.pose.orientation.z = noisy_q3
        msg.pose.orientation.w = noisy_q4

        self.gps_pub.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)
    node = DummyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
