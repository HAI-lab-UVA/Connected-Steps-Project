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

n_users = 182
column_names = ["Latitude", "Longitude", "Zeros", "Altitude", "Unix_Day", "Date", "Time"]

def plotLocation(path):
    data = np.genfromtxt(path, delimiter=',', dtype=(float, float, float,float,float,object,object),skip_header=6)

    latitude = []
    longitude=[]
    time_list = []
                         
    for row in data:
        
        date = row[5].decode("utf-8") + " " + row[6].decode("utf-8")
        my_time = time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')) # convert to timestamp
        
        ts = pd.to_datetime(my_time, unit='s')
        hour = ts.hour
        
        latitude.append(row[0])
        longitude.append(row[1])


        time_list.append(ts.hour)
                         
    return latitude, longitude,time_list


def lat_long_time(user, file_name):

    latitude = user[file_name]["Latitude"]
    longitude = user[file_name]["Longitude"]
    time = user[file_name]["Time"]
                         
    return latitude, longitude, time


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


def read_one_user_trajectories(m):
    
    user = {}
    user_string = "{0:03}".format(m)
    user_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + user_string
    user_data_dir = user_dir + "\\Trajectory\\"
    data_list = glob.glob(user_data_dir + "*.plt")
    
    for j in range(len(data_list)):
        file_key = data_list[j][101:115]
        user[file_key] = pd.read_csv(data_list[j], names= column_names, skiprows=6)
        
    return user

def plot_user_file(user_id, file_name):
    user  = read_one_user_trajectories(user_id)
    lat, long, time = lat_long_time(user, file_name)
    #long, time = lat_long_time(user_10,'20070804033032')
    fig = plt.figure(figsize=(15,15))
    ax = fig.add_subplot(2, 2, 1)
    ax.scatter(long, lat)
    
    return

def plot_walking_trip(user_id, user_trj_all, start_time, end_time, trip_id):
    
    file_id_to_read = 0
    for i in range(len(user_trj_all)):
        if int(user_trj_all[i]) <= start_time:
            file_id_to_read = i
        else:
            break;
    
    user_string = "{0:03}".format(user_id)
    trj_file_dir = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" + user_string \
        + "\\Trajectory\\" + user_trj_all[file_id_to_read] + ".plt"
    
    trj_df = pd.read_csv(trj_file_dir, names=column_names, skiprows=6)
    trj_df['DateTime'] = 0
    last_row_id = len(trj_df) - 1
    
    for i in range(len(trj_df)):
        trj_df['DateTime'][i] = int(trj_df.Date[i].replace('-','') + trj_df.Time[i].replace(':',''))
    
    is_start_time = (trj_df['DateTime'][0] <= start_time and trj_df['DateTime'][last_row_id] >= start_time)
    is_end_time = (trj_df['DateTime'][0] <= end_time and trj_df['DateTime'][last_row_id] >= end_time)
    
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
    
    trip_lat = trj_df["Latitude"][start_row_read:end_row_read]
    trip_long = trj_df["Longitude"][start_row_read:end_row_read]
    
    fig = plt.figure(figsize=(15,15))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(trip_long, trip_lat)
    fig.suptitle('Walking trip at DateTime {}'.format(start_time), fontsize=20)
    ax.set_xlabel('Longitude', fontsize=18)
    ax.set_xlabel('Latitude', fontsize=18)
    fig.savefig('./Figs/Walking/User_{}_{}.png'.format(user_id, trip_id))
    

def read_label(user_id, target_label, all_users_trj):
    
    user_string = "{0:03}".format(user_id)    
    label_path = os.getcwd() + "\\Geolife Trajectories 1.3\\Data\\" \
        + user_string + '\labels.txt'
    
    label_columns = ['StartDateTime', 'EndDateTime', 'Transportation']
    labels_df = pd.read_csv(label_path, delimiter='\t', names=label_columns, skiprows=1)
    
    labels_df['StartTime_int'] = 0
    labels_df['EndTime_int'] = 0
    
    for i in range(len(labels_df)):
        labels_df['StartTime_int'][i] = labels_df['StartDateTime'][i].replace(' ','').replace('/','').replace(':','')
        labels_df['EndTime_int'][i] = labels_df['EndDateTime'][i].replace(' ','').replace('/','').replace(':','')
    
    labels_df_select = labels_df[labels_df.Transportation == target_label]
    
    user_trj_list = all_users_trj[user_id]
    
    for i in labels_df_select.index:
        print(i)
        plot_walking_trip(user_id, user_trj_list, labels_df_select['StartTime_int'][i], \
                          labels_df_select['EndTime_int'][i],i)
    
    
user_to_extract = 10  
all_users_trj, is_label = scan_trj_label()    
read_label(user_to_extract, 'walk', all_users_trj)


#plot_user_file(10,'20070804033032')