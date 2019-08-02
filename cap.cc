#include "cap.h"
#include <pylon/PylonImage.h>
#include "opencv2/core/core.hpp"

using namespace std;

using namespace Pylon;

Capture::Capture(std::string serial)
{
  try
  {
    CTlFactory& tlFactory = CTlFactory::GetInstance();
    DeviceInfoList_t devices;
    tlFactory.EnumerateDevices(devices);
    for (auto& device : devices)
      {
	if (device.GetSerialNumber() == String_t(serial.c_str()))
	  {
	    camera.Attach(tlFactory.CreateDevice(device));
	  }
      }
    camera.Open();

    cout << "Using device " << camera.GetDeviceInfo().GetModelName() << endl;
    converter.OutputPixelFormat = PixelType_BGR8packed;
    converter.OutputBitAlignment = OutputBitAlignment_MsbAligned;
  }
  catch (GenICam::GenericException & e)
  {
    //camera = nullptr;
    cerr << "An exception occurred" << endl;
    cout << e.GetDescription() << endl;
    exit(1);
  }
}

void Capture::start()
{
  GenApi::INodeMap& nodemap = camera.GetNodeMap();
  CEnumParameter gainAuto(nodemap, "GainAuto");
  gainAuto.TrySetValue("Continuous");
  camera.StartGrabbing(Pylon::GrabStrategy_LatestImageOnly);
}

void Capture::grab(cv::Mat& img)
{
  if (!camera.IsGrabbing())
    {
      cout << "Error: Not grabbing" << endl;
      return;
    }
  CPylonImage image;
  camera.RetrieveResult(1000, ptrGrabResult, TimeoutHandling_ThrowException);
  if (ptrGrabResult->GrabSucceeded())
    {
      converter.Convert(image, ptrGrabResult);

      img = cv::Mat(ptrGrabResult->GetHeight(), ptrGrabResult->GetWidth(), CV_8UC3);
      memcpy(img.ptr(), image.GetBuffer(), ptrGrabResult->GetHeight() * ptrGrabResult->GetWidth() * 3);
      /*
      cv::namedWindow("TEST", cv::WINDOW_NORMAL);
      cv::imshow("TEST", img);
      cv::waitKey(3000);*/
    }
}

void Capture::stop()
{
  camera.StopGrabbing();
  camera.Close();
}
/*
int main()
{
  cv::Mat img;
  if (img.empty())
    {
      cout << "Image empty at start" << endl;
    }
  
  Pylon::PylonAutoInitTerm autoInitTerm;
  
  Capture cap("40016577");
  cap.start();
  cap.grab(img);

  if (img.empty())
    {
      cout << "Empty frame" << endl;
    }

  cout << "Size: " << img.size << endl;

  //cv::imwrite("test_IMAGE.png", img);
  
  cv::Mat hsv;
  //cv::cvtColor(img, hsv, cv::COLOR_BGR2HSV);
  
  cv::namedWindow("test", cv::WINDOW_NORMAL);
  cout << "Named window" << endl;
  cv::imshow("test", img);
  cout << "Imshow" << endl;
  cv::waitKey(5000);

  cap.stop();

  return 0;
}
*/
