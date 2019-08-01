#ifndef TRIANGULATOR_H
#define TRIANGULATOR_H

#include <opencv2/opencv.hpp>

class Triangulator
{
 public:
  Triangulator(std::string camera1_file, std::string camera2_file, std::string r_and_t_file);
  ~Triangulator() = default;

  //private:
  cv::Mat camera_matrix1;
  cv::Mat camera_matrix2;
  cv::Mat R_1to2;
  cv::Mat t_1to2;

  cv::Point3f triangulate(cv::Point2f point1, cv::Point2f point2);
};

#endif
