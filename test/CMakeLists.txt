cmake_minimum_required (VERSION 3.2)
project (Test)
SET("OpenCV_DIR" "/user/sommarjobb/opencv/opencv")
find_package(OpenCV REQUIRED)



add_executable (Test color_matching.cc)
target_link_libraries(Test ${OpenCV_LIBS})
