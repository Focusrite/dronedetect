#include "Triangulator.h"
#include <opencv2/opencv.hpp>
#include <cmath>

using namespace std;

using namespace cv;

Triangulator::Triangulator(std::string camera1_file, std::string camera2_file, std::string r_and_t_file)
{
  FileStorage fs1(camera1_file, FileStorage::READ);
  FileStorage fs2(camera2_file, FileStorage::READ);
  FileStorage fs3(r_and_t_file, FileStorage::READ);
  fs1["cameramatrix"] >> camera_matrix1;
  fs2["cameramatrix"] >> camera_matrix2;
  fs3["R"] >> R_1to2;
  fs3["t"] >> t_1to2;
  fs1.release();
  fs2.release();
  fs3.release();

  camera_matrix1.convertTo(camera_matrix1, CV_32FC1);
  camera_matrix2.convertTo(camera_matrix2, CV_32FC1);
  R_1to2.convertTo(R_1to2, CV_32FC1);
  t_1to2.convertTo(t_1to2, CV_32FC1);
}

void Triangulator::triangulate(Point2f point1, Point2f point2, Mat& coords)
{
  Mat mat;
  hconcat(Mat::eye(3, 3, CV_32FC1), Mat::zeros(3, 1, CV_32FC1), mat);
  Mat proj_matrix1 = camera_matrix1 * mat;
  Mat mat2;
  hconcat(R_1to2, t_1to2, mat2);
  Mat proj_matrix2 = camera_matrix2 * mat2;
  
  vector<Point2f> points1;
  points1.push_back(point1);
  vector<Point2f> points2;
  points2.push_back(point2);

  Mat points4d;

  triangulatePoints(proj_matrix1, proj_matrix2, points1, points2, points4d);
  points4d = points4d / points4d.at<float>(0, 3);
  
  coords = points4d.colRange(0, 1).rowRange(0, 3).clone();

}

void Triangulator::camera2edn(Mat& camera_coords, Mat& edn_coords, double angle)
{
  double cosine = cos(-1 * angle);
  double sine = sin(-1 * angle);

  Mat R = Mat::eye(3, 3, CV_32FC1);
  R.at<float>(0, 0) = cosine;
  R.at<float>(2, 0) = sine;
  R.at<float>(1, 1) = 1;
  R.at<float>(0, 2) = -1 * sine;
  R.at<float>(2, 2) = cosine;

  edn_coords = R * camera_coords;
}

void Triangulator::edn2gps(Mat& edn_coords, Mat& gps_coords, Mat& enu_origin)
{
  cout << "edn2gps" << endl;
  const double pi = 3.1415926535897;
  
  const double a = 6378137; // Equatorial radius of the earth [m]
  const double e2 = 0.00669437999; // e = eccentricity of ellipsoid
  const double b = a * sqrt(1 - e2); // Polar radius of the earth

  double lat_o = enu_origin.at<double>(0, 0);
  double long_o = enu_origin.at<double>(0, 1);
  double alt_o = enu_origin.at<double>(0, 2);

  double lat_sin = sin(pi * lat_o / 180.0);
  double lat_cos = cos(pi * lat_o / 180.0);
  double long_sin = sin(pi * long_o / 180.0);
  double long_cos = cos(pi * long_o / 180.0);

  // Prime vertical radius of curvature at the given latitude
  const double N = a / sqrt(1 - e2 * pow(lat_sin, 2));

  // Calculate the ECEF coordinates of the EDN origin
  double X_o = (N + alt_o) * lat_cos * long_cos;
  double Y_o = (N + alt_o) * lat_cos * long_sin;
  double Z_o = (pow(b, 2) / pow(a, 2) * N + alt_o) * lat_sin;
  Mat ecef_o = (Mat_<double>(3, 1) << X_o, Y_o, Z_o);

  // Rotation matrix for conversion between ENU and ECEF
  Mat R = (Mat_<double>(3, 3) <<
	   -long_sin, -lat_sin * long_cos, lat_cos * long_cos,
	   long_cos, -lat_sin * long_sin, lat_cos * long_sin,
	   0, lat_cos, lat_sin);

  // Rotation matrix for conversion between EDN and ENU
  Mat R_enu = (Mat_<double>(3, 3) <<
	       1, 0, 0,
	       0, 0, 1,
	       0, -1, 0);

  // We need to convert edn_coords from float to double
  Mat edn_double;
  edn_coords.convertTo(edn_double, CV_64FC1);
  
  // Convert from EDN to ENU coordinates
  Mat enu = R_enu * edn_double;

  // Convert from ENU to ECEF coordinates
  Mat ecef = R * enu + ecef_o;

  // Calculate some help variables
  double ep = e2 / (1 - e2);
  double p = sqrt(pow(ecef.at<double>(0, 0), 2) +
		  pow(ecef.at<double>(0, 1), 2));
  double th = atan2(a * ecef.at<double>(2, 0), b * p);

  // Convert from ECEF to gps coordinates
  double lon = atan2(ecef.at<double>(0, 1), ecef.at<double>(0, 0));
  double lat = atan2(ecef.at<double>(0, 2) + ep * b * pow(sin(th), 3),
		     p - e2 * a * pow(cos(th), 3));

  double v = a / sqrt(1 - e2 * pow(sin(lat), 2));
  double alt = p / cos(lat) - v;

  // Convert from radians to degrees
  lat = lat * 180.0 / pi;
  lon = lon * 180.0 / pi;

  gps_coords = (Mat_<double>(3, 1) << lat, lon, alt);
}
