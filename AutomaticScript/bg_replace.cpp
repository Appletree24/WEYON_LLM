/**
@ name:	 bg_replace.cpp
@ author:	 Appletree24(张子辉)
@ email:	 1246908638zxc@gmail.com
@ description: 替换绿幕背景为用户自定义
@ version:	 1.0
@ time:	2024/07/31 11:52
请不要用GPT生成代码中的注释，谢谢
**/

#include <opencv2/opencv.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudafilters.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <opencv2/cudawarping.hpp>
#include <iostream>

using namespace cv;
using namespace cv::cuda;

void replaceAndBlend(const Mat &frame, const Mat &mask, const Mat &bgimg, Mat &result)
{
    result = Mat::zeros(frame.size(), frame.type());
    int h = frame.rows;
    int w = frame.cols;

    for (int row = 0; row < h; ++row)
    {
        for (int col = 0; col < w; ++col)
        {
            uchar m = mask.at<uchar>(row, col);
            if (m == 255)
            {
                result.at<Vec3b>(row, col) = bgimg.at<Vec3b>(row, col);
            }
            else if (m == 0)
            {
                result.at<Vec3b>(row, col) = frame.at<Vec3b>(row, col);
            }
            else
            {
                float alpha = m / 255.0f;
                float beta = 1.0f - alpha;
                Vec3b b1 = bgimg.at<Vec3b>(row, col);
                Vec3b b2 = frame.at<Vec3b>(row, col);
                Vec3b b;
                b[0] = static_cast<uchar>(b1[0] * alpha + b2[0] * beta);
                b[1] = static_cast<uchar>(b1[1] * alpha + b2[1] * beta);
                b[2] = static_cast<uchar>(b1[2] * alpha + b2[2] * beta);
                result.at<Vec3b>(row, col) = b;
            }
        }
    }
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <video_path> <background_image_path>" << std::endl;
        return -1;
    }

    std::string videoPath = argv[1];
    std::string bgimgPath = argv[2];

    Mat bgimg = imread(bgimgPath);
    if (bgimg.empty())
    {
        std::cerr << "Background image not found: " << bgimgPath << std::endl;
        return -1;
    }

    VideoCapture cap(videoPath);
    if (!cap.isOpened())
    {
        std::cerr << "Video not found: " << videoPath << std::endl;
        return -1;
    }

    int frameWidth = static_cast<int>(cap.get(CAP_PROP_FRAME_WIDTH));
    int frameHeight = static_cast<int>(cap.get(CAP_PROP_FRAME_HEIGHT));

    cv::resize(bgimg, bgimg, Size(frameWidth, frameHeight));

    GpuMat bgimgGpu;
    bgimgGpu.upload(bgimg);

    VideoWriter out("output.avi", VideoWriter::fourcc('X', 'V', 'I', 'D'), 20.0, Size(frameWidth, frameHeight));

    int frameCount = 0;
    int frameCountAll = static_cast<int>(cap.get(CAP_PROP_FRAME_COUNT));
    std::cout << "视频总帧数为: " << frameCountAll << std::endl;

    Mat frame, hsv, mask, result;
    GpuMat frameGpu, hsvGpu, maskGpu;

    while (cap.isOpened())
    {
        bool ret = cap.read(frame);
        if (!ret)
        {
            std::cout << "End of video reached or error reading frame." << std::endl;
            break;
        }

        frameCount++;
        std::cout << "Processing frame " << frameCount << std::endl;

        frameGpu.upload(frame);

        cuda::cvtColor(frameGpu, hsvGpu, COLOR_BGR2HSV);
        cuda::inRange(hsvGpu, Scalar(35, 43, 46), Scalar(77, 255, 255), maskGpu);

        Ptr<cuda::Filter> morphFilter = cuda::createMorphologyFilter(MORPH_OPEN, maskGpu.type(), getStructuringElement(MORPH_RECT, Size(5, 5)));
        morphFilter->apply(maskGpu, maskGpu);

        Ptr<cuda::Filter> gaussianFilter = cuda::createGaussianFilter(maskGpu.type(), maskGpu.type(), Size(5, 5), 0);
        gaussianFilter->apply(maskGpu, maskGpu);

        maskGpu.download(mask);
        replaceAndBlend(frame, mask, bgimg, result);
        out.write(result);
    }

    std::cout << "Releasing resources." << std::endl;
    cap.release();
    out.release();

    return 0;
}
