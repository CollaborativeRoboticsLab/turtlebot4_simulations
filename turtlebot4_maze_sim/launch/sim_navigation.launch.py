from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_turtlebot4_navigation = get_package_share_directory('turtlebot4_navigation')
    pkg_turtlebot4_maze_sim = get_package_share_directory('turtlebot4_maze_sim')

    nav2_params = RewrittenYaml(
        source_file=PathJoinSubstitution([
            pkg_turtlebot4_navigation,
            'config',
            'nav2.yaml'
        ]),
        param_rewrites={
            'cmd_vel_out_topic': 'diffdrive_controller/cmd_vel'
        },
        convert_types=True,
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='turtlebot4',
        description='Robot namespace used by the simulation topics.'
    )

    sync_arg = DeclareLaunchArgument(
        'sync',
        default_value='true',
        choices=['true', 'false'],
        description='Use synchronous SLAM.'
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            pkg_turtlebot4_maze_sim,
            'config',
            'maze.rviz'
        ]),
        description='RViz configuration file.'
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                pkg_turtlebot4_navigation,
                'launch',
                'slam.launch.py'
            ])
        ),
        launch_arguments={
            'namespace': LaunchConfiguration('robot_name'),
            'use_sim_time': 'true',
            'sync': LaunchConfiguration('sync'),
        }.items()
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                pkg_turtlebot4_navigation,
                'launch',
                'nav2.launch.py'
            ])
        ),
        launch_arguments={
            'namespace': LaunchConfiguration('robot_name'),
            'use_sim_time': 'true',
            'params_file': nav2_params,
        }.items()
    )

    rviz_launch = GroupAction([
        PushRosNamespace(LaunchConfiguration('robot_name')),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            parameters=[{'use_sim_time': True}],
            remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
            output='screen'
        ),
    ])

    return LaunchDescription([
        robot_name_arg,
        sync_arg,
        rviz_config_arg,
        slam_launch,
        nav2_launch,
        rviz_launch,
    ])