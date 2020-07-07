# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:50:58 2020

@author: 14342
"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import re
from mpl_toolkits import mplot3d
import pandas as pd
import os
import glob
from pathlib import Path
from scipy.interpolate import splprep, splev
from pathlib import Path

import warnings
warnings.filterwarnings("ignore")

n_users = 182
column_names = ["Latitude", "Longitude", "Zeros", "Altitude", "Unix_Day", "Date", "Time"]
smoothing_coeff = 1e-10
save_plots_here = './Figs/Walking/Smoothed_2/'

# def plotLocation(path):
#     data = np.genfromtxt(path, delimiter=',', dtype=(float, float, float,float,float,object,object),skip_header=6)

#     latitude = []
#     longitude=[]
#     time_list = []
                         
#     for row in data:
        
#         date = row[5].decode("utf-8") + " " + row[6].decode("utf-8")
#         my_time = time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')) # convert to timestamp
        
#         ts = pd.to_datetime(my_time, unit='s')
#         hour = ts.hour
        
#         latitude.append(row[0])
#         longitude.append(row[1])


#         time_list.append(ts.hour)
                         
#     return latitude, longitude,time_list


# def lat_long_time(user, file_name):

#     latitude = user[file_name]["Latitude"]
#     longitude = user[file_name]["Longitude"]
#     time = user[file_name]["Time"]
                         
#     return latitude, longitude, time


# def read_all_trajectories():
    
#     all_users = []
#     is_label = []
    
#     users_strings = ["{0:03}".format(i) for i in range(n_users)]

#     for i in range(n_users):
#         print("reading user {} data".format(i+1))
#         all_users.append({})
#         user_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + users_strings[i]
#         user_data_dir = user_dir + "\\Trajectory\\"
        
#         my_label = Path(user_dir + '\labels.txt')
#         is_label.append(my_label.is_file())
        
#         data_list = glob.glob(user_data_dir + "*.plt")
                
#         for j in range(len(data_list)):
#             file_key = data_list[j][101:115]
#             all_users[i][file_key] = pd.read_csv(data_list[j], names= column_names, skiprows=6)
    
#     return all_users, is_label

def scan_trj_label():
    """
    This function scans the trajectory files and labels for all users and returns
    trajectories filenames and whether or not a user has a label file

    Returns
    -------
    all_users_trj : List of List
        Each element corresponds to one user and is itself a list of all trajectory
        filenames of that user.
    is_label : List
        A boolean list that is True is the user has a label file and is False otherwise.

    """
    all_users_trj = []
    is_label = []
    
    users_strings = ["{0:03}".format(i) for i in range(n_users)]

    for i in range(n_users):
        print("reading user {} data".format(i+1))
        all_users_trj.append([])
        user_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + users_strings[i]
        user_data_dir = user_dir + "\\Trajectory\\"
        
        my_label = Path(user_dir + '\labels.txt')
        is_label.append(my_label.is_file())
        
        data_list = glob.glob(user_data_dir + "*.plt")
                
        for j in range(len(data_list)):
            file_key = data_list[j][101:115]
            all_users_trj[i].append(file_key)
            #all_users[i][file_key] = pd.read_csv(data_list[j], names= column_names, skiprows=6)
    
    return all_users_trj, is_label


# def read_one_user_trajectories(m):
    
#     user = {}
#     user_string = "{0:03}".format(m)
#     user_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + user_string
#     user_data_dir = user_dir + "\\Trajectory\\"
#     data_list = glob.glob(user_data_dir + "*.plt")
    
#     for j in range(len(data_list)):
#         file_key = data_list[j][101:115]
#         user[file_key] = pd.read_csv(data_list[j], names= column_names, skiprows=6)
        
#     return user

# def plot_user_file(user_id, file_name):
#     user  = read_one_user_trajectories(user_id)
#     lat, long, time = lat_long_time(user, file_name)
#     #long, time = lat_long_time(user_10,'20070804033032')
#     fig = plt.figure(figsize=(15,15))
#     ax = fig.add_subplot(2, 2, 1)
#     ax.scatter(long, lat)
    
#     return

