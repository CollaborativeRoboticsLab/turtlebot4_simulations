# TurtleBot4 Maze Simulations

Gazebo Harmonic based simulations for TurtleBot4, contains following,

| Simulation | Description | Package | Launch File |
|------------|-------------|---------|-------------|
| TurtleBot4 Maze | Standard TurtleBot4 in maze world | turtlebot4_maze_sim | turtlebot4_maze.launch.py |

## Build

From the root of a ROS 2 Jazzy workspace containing this repository:

```bash
colcon build
source install/setup.bash
```

## Launch

Start the standard TurtleBot4 model:

```bash
ros2 launch turtlebot4_maze_sim turtlebot4_maze.launch.py
```