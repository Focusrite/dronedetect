#ifndef CAP_H
#define CAP_H

#include <pylon/PylonIncludes.h>
#include <opencv2/opencv.hpp>

class Capture
{
 public:
  Capture(std::string serial);
  ~Capture() = default;
  void start();
  void grab(cv::Mat& img);
  void stop();
 private:
  Pylon::CInstantCamera camera;
  Pylon::CImageFormatConverter converter;
  Pylon::CGrabResultPtr ptrGrabResult;
  void connect(std::string serial);
};

#endif