def lat_long_extract(user_id, user_trj_list, start_time, end_time):
    """
    This function extracts the relevant latitudes and longitudes of one specific
    trip from the user "user_id" with a given start time and end time. The function
    scans all the trajectory files and determine which one could contain the location
    data pertaining to that trip and reads that file and extracts the data 
    corresponding to the trip if exist.

    Parameters
    ----------
    user_id : integer
        index of the user we are interested in.
    user_trj_list : list of list
        Each element corresponds to one user and is itself a list of all trajectory
        filenames of that user.
    start_time : integer
        start time of the trip.
    end_time : integer
        end time of the trip.

    Returns
    -------
    trip_lat : numpy.array
        latitudes.
    trip_long : numpy.array
        longitute.
    trip_lat_s : numpy.array
        smoothed latitude.
    trip_long_s : numpy.array
        smoothed longitude.

    """
    # Finding the file_id_to_read out of all trajectory files based on the start_time
    # of the trip
    file_id_to_read = 0
    for i in range(len(user_trj_list)):
        if int(user_trj_list[i]) <= start_time:
            file_id_to_read = i
        else:
            break;
    
    # Setting up the address to file to be read
    user_string = "{0:03}".format(user_id)
    trj_file_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + user_string \
        + "\\Trajectory\\" + user_trj_list[file_id_to_read] + ".plt"
    
    # Reading the file that could possibly have trajectory data of desired trip
    trj_df = pd.read_csv(trj_file_dir, names=column_names, skiprows=6)
    trj_df['DateTime'] = 0
    last_row_id = len(trj_df) - 1
    
    # Creating a DateTime column to hold the integer value of the date and time
    for i in range(len(trj_df)):
        trj_df['DateTime'][i] = int(trj_df.Date[i].replace('-','') + trj_df.Time[i].replace(':',''))
    
    # Determining if the start_time and end_time of the trip exist in the trajectory file
    is_start_time = (trj_df['DateTime'][0] <= start_time and trj_df['DateTime'][last_row_id] > start_time)
    is_end_time = (trj_df['DateTime'][0] < end_time and trj_df['DateTime'][last_row_id] >= end_time)
    
    # Obtaining the first row and last row of the trajectory file to read
    start_row_read = 0
    end_row_read = 0
    
    if is_start_time == True:
        for i in range(len(trj_df)):
            if trj_df['DateTime'][i] >= start_time:
                start_row_read = i
                break;
    
    if is_end_time == True:
        for i in range(start_row_read,len(trj_df)):
            if trj_df['DateTime'][i] > end_time:
                end_row_read = i - 1
                break;
    else:
        end_row_read = last_row_id
    
    # Slicing the dataframe of trajectory from "start_row_read" to "end_row_read"
    trj_df = trj_df.iloc[start_row_read:end_row_read,:]
    trj_df.reset_index(drop=True, inplace=True)
    
    trip_lat = trj_df['Latitude'].values
    trip_long = trj_df['Longitude'].values
    trip_timestamp = trj_df['DateTime']
    
    # Getting the smoothed trip long and lat
    trip_long_s, trip_lat_s = trj_smoothing(trj_df)
    
    # Selecting which columns to include in the processsed data
    trj_df = trj_df[['DateTime', 'Latitude','Longitude']]
    
    return trip_lat, trip_long, trip_lat_s, trip_long_s, trip_timestamp, trj_df

def plot_trajectory(lat, long, lat_s, long_s, trip_id,plot_save_dir = None):
    """
    This function takes latitude and longitute and smoothed latitude and longitude
    values and plots them side by side.

    Parameters
    ----------
    lat : numpy.array
        latitudes.
    long : numpy.array
        longitute.
    lat_s : numpy.array
        smoothed latitude.
    long_s : numpy.array
        smoothed longitude.

    Returns
    -------
    None.

    """
    fig = plt.figure(figsize=(30,15))
    #fig.suptitle('Walking trip at DateTime {}'.format(start_time), fontsize=20)
    
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(long, lat)
    ax1.set_xlabel('Longitude', fontsize=18)
    ax1.set_xlabel('Latitude', fontsize=18)
    
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(long_s, lat_s)
    ax2.set_xlabel('Longitude', fontsize=18)
    ax2.set_xlabel('Latitude', fontsize=18)
    
    
    if plot_save_dir is not None:
        fig.savefig(plot_save_dir + 'User_{}_{}_Smoothed.png'.format(user_id, trip_id))
    return

