# GeoVisionAI- AI-Based Frame Interpolation, Video Generation, and Display System for WMS Services

## Overview

This project focuses on AI-driven video generation using frame interpolation techniques for satellite imagery obtained from a Web Map Service (WMS). It generates smooth videos from images received at regular intervals (e.g., every 30 minutes) by interpolating frames at finer time steps (e.g., every minute). The final output is displayed on an interactive web-based map using OpenLayers or Leaflet.

## Problem Statement

Given a WMS service that provides satellite imagery at regular intervals within a specified bounding box, the objective is to generate a video by creating intermediate frames between consecutive images. This is particularly challenging for dynamic elements such as clouds, which deform and change between frames. The final video should be overlaid on an open-source WebGIS library for visualization.

## Features

- **Frame Interpolation Model**: A neural network model generates intermediate frames between two consecutive images.
- **WMS Data Fetching**: Retrieves satellite images from a WMS service at specified timestamps.
- **Video Generation**: Creates an MP4 video from retrieved and interpolated frames.
- **GPU Acceleration**: Utilizes GPU for faster processing when available.
- **WebGIS Integration**: Displays the generated video on an interactive web map using OpenLayers or Leaflet.

## Components

### **FrameInterpolator (Neural Network Model)**

- A convolutional neural network (CNN) designed to generate an intermediate frame between two given frames.
- Encoder-decoder architecture utilizing convolutional and deconvolutional layers.
- Uses ReLU activations and a sigmoid output for pixel intensity predictions.

### **WMSVideoGenerator**

- Fetches satellite images from a WMS service at given timestamps.
- Uses the interpolation model to create intermediate frames.
- Combines all frames into a smooth video output.

## Algorithm Workflow

1. Define the WMS service URL, layer name, bounding box, and image dimensions.
2. Retrieve satellite images at specified time intervals.
3. Convert images to tensors and normalize them.
4. Use the neural network to generate intermediate frames.
5. Convert frames back to image format and store them.
6. Generate an MP4 video with smooth transitions between frames.
7. Overlay the video on an OpenLayers or Leaflet-based map for interactive visualization.

## Future Enhancements

- Improve model accuracy for handling object deformations (e.g., cloud motion).
- Optimize performance with enhanced GPU utilization.
- Expand support for different WMS services and video formats.
- Implement real-time rendering for dynamic data updates.
