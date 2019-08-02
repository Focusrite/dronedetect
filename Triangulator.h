#ifndef TRIANGULATOR_H
#define TRIANGULATOR_H

#include <opencv2/opencv.hpp>

class Triangulator
{
 public:
  Triangulator(std::string camera1_file, std::string camera2_file, std::string r_and_t_file);
  ~Triangulator() = default;
  void triangulate(cv::Point2f point1, cv::Point2f point2, cv::Mat& coords);
  void camera2edn(cv::Mat& camera_coords, cv::Mat& edn_coords, double angle);
  void edn2gps(cv::Mat& edn_coords, cv::Mat& gps_coords, cv::Mat & enu_origin);

 private:
  cv::Mat camera_matrix1;
  cv::Mat camera_matrix2;
  cv::Mat R_1to2;
  cv::Mat t_1to2;

};

#endif
