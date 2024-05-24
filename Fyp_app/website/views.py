import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import googlemaps
from flask import Blueprint , render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Mysql
# import pyaudio
# import wave
from flask import send_from_directory
from flask import jsonify
import threading
import random as r
import mysql.connector
import numpy as np
import io
import base64
from joblib import load



# from . import mydb, cursor
user_id = r.randint(10000,99999)
# user_email = r.randint(10000,99999)

mysql = Mysql()
views = Blueprint('views', __name__)
@views.route('/')
@login_required
def home():
    return render_template("home.html", user= current_user)#can pass variable from here to ur templates(varname = "something")


@views.route('/hearing-test0', methods=['POST', 'GET'])
def hearingtest0():
    return render_template('hearing-test0.html')

@views.route('/hearing-test_L', methods=['POST', 'GET'])
def hearingtestl():
    return render_template('hearing-test_L.html')

@views.route('/hearing-test_R', methods=['POST', 'GET'])
def hearingtestr():
    return render_template('hearing_test_R.html')


@views.route('/add_audiogram_L', methods=['POST'])
def add_audiograml():
    if request.method == 'POST':
        data = request.json
        frequency = data.get('frequency')
        decibels = data.get('decibels')

        user_email = current_user.email

        # Construct the column name based on the frequency
        if frequency:
            column_name_L = 'l{}'.format(frequency)

            # Check if the user's audiogram data already exists
            mysql.cursor.execute("SELECT * FROM audiogram WHERE userid = %s", (user_email,))
            existing_row = mysql.cursor.fetchone()

            if existing_row:
                # Update the existing row
                sql = "UPDATE audiogram SET {} = %s WHERE userid = %s".format(column_name_L)
                mysql.cursor.execute(sql, (int(decibels), user_email))
                mysql.mydb.commit()
            else:
                # Insert a new row for the user
                sql = "INSERT INTO audiogram (userid, {}) VALUES (%s, %s)".format(column_name_L)
                mysql.cursor.execute(sql, (user_email, int(decibels)))
                mysql.mydb.commit()

            print(mysql.cursor.rowcount, "record inserted.")

        return jsonify({'message': 'Audiogram added successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400
    
@views.route('/add_audiogram_R', methods=['POST'])
def add_audiogramr():
    if request.method == 'POST':
        data = request.json
        frequency = data.get('frequency')
        decibels = data.get('decibels')

        user_email = current_user.email

        # Construct the column name based on the frequency
        if frequency:
            column_name_R = 'r{}'.format(frequency)
            print("Column Name for Right Ear:", column_name_R)  # Debug statement

            # Check if the user's audiogram data already exists
            mysql.cursor.execute("SELECT * FROM audiogram WHERE userid = %s", (user_email,))
            existing_row = mysql.cursor.fetchone()

            if existing_row:
                # Update the existing row
                sql = "UPDATE audiogram SET {} = %s WHERE userid = %s".format(column_name_R)
                mysql.cursor.execute(sql, (int(decibels), user_email))
                mysql.mydb.commit()
            else:
                # Insert a new row for the user
                sql = "INSERT INTO audiogram (userid, {}) VALUES (%s, %s)".format(column_name_R)
                mysql.cursor.execute(sql, (user_email, int(decibels)))
                mysql.mydb.commit()

            print(mysql.cursor.rowcount, "record inserted.")

        return jsonify({'message': 'Audiogram added successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request method'}), 400




@views.route('/report', methods=['GET'])
def plot_audiograms():

    clf = load('website/rf_clf.joblib')
    # Connect to database
    user_email = current_user.email
    
    # Fetch audiogram data for the user
    mysql.cursor.execute("SELECT * FROM audiogram WHERE userid = %s", (user_email,))
    row = mysql.cursor.fetchone()

    if row:
        # Extract frequency and decibel data for the left ear
        frequencies_L = ['500', '1000', '2000', '3000', '4000', '6000', '8000']
        thresholds_L = [row[i] for i in range(2, 9)]  # Assuming frequency columns start from index 2
        avg_L = (row[2] + row[3] + row[4] +row[5] +row[6] +row[7] +row[8])/7
        avg_500_1000_L = (row[2] + row[3]) / 2
        avg_2000_3000_4000_L = (row[4] + row[5] + row[6]) / 3
        avg_6000_8000_L = (row[7] + row[8]) / 2
        minimum_threshold_L = min(thresholds_L)
        maximum_threshold_L = max(thresholds_L)
        std_threshold_L = np.std(thresholds_L)

        # Extract frequency and decibel data for the right ear
        frequencies_R = ['500', '1000', '2000', '3000', '4000', '6000', '8000']
        thresholds_R = [row[i] for i in range(9, 16)]  # Assuming frequency columns start from index 9
        avg_R = (row[9] + row[10] + row[11] +row[12] +row[13] +row[14] +row[15])/7
        avg_500_1000_R = (row[9] + row[10]) / 2
        avg_2000_3000_4000_R = (row[11] + row[12] + row[13]) / 3
        avg_6000_8000_R = (row[14] + row[15]) / 2
        minimum_threshold_R = min(thresholds_R)
        maximum_threshold_R = max(thresholds_R)
        std_threshold_R = np.std(thresholds_R)

        # Combine all features into a single list for the left ear
        features_L = thresholds_L + [avg_500_1000_L, avg_2000_3000_4000_L, avg_6000_8000_L, minimum_threshold_L, maximum_threshold_L, std_threshold_L]

        # Combine all features into a single list for the right ear
        features_R = thresholds_R + [avg_500_1000_R, avg_2000_3000_4000_R, avg_6000_8000_R, minimum_threshold_R, maximum_threshold_R, std_threshold_R]

        # Predict class for the left ear
        predicted_class_L = clf.predict([features_L])

        # Predict class for the right ear
        predicted_class_R = clf.predict([features_R])

        plt.figure(figsize=(8, 6))
        plt.plot(frequencies_L, thresholds_L, marker='o')
        plt.title('Audiogram - Left Ear')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Threshold (dB)')
        plt.grid(True)
        plt.ylim(110, -10)  # Adjust the y-axis limits as needed
        plt.yticks(np.arange(110, -20, -10))
        img_bytes_L = io.BytesIO()
        plt.savefig(img_bytes_L, format='png')
        img_bytes_L.seek(0)
        img_base64_L = base64.b64encode(img_bytes_L.read()).decode('utf-8')

        # Plot the audiograms for the right ear
        plt.figure(figsize=(8, 6))
        plt.plot(frequencies_R, thresholds_R, marker='x', color='red')
        plt.title('Audiogram - Right Ear')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Threshold (dB)')
        plt.grid(True)
        plt.ylim(110, -10)  # Adjust the y-axis limits as needed
        plt.yticks(np.arange(110, -20, -10))
        img_bytes_R = io.BytesIO()
        plt.savefig(img_bytes_R, format='png')
        img_bytes_R.seek(0)
        img_base64_R = base64.b64encode(img_bytes_R.read()).decode('utf-8')

        

        # Return the threshold string to the client
        threshold_string_L = ', '.join(str(threshold) for threshold in thresholds_L)
        threshold_string_R = ', '.join(str(threshold) for threshold in thresholds_R)

        # Return the filename of the plot to the client
        return render_template('report.html', plot_base64_L=img_base64_L, plot_base64_R=img_base64_R, thresholdvalues_L=threshold_string_L, thresholdvalues_R=threshold_string_R, predicted_class_L=predicted_class_L, predicted_class_R=predicted_class_R, max_L =  maximum_threshold_L, max_R = maximum_threshold_R, avg_L = avg_L, avg_R = avg_R )  
    else:
        return "Audiogram data not found for user with ID {}".format(user_id), 404


# @views.route('/report_L', methods=['GET'])
# def plot_audiogram_L():

#     clf = load('website\clf.joblib2')
#     # # Connect to database
#     user_email = current_user.email
    
#     mysql.cursor.execute("SELECT * FROM audiogram WHERE userid = %s", (user_email,))       
#     row = mysql.cursor.fetchone()

#     if row:
#         # Extract frequency and decibel data from the row
#         frequencies = ['500', '1000', '2000', '3000', '4000', '6000', '8000']
#         thresholds = [row[i] for i in range(2, 9)]  # Assuming frequency columns start from index 2

#         avg_500_1000 = (row[2] + row[3]) / 2
#         avg_2000_3000_4000 = (row[4] + row[5] + row[6]) / 3
#         avg_6000_8000 = (row[7] + row[8]) / 2
#         minimum_threshold = min(thresholds)
#         maximum_threshold = max(thresholds)
#         std_threshold = np.std(thresholds)

# # Combine all features into a single list
#         features = thresholds + [avg_500_1000, avg_2000_3000_4000, avg_6000_8000, minimum_threshold, maximum_threshold, std_threshold]

#         predicted_class = clf.predict([features])

#         # Plot the audiogram
#         plt.figure(figsize=(8, 6))
#         plt.plot(frequencies, thresholds, marker='o')
#         plt.title('Audiogram')
#         plt.xlabel('Frequency (Hz)')
#         plt.ylabel('Threshold (dB)')
#         plt.grid(True)
#         plt.ylim(110, -10)  # Adjust the y-axis limits as needed
#         plt.yticks(np.arange(110, -20, -10))

#         # Save the plot to a temporary file
#         # plot_filename = 'audiogram_plot.png'
#         # plt.savefig(plot_filename)
#         # plt.close()

#         # Convert the plot to a bytes object
#         img_bytes = io.BytesIO()
#         plt.savefig(img_bytes, format='png')
#         img_bytes.seek(0)
#         img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

#         # Return the filename of the plot to the client
    
#         threshold_string = ', '.join(str(threshold) for threshold in thresholds)

#         # Return the threshold string to the client
#         return render_template('report.html',plot_base64_L=img_base64,thresholdvalues = threshold_string, predicted_class = predicted_class)  
#     else:
#         return "Audiogram data not found for user with ID {}".format(user_id), 404
    

# @views.route('/report_R', methods=['GET'])
# def plot_audiogramr():

#     clf = load('website\clf.joblib2')
#     # # Connect to database
#     user_email = current_user.email
    
#     mysql.cursor.execute("SELECT * FROM audiogram WHERE userid = %s", (user_email,))       
#     row = mysql.cursor.fetchone()

#     if row:
#         # Extract frequency and decibel data from the row
#         frequencies = ['500', '1000', '2000', '3000', '4000', '6000', '8000']
#         thresholds = [row[i] for i in range(9, 16)]  # Assuming frequency columns start from index 2

#         avg_500_1000 = (row[9] + row[10]) / 2
#         avg_2000_3000_4000 = (row[11] + row[12] + row[13]) / 3
#         avg_6000_8000 = (row[14] + row[15]) / 2
#         minimum_threshold = min(thresholds)
#         maximum_threshold = max(thresholds)
#         std_threshold = np.std(thresholds)

# # Combine all features into a single list
#         features = thresholds + [avg_500_1000, avg_2000_3000_4000, avg_6000_8000, minimum_threshold, maximum_threshold, std_threshold]

#         predicted_class = clf.predict([features])

#         # Plot the audiogram
#         plt.figure(figsize=(8, 6))
#         plt.plot(frequencies, thresholds, marker='o')
#         plt.title('Audiogram')
#         plt.xlabel('Frequency (Hz)')
#         plt.ylabel('Threshold (dB)')
#         plt.grid(True)
#         plt.ylim(110, -10)  # Adjust the y-axis limits as needed
#         plt.yticks(np.arange(110, -20, -10))

#         # Save the plot to a temporary file
#         # plot_filename = 'audiogram_plot.png'
#         # plt.savefig(plot_filename)
#         # plt.close()

#         # Convert the plot to a bytes object
#         img_bytes = io.BytesIO()
#         plt.savefig(img_bytes, format='png')
#         img_bytes.seek(0)
#         img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

#         # Return the filename of the plot to the client
    
#         threshold_string = ', '.join(str(threshold) for threshold in thresholds)

#         # Return the threshold string to the client
#         return render_template('report.html',plot_base64_R=img_base64,thresholdvalues = threshold_string, predicted_class = predicted_class)  
#     else:
#         return "Audiogram data not found for user with ID {}".format(user_id), 404
    
    
@views.route('/speech', methods=['POST', 'GET'])
def speechtest():
    return render_template('speech.html')


