import os

from ament_index_python.packages import get_package_prefix, get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo, OpaqueFunction, RegisterEventHandler, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, NotEqualsSubstitution, PathJoinSubstitution
from launch_ros.actions import Node


def create_sensor_bridge(context):
    world_name = LaunchConfiguration('world_name').perform(context)
    robot_name = LaunchConfiguration('robot_name').perform(context)
    model_prefix = f'/world/{world_name}/model/{robot_name}'
    lidar_topic = f'{model_prefix}/link/rplidar_link/sensor/rplidar/scan'
    camera_prefix = f'{model_prefix}/link/oakd_rgb_camera_frame/sensor/rgbd_camera'
    image_topic = f'{camera_prefix}/image'
    depth_topic = f'{camera_prefix}/depth_image'
    camera_info_topic = f'{camera_prefix}/camera_info'
    battery_topic = f'/model/{robot_name}/battery/linear_battery/state'

    return [Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        namespace=robot_name,
        arguments=[
            f'{lidar_topic}@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            f'{image_topic}@sensor_msgs/msg/Image[gz.msgs.Image',
            f'{depth_topic}@sensor_msgs/msg/Image[gz.msgs.Image',
            f'{camera_info_topic}@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'{battery_topic}@sensor_msgs/msg/BatteryState@gz.msgs.BatteryState',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        remappings=[
            (lidar_topic, 'scan'),
            (image_topic, 'camera/image_raw'),
            (depth_topic, 'camera/depth/image_raw'),
            (camera_info_topic, 'camera/camera_info'),
            (battery_topic, 'battery_state')
        ],
        output='screen'
    )]


def generate_launch_description():
    pkg_turtlebot4_maze_sim = get_package_share_directory('turtlebot4_maze_sim')
    pkg_turtlebot4_description = get_package_share_directory('turtlebot4_description')

    world_path = PathJoinSubstitution([
        pkg_turtlebot4_maze_sim,
        'worlds',
        'maze_world_large.sdf'
    ])

    model_arg = DeclareLaunchArgument(
        'model',
        default_value='standard',
        choices=['standard', 'lite'],
        description='Turtlebot4 model to use.'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='turtlebot4',
        description='Name of the robot entity in Gazebo Harmonic.'
    )

    world_name_arg = DeclareLaunchArgument(
        'world_name',
        default_value='maze_world',
        description='World name used by Gazebo Harmonic.'
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        choices=['true', 'false'],
        description='Launch the Gazebo GUI; set false for headless mode.'
    )

    spawn_x_arg = DeclareLaunchArgument(
        'spawn_x',
        default_value='0.0',
        description='Initial robot X position in the Gazebo world.'
    )

    spawn_y_arg = DeclareLaunchArgument(
        'spawn_y',
        default_value='0.0',
        description='Initial robot Y position in the Gazebo world.'
    )

    spawn_z_arg = DeclareLaunchArgument(
        'spawn_z',
        default_value='0.15',
        description='Initial robot Z position in the Gazebo world.'
    )

    spawn_yaw_arg = DeclareLaunchArgument(
        'spawn_yaw',
        default_value='0.0',
        description='Initial robot yaw in radians in the Gazebo world.'
    )

    robot_xacro = PathJoinSubstitution([
        pkg_turtlebot4_maze_sim,
        'urdf',
        'turtlebot4_maze.urdf.xacro'
    ])

    robot_description = Command([
        'xacro ',
        robot_xacro,
        ' gazebo:=ignition namespace:=',
        LaunchConfiguration('robot_name')
    ])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=LaunchConfiguration('robot_name'),
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': robot_description}
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    tf_namespaced_odom_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_namespaced_odom_publisher',
        namespace=LaunchConfiguration('robot_name'),
        parameters=[{'use_sim_time': True}],
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'odom', [LaunchConfiguration('robot_name'), '/odom']
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen',
        condition=IfCondition(NotEqualsSubstitution(LaunchConfiguration('robot_name'), ''))
    )

    tf_namespaced_base_link_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_namespaced_base_link_publisher',
        namespace=LaunchConfiguration('robot_name'),
        parameters=[{'use_sim_time': True}],
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            [LaunchConfiguration('robot_name'), '/base_link'], 'base_link'
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen',
        condition=IfCondition(NotEqualsSubstitution(LaunchConfiguration('robot_name'), ''))
    )

    tf_namespaced_lidar_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_namespaced_lidar_publisher',
        namespace=LaunchConfiguration('robot_name'),
        parameters=[{'use_sim_time': True}],
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'rplidar_link', [LaunchConfiguration('robot_name'), '/rplidar_link/rplidar']
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        output='screen',
        condition=IfCondition(NotEqualsSubstitution(LaunchConfiguration('robot_name'), ''))
    )

    controller_manager = PathJoinSubstitution([
        '/',
        LaunchConfiguration('robot_name'),
        'controller_manager'
    ])

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', controller_manager,
            '--controller-manager-timeout', '60'
        ],
        output='screen'
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diffdrive_controller',
            '--controller-manager', controller_manager,
            '--controller-manager-timeout', '60'
        ],
        output='screen'
    )

    start_drive_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner]
        )
    )

    generate_robot_urdf = ExecuteProcess(
        cmd=[
            'xacro', robot_xacro,
            'gazebo:=ignition',
            ['namespace:=', LaunchConfiguration('robot_name')],
            '-o', '/tmp/turtlebot4_maze_robot.urdf'
        ],
        output='screen'
    )

    world_server_gui = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],
        output='screen',
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    world_server_headless = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', world_path],
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    spawn_robot = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'ros_gz_sim', 'create',
            '-world', LaunchConfiguration('world_name'),
            '-file', '/tmp/turtlebot4_maze_robot.urdf',
            '-name', LaunchConfiguration('robot_name'),
            '-x', LaunchConfiguration('spawn_x'),
            '-y', LaunchConfiguration('spawn_y'),
            '-z', LaunchConfiguration('spawn_z'),
            '-Y', LaunchConfiguration('spawn_yaw')
        ],
        output='screen'
    )

    spawn_controllers = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_robot,
            on_exit=[TimerAction(period=2.0, actions=[joint_state_broadcaster_spawner])]
        )
    )

    spawn_after_description = RegisterEventHandler(
        OnProcessExit(
            target_action=generate_robot_urdf,
            on_exit=[TimerAction(period=3.0, actions=[spawn_robot])]
        )
    )

    ament_prefixes = [p for p in os.environ.get('AMENT_PREFIX_PATH', '').split(os.pathsep) if p]
    resource_paths = os.pathsep.join([p + '/share' for p in ament_prefixes])
    library_paths = os.pathsep.join(
        [p + '/lib' for p in ament_prefixes] + [
            os.path.join(
                get_package_prefix('gz_sim_vendor'),
                'opt', 'gz_sim_vendor', 'lib', 'gz-sim-8', 'plugins'
            ),
            os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', '')
        ]
    )

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_paths),
        SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', library_paths),
        model_arg,
        robot_name_arg,
        world_name_arg,
        gui_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        spawn_yaw_arg,
        LogInfo(msg='Launching TurtleBot4 maze world in Gazebo Harmonic'),
        generate_robot_urdf,
        robot_state_publisher,
        tf_namespaced_odom_publisher,
        tf_namespaced_base_link_publisher,
        tf_namespaced_lidar_publisher,
        OpaqueFunction(function=create_sensor_bridge),
        world_server_gui,
        world_server_headless,
        spawn_after_description,
        spawn_controllers,
        start_drive_controller,
    ])
