import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo, RegisterEventHandler, SetEnvironmentVariable, TimerAction
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_turtlebot4_maze_sim = get_package_share_directory('turtlebot4_maze_sim')
    pkg_turtlebot4_description = get_package_share_directory('turtlebot4_description')

    world_path = PathJoinSubstitution([
        pkg_turtlebot4_maze_sim,
        'worlds',
        'maze_world.sdf'
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

    robot_xacro = PathJoinSubstitution([
        pkg_turtlebot4_description,
        'urdf',
        LaunchConfiguration('model'),
        'turtlebot4.urdf.xacro'
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
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': robot_description}
        ],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
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

    world_server = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', world_path],
        output='screen'
    )

    spawn_robot = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'ros_gz_sim', 'create',
            '-world', LaunchConfiguration('world_name'),
            '-file', '/tmp/turtlebot4_maze_robot.urdf',
            '-name', LaunchConfiguration('robot_name'),
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15',
            '-Y', '0.0'
        ],
        output='screen'
    )

    spawn_after_description = RegisterEventHandler(
        OnProcessExit(
            target_action=generate_robot_urdf,
            on_exit=[TimerAction(period=3.0, actions=[spawn_robot])]
        )
    )

    ament_prefixes = [p for p in os.environ.get('AMENT_PREFIX_PATH', '').split(os.pathsep) if p]
    resource_paths = os.pathsep.join([p + '/share' for p in ament_prefixes])
    library_paths = os.pathsep.join([p + '/lib' for p in ament_prefixes])

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_paths),
        SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', library_paths),
        model_arg,
        robot_name_arg,
        world_name_arg,
        LogInfo(msg='Launching TurtleBot4 maze world in Gazebo Harmonic'),
        generate_robot_urdf,
        robot_state_publisher,
        joint_state_publisher,
        world_server,
        spawn_after_description,
    ])
