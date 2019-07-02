#include <opencv2/opencv.hpp>
#include <iostream>
#include <algorithm>

using namespace cv;
using namespace std;

// Comparison function for contour areas
static bool contour_compare(vector<Point> contour1, vector<Point> contour2)
{
  return contourArea(contour1) < contourArea(contour2);
}

/*
 * Returns true if a red area of sufficiently large size is detected.
 * Calculates the offset in pixels from the image center for the
 * detected red area center.
 */
bool color_matching(Mat& img, int& x_offset, int& y_offset)
{
  int img_w = img.size().width;
  int img_h = img.size().height;
  bool detected = false;
  
  Mat hsv;

  // Blur image
  GaussianBlur(img, hsv, Size(5, 5), 0);

  // Convert to HSV color space
  cvtColor(hsv, hsv, COLOR_BGR2HSV);

  // Mask out the red areas in the image
  Mat mask1, mask2, mask;
  inRange(hsv, Scalar(0, 120, 120), Scalar(10, 255, 255), mask1);
  inRange(hsv, Scalar(170, 120, 120), Scalar(179, 255, 255), mask2);
  addWeighted(mask1, 1.0, mask2, 1.0, 0.0, mask);

  vector<vector<Point> > contours;
  vector<Vec4i> hierarchy;

  // Find contours of the image
  findContours(mask, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE, Point(0, 0));

  if (contours.size() > 0)
    {
      // Find the contour with the largest area, and find the smallest bounding box
      vector<Point> c = * max_element(contours.begin(), contours.end(), contour_compare);
      Rect boundRect = boundingRect(c);

      if (boundRect.area() > 500)
	{
	  detected = true;
	  rectangle(img, boundRect.tl(), boundRect.br(), Scalar(255, 0, 0), 3);

	  // Find the offset
	  x_offset = int((boundRect.br().x + boundRect.tl().x - img_w) / 2);
	  y_offset = (img_h - boundRect.tl().y - boundRect.br().y) / 2;
	}
    }

  return detected;
}
int main()
{
  std::cout << "TESTING" << std::endl;

  Mat image = imread("../../test3.png");
  //Rect boundingRect;

  VideoCapture cap;

  if (!cap.open(0))
    {
      cout << "Camera not found" << endl;
      return 0;
    }

  for (;;)
    {
      Mat frame;
      cap >> frame;
      if (frame.empty())
	break;

      int x_offset, y_offset;

      bool found = color_matching(frame, x_offset, y_offset);
      namedWindow("TEST", WINDOW_NORMAL);
      imshow("TEST", frame);

      if (waitKey(20) == 27) break; // stop by pressing ESC
    }

  return 0;
}
