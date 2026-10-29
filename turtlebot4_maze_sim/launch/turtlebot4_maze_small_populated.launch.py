from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    package = get_package_share_directory('turtlebot4_maze_sim')
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                package, 'launch', 'turtlebot4_maze_small.launch.py'
            ])),
            launch_arguments={
                'world_path': PathJoinSubstitution([
                    package, 'worlds', 'maze_world_small_populated.sdf'
                ])
            }.items()
        )
    ])