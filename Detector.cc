#include "Detector.h"
#include <pylon/PylonIncludes.h>
#include <opencv2/opencv.hpp>
#include <iostream>

using namespace std;

using namespace cv;

/*
  Constructor for Detector.
 */
Detector::Detector(string serial1, string serial2) :
  cap1{serial1}, cap2{serial2}, triangulator{"camera1.xml", "camera2.xml", "r_and_t.xml"}
{
}

void Detector::run()
{
  bool running = true;
  Mat frame1;
  Mat frame2;

  Rect bbox1;
  Rect bbox2;

  bool detected1 = false;
  bool detected2 = false;

  namedWindow("Camera1", WINDOW_NORMAL);
  namedWindow("Camera2", WINDOW_NORMAL);

  cap1.start();
  cap2.start();

  cout << "Detector running" << endl;
  
  while(running)
    {
      cap1.grab(frame1);
      cap2.grab(frame2);
      
      if (!frame1.empty() && !frame2.empty())
	{
	  detected1 = color_detection(frame1, bbox1);
	  detected2 = color_detection(frame2, bbox2);
	  
	  if (detected1 && detected2)
	    {
	      Point2f point1 = (bbox1.tl() + bbox1.br()) / 2;
	      Point2f point2 = (bbox2.tl() + bbox2.br()) / 2;

	      Mat pos;
	      triangulator.triangulate(point1, point2, pos);
	      //cout << "Triangulated: " << pos << endl;
	      triangulator.camera2edn(pos, pos, 0.0);
	      cout << pos << endl;
	      Mat gps;
	      Mat ecef_o = (Mat_<double>(3, 1) << 0, 0, 0);
	      pos = pos * 0.001;
	      triangulator.edn2gps(pos, gps, ecef_o);
	      cout << "GPS: " << gps << endl;
	    }
	  imshow("Camera1", frame1);
	  imshow("Camera2", frame2);
	}
	char ch = waitKey(1);
	if (ch == (int) 'q')
	  {
	    running = false;
	  }
    }

  cap1.stop();
  cap2.stop();
  destroyAllWindows();
}

static bool contour_compare(vector<Point> contour1, vector<Point> contour2)
{
  return contourArea(contour1) < contourArea(contour2);
}

bool Detector::color_detection(Mat& img, Rect& boundRect)
{
  int img_w = img.size().width;
  int img_h = img.size().height;
  bool detected = false;

  Mat hsv;

  GaussianBlur(img, hsv, Size(5, 5), 0);

  cvtColor(hsv, hsv, COLOR_BGR2HSV);

  Mat mask1, mask2, mask;
  inRange(hsv, Scalar(0, 120, 120), Scalar(10, 255, 255), mask1);
  inRange(hsv, Scalar(170, 120, 120), Scalar(179, 255, 255), mask2);
  addWeighted(mask1, 1.0, mask2, 1.0, 0.0, mask);

  vector<vector<Point> > contours;
  vector<Vec4i> hierarchy;

  findContours(mask, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE, Point(0, 0));

  if (contours.size() > 0)
    {
      vector<Point> c = * max_element(contours.begin(), contours.end(), contour_compare);
      boundRect = boundingRect(c);

      if (boundRect.area() > 500)
	{
	  detected = true;
	  rectangle(img, boundRect.tl(), boundRect.br(), Scalar(255, 0, 0), 3);
	}
    }
  return detected;
}

int main()
{
  Pylon::PylonAutoInitTerm autoInitTerm;
  
  cout << "Detector.cc" << endl;
  Detector detector("40016577", "21810700");
  detector.run();
  cout << "Run finished" << endl;
  return 0;
}
