cmake_minimum_required(VERSION 3.8)
project(turtlebot4_maze_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch worlds urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