def read_label(user_id, target_label, all_users_trj, plot_save_dir = None):
    # """
    # This function takes user_id and target_label and trajectory filenames of 
    # all users ("all_users_trj") and reads the label file of that user and extracts
    # all the trips with that target_label. Then it returns the dataframe of the 
    # trimmed label file with start time and end time in integer format.

    # Parameters
    # ----------
    # user_id : Integer
    #     index of the user we are interested in. (The user must have a label
    #                                                    file).
    # target_label : String 
    #     Transportation mode of the user. This should match the labels in the label
    #     file (i.e. 'walk', 'bus', 'subway', 'train', 'taxi', 'car')
    # all_users_trj : List of List
    #     Each element corresponds to one user and is itself a list of all trajectory
    #     filenames of that user.
    # plot_save_dir : Sting, optional
    #     A string addressing the directory that plots are going to be saved (i.e.
    #     'C:\User\Desktop'). The default is None.

    # Returns
    # -------
    # labels_df_select : Dataframe
    #     Dataframe of the label file.

    # """
    user_string = "{0:03}".format(user_id)    
    label_path = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" \
        + user_string + '\labels.txt'
    
    label_columns = ['StartDateTime', 'EndDateTime', 'Transportation']
    labels_df = pd.read_csv(label_path, delimiter='\t', names=label_columns, skiprows=1)
    
    labels_df['StartTime_int'] = 0
    labels_df['EndTime_int'] = 0
    
    # Converting date and time to an integer (like the name of the trajectory files)
    for i in range(len(labels_df)):
        labels_df['StartTime_int'][i] = labels_df['StartDateTime'][i].replace(' ','').replace('/','').replace(':','')
        labels_df['EndTime_int'][i] = labels_df['EndDateTime'][i].replace(' ','').replace('/','').replace(':','')
    
    labels_df_select = labels_df[labels_df['Transportation'] == target_label]
    labels_df_select.reset_index(drop=True, inplace=True)
    
    return labels_df_select


def trj_smoothing(trj_df):
    """
    This function take a dataframe containing latitudes and longitudes and 
    returns smoothed lat and long. This function uses B-splines from scipy
    library to do the smoothing. Smoothing can be controlled via a smoothing
    factor. Note that "smoothing_coeff" is defined as a global variable!

    Parameters
    ----------
    trj_df : Dataframe
        A dataframe with at least two columns of "Latitude" and "Longitude".

    Returns
    -------
    long_s: numpy.array
        Smoothed longitudes.
    lat_s: numpy.array
        Smoothed latitudes.

    """
    
    trj_df = trj_df.drop_duplicates(subset=['Latitude', 'Longitude'], keep='first')
    
    lat = trj_df['Latitude'].values
    long = trj_df['Longitude'].values
    
    trip_len = len(lat)
    if trip_len <= 5:
        return lat, long
    
    smoothing_factor = smoothing_coeff*trip_len
    tck, u = splprep([long, lat], s=smoothing_factor, k=5)
    new_points = splev(u, tck)
    
    long_s = new_points[0]
    lat_s = new_points[1]
    
    return long_s, lat_s
    
    
if __name__ == "__main__":
    
    avail_labels = ['walk', 'bus', 'train', 'taxi', 'subway', 'car', 'airplane', 'bike']
    
    # "all_users_trj" is a 2D list that holds all the trajectory filenames of 
    # all users (182 in total). "is_label" is boolean list of 182 elements with
    # "True" is the user has a label file and "False" otherwise
    all_users_trj, is_label = scan_trj_label()
    
    # "users_with_label" holds the indecies of the users who have labels
    users_with_label = [i for i, x in enumerate(is_label) if x == True]
    user_id = users_with_label[0]
    
    # # Getting all the entries of the target label (i.e. 'walk') from the label file
    # labels_df_select = read_label(user_id, 'walk', all_users_trj)
    
    # looping over all trips of target label and plotting them
    plot_save_dir = None
    
    for j in users_with_label:
        print(j)
        for l in avail_labels:
            # Getting all the entries of the target label (i.e. 'walk') from the label file
            labels_df_select = read_label(j, l, all_users_trj)
            
            THE_PATH = os.getcwd() + '\\Preprocessed-Users-Data\\user_%d\\%s'%(j,l)
            
            Path(THE_PATH).mkdir(parents=True, exist_ok=True)
            
            for i in range(len(labels_df_select)):
            # for i in range(3):

                lat, long, lat_s, long_s, timestamp, trip_df = \
                    lat_long_extract(user_id, all_users_trj[user_id],\
                                     labels_df_select['StartTime_int'][i],\
                                         labels_df_select['EndTime_int'][i])
                
                csv_path = THE_PATH + '\\%d.csv'%(i)
                trip_df.to_csv(csv_path)
                
                # if len(lat) > 3:
                #     plot_trajectory(lat, long, lat_s, long_s, i, save_plots_here)

    
    

