#ifndef DETECTOR_H
#define DETECTOR_H

#include "cap.h"
#include "Triangulator.h"


/*
  Defines the Detector class.
 */
class Detector
{
 public:
  Detector(std::string serial1, std::string serial2);
  ~Detector() = default;
  void run();

 private:
  Capture cap1;
  Capture cap2;
  Triangulator triangulator;

  bool color_detection(cv::Mat& img, cv::Rect& boundRect);
};

#endif
