# Connected-Steps-Project

File content:
* Microsoft_Dataset_Plot2.py: credit to Mehrdad <br />
         This file extracts walking trips information from original Microsoft dataset. The program only use users with transportation labels, and only considered location data that were label as "walking". The program created folders of CSV files, each CSV file representes a trip, containing information of latitude, longitude, and timestamp; and each folder represents a distinct user.
         
* Smooth and SP detection.ipynb:<br />
        This file uses the CSV folders generated with Microsoft_Dataset_Plot2.py, applying stay point detection (Credit to Runze) and B-Spline (Credit to Mehrdad), and generates           smoothed trajectory plots for each CSV trip.
        
* Make prediction.ipynb:<br />
        This file takes the trajectory plots generated from Smooth and SP detection.ipynb, feeding the image to pretrained MNIST dataset model, and output the predicted digit (0-9) for each plot. 
