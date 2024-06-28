#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""video2geoframes.py
Python script to generate a collection of geotagged images from a video and a GPS track.
Designed for contribution to street-level imagery projects like Mapillary or Panoramax.
"""

__author__ = "Lucas MATHIEU (@campanu)"
__license__ = "GPL-3.0-or-later"
__version__ = "1.0-beta"
__maintainer__ = "Lucas MATHIEU (@campanu)"
__email__ = "campanu@luc-geo.fr"

import os
import glob
import platform
from datetime import datetime, timedelta
import exiftool as et
#import tqdm

# Functions
def unix_path(path):
    if '\\' in path:
        path = path.replace('\\', '/')

    return path


def existing_path(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def byte_multiple(size):
    multiples = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q']
    i = -1

    while size >= 1024 and i < 9:
        i += 1
        size = size / 1024

    multiple = multiples[i]

    return size, multiple


# Start
print('# video2geoframes.py')

# Configuration settings
base_path = unix_path(os.path.dirname(__file__))
ini_file_path = '{}/video2geoframes.ini'.format(base_path)
ini_file_err = False

## Default values
ui_language = 'en'
max_frame_samp = float(60)

if platform.system() == 'Windows':
    ffmpeg_path = '{}/dependencies/ffmpeg-essentials/bin/ffmpeg.exe'.format(base_path)
    exiftool_path = '{}/dependencies/exiftool.exe'.format(base_path)
else:
    ffmpeg_path = 'ffmpeg'
    exiftool_path = 'exiftool'

## ini file reading
if os.path.exists(ini_file_path):
    configuration = {}

    try:
        with open(ini_file_path, 'r') as file:
            for line in file:
                if line[0] == '#':
                    continue
                else:
                    (key, value) = line.split()
                    configuration[key] = value.replace('"', '')

        ui_language = configuration.get('ui_language')
        max_frame_samp = float(configuration.get('max_frame_sample'))
        ffmpeg_path = configuration.get('ffmpeg_path').replace('./', '{}/'.format(base_path))
        exiftool_path = configuration.get('exiftool_path').replace('./', '{}/'.format(base_path))
    except:
        print('\nError... not readable or incomplete ini file. Default configuration will be used.')
        
# UI language
ui_text_dict = {
    'fr':
        {
            'ui_intro': 'Bienvenue dans le script video2geoframes.py !\n'
                        'Ce script permet de créer à partir d\'une vidéo et d\'une trace GPX un ensemble de photos'
                        ' géotaguées.',
            'ui_end': 'Fin du programme, appuyez sur Entrée pour fermer.',
            'ui_paths_title': '## Chemins',
            'ui_parameters_title': '## Paramètres du traitement',
            'ui_timelapse': 'Vidéo timelapse (O/N) ? ',
            'ui_timelapse_fps': 'Débit d\'image du timelapse (image/s) : ',
            'ui_timelapse_fps_err': 'Débit d\'image du timelapse (image/s) : ',
            'ui_frame_samp': 'Entrez l\'espacement temporel des images en secondes [{}-{}] : ',
            'ui_frame_samp_err': 'Erreur... veuillez entrer un nombre décimal.',
            'ui_frame_height': 'Entrez la hauteur des images en pixels (ratio inchangé) [{}-{}] : ',
            'ui_frame_height_err': 'Erreur... veuillez entrer un nombre entier entre {} et {}.',
            'ui_video_start_datetime': 'Entrez l\'horodatage du début de la vidéo au format ISO'
                                       ' (exemple : 2023-09-18T22:00:02.000) : ',
            'ui_video_start_datetime_err': 'Erreur... la l\'horodatage entré est invalide.',
            'ui_rec_timezone': 'Entrez le décalage horaire par rapport à UTC (exemple pour CEST : +02:00) : ',
            'ui_time_offset': 'Entrez le décalage temporel entre la vidéo et le GPX en secondes [{}-{}] : ',
            'ui_time_offset_err': 'Erreur... veuillez entrer un nombre décimal entre {} et {}.',
            'ui_video_path': 'Entrez le chemin de la vidéo : ',
            'ui_gpx_path': 'Entrez le chemin de la trace GPX : ',
            'ui_output': 'Entrez le dossier de sortie : ',
            'ui_path_err': 'Erreur... le fichier n\'existe pas.',
            'ui_make': 'Entrez la marque du capteur : ',
            'ui_model': 'Entrez le modèle du capteur : ',
            'ui_author': 'Entrez l\'auteur : ',
            'ui_metadata': '{} ({} {}B)\n'
                           '- Durée : {} s\n'
                           '- Heure de début : {}.{}\n'
                           '- Décalage horaire : {}',
            'process_reading_metadata': 'Lecture des métadonnées de la vidéo...',
            'process_sampling': 'Extraction des images depuis la vidéo...',
            'process_timestamping': 'Définition de l\'horodatage des images...',
            'process_geotagging': 'Géotaguage des images...',
            'agree': 'O'
        },

    'en':
        {
            'ui_intro': 'Welcome in video2geoframes.py script !\n'
                        'This script is designed to create geotagged frames from video and GPX track.',
            'ui_end': 'End of program, press Enter to quit.',
            'ui_paths_title': '## Paths',
            'ui_parameters_title': '## Process parameters',
            'ui_timelapse': 'Timelapse video (Y/N) ? ',
            'ui_timelapse_fps': 'Timelapse framerate (frame/s) : ',
            'ui_timelapse_fps_err': 'Error... please enter a decimal.',
            'ui_frame_samp': 'Enter the frame sampling in seconds [{}-{}] : ',
            'ui_frame_samp_err': 'Error... please enter a decimal between {} and {}.',
            'ui_frame_height': 'Enter frame height in pixels (ratio unchanged) [{}-{}] : ',
            'ui_frame_height_err': 'Error... please enter an integer between {} and {}.',
            'ui_video_start_datetime': 'Enter video start datetime following ISO format'
                                       ' (exemple : 2023-09-18T22:00:02.000) : ',
            'ui_video_start_datetime_err': 'Error... entered datetime is not valid.',
            'ui_rec_timezone': 'Enter time offset related to UTC (example for CEST : +02:00) : ',
            'ui_time_offset': 'Enter time offset between video and GPX in seconds [{}-{}] : ',
            'ui_time_offset_err': 'Error... please enter a decimal between {} and {}.',
            'ui_video_path': 'Enter video path : ',
            'ui_gpx_path': 'Enter GPX track path : ',
            'ui_output': 'Enter output folder : ',
            'ui_path_err': 'Error... File doesn\'t exist.',
            'ui_make': 'Enter the camera brand : ',
            'ui_model': 'Enter the camera model : ',
            'ui_author': 'Enter author name : ',
            'ui_metadata': '{} ({} {}B)\n'
                           '- Duration : {} s\n'
                           '- Start time : {}.{}\n'
                           '- Time offset : {}',
            'process_reading_metadata': 'Reading video metadata...',
            'process_sampling': 'Extracting frames from video...',
            'process_timestamping': 'Setting timestamp on frames...',
            'process_geotagging': 'Geotagging frames...',
            'agree': 'Y'
        }
}

ui_text_locale = ui_text_dict.get(ui_language)

# Introduction text
print(ui_text_locale.get('ui_intro'))

# User variables
## Paths
print('\n{}'.format(ui_text_locale.get('ui_paths_title')))

### Video file
while True:
    try:
        video_path = unix_path(input('{}'.format(ui_text_locale.get('ui_video_path')))).strip()
        if os.path.exists(video_path):
            break
        else:
            print('{}\n'.format(ui_text_locale.get('ui_path_err')))
            True
    except:
        print('{}\n'.format(ui_text_locale.get('ui_path_err')))

### GPX track file
while True:
    try:
        gpx_path = unix_path(input('{}'.format(ui_text_locale.get('ui_gpx_path')))).strip()
        if os.path.exists(gpx_path):
            break
        else:
            print('{}\n'.format(ui_text_locale.get('ui_path_err')))
            True
    except:
        print('{}\n'.format(ui_text_locale.get('ui_path_err')))

### Output folder
output_path = unix_path(input(ui_text_locale.get('ui_output')))

## Parameters
print('\n{}'.format(ui_text_locale.get('ui_parameters_title')))

### Timelapse video
timelapse = input(ui_text_locale.get('ui_timelapse'))

if timelapse.upper() == ui_text_locale.get('agree'):
    ### Timelapse framerate parameter
    while True:
        try:
            timelapse_fps = int(input(ui_text_locale.get('ui_timelapse_fps')))
            frame_sampling = 1 / timelapse_fps
            break
        except ValueError:
            print(ui_text_locale.get('ui_timelapse_fps_err'))
            True

else:
    ### Frame sampling parameter
    min_frame_samp = 0.5

    while True:
        try:
            frame_sampling = float(input(ui_text_locale.get('ui_frame_samp').format(min_frame_samp, max_frame_samp)))

            if max_frame_samp >= frame_sampling >= min_frame_samp:
                break
            else:
                print(ui_text_locale.get('ui_frame_samp_err').format(min_frame_samp, max_frame_samp))
                True
        except ValueError:
            print(ui_text_locale.get('ui_frame_samp_err').format(min_frame_samp, max_frame_samp))

## Frame height parameter
min_frame_height = 480
max_frame_height = 6000

while True:
    try:
        frame_height = int(input(ui_text_locale.get('ui_frame_height').format(min_frame_height, max_frame_height)))

        if max_frame_height >= frame_height >= min_frame_height:
            break
        else:
            print(ui_text_locale.get('ui_frame_height_err').format(min_frame_height, max_frame_height))
            True
    except ValueError:
        print(ui_text_locale.get('ui_frame_height_err').format(min_frame_height, max_frame_height))

### Video start datetime parameter
while True:
    try:
        video_start_datetime = input(ui_text_locale.get('ui_video_start_datetime'))
        video_start_datetime_obj = datetime.strptime(video_start_datetime, '%Y-%m-%dT%H:%M:%S.%f')
        break
    except ValueError:
        print(ui_text_locale.get('ui_video_start_datetime_err'))
        True

### Video recording timezone
video_rec_timezone = input(ui_text_locale.get('ui_rec_timezone'))

### Time offset parameter
min_time_offset = -10.0
max_time_offset = 10.0

while True:
    try:
        time_offset = float(input(ui_text_locale.get('ui_time_offset').format(min_time_offset, max_time_offset)))

        if max_time_offset >= frame_sampling >= min_time_offset:
            break
        else:
            print(ui_text_locale.get('ui_time_offset_err').format(min_time_offset, max_time_offset))
            True
    except ValueError:
        print(ui_text_locale.get('ui_time_offset_err').format(min_time_offset, max_time_offset))

### User-defined metadata
make = input(ui_text_locale.get('ui_make'))
model = input(ui_text_locale.get('ui_model'))
author = input(ui_text_locale.get('ui_author'))

# Getting EXIF metadata
print('\n{}'.format(ui_text_locale.get('process_reading_metadata')))

if exiftool_path != 'exiftool':
    et.ExifTool(executable=exiftool_path)

with et.ExifToolHelper() as eth:
    video_metadata = eth.get_metadata('{}'.format(video_path))

    # for d in video_metadata:
        # for k, v in d.items():
            # print(f"Dict: {k} = {v}")

## Building metadata variables
video_metadata = video_metadata[0]
video_file_name = os.path.splitext(video_metadata.get('File:FileName'))[0]
video_size = byte_multiple(video_metadata.get('File:FileSize'))
#video_rec_timezone = video_metadata.get('File:FileModifyDate')[-6:]
video_duration = video_metadata.get('QuickTime:Duration')

video_start_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_offset)
video_start_datetime = video_start_datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
video_start_subsectime = video_start_datetime_obj.strftime('%f')

# Displaying metadata
print('\n{}'.format(ui_text_locale.get('ui_metadata').format(video_metadata.get('File:FileName'),
                                                             round(video_size[0], 3), video_size[1], video_duration,
                                                             video_start_datetime,
                                                             int(int(video_start_subsectime) / 1000),
                                                             video_rec_timezone)))

# Creating output folder
output_path = '{}/{}'.format(output_path, video_metadata.get('File:FileName'))
existing_path(output_path)

# Processes
## ffmpeg process
print('\n{}'.format(ui_text_locale.get('process_sampling')))

if timelapse.upper() == ui_text_locale.get('agree'):
    sampling_cmd = (('{} -loglevel error -hide_banner -stats -i {} -vf "scale=-2:{}" -qscale:v 2 '
                    '{}/{}_f%04d.jpg').format(ffmpeg_path, video_path, frame_height, output_path, video_file_name))
else:
    sampling_cmd = (('{} -loglevel error -hide_banner -stats -i {} -vf "scale=-2:{},fps=fps=1/{}:start_time=0:round=zero"'
                     ' -qscale:v 2 {}/{}_f%04d.jpg').format(ffmpeg_path, video_path, frame_height, frame_sampling,
                                                            output_path, video_file_name))

sampling = os.system(sampling_cmd)

## ExifTool processes
print('\n{}'.format(ui_text_locale.get('process_timestamping')))
user_metadata = '"-Make={}" "-Model={}" "-Author={}" "-Copyright={}, {}"'\
    .format(make, model, author, author, video_start_datetime_obj.strftime('%Y'))
metadata_cmd = '{} -overwrite_original {} "{}/{}_f*.jpg"'\
    .format(exiftool_path, user_metadata, output_path, video_file_name)
metadata = os.system(metadata_cmd)

frame_list = glob.glob('{}/{}_f*.jpg'.format(output_path, video_file_name))
i = 0

for f in frame_list:
    time_shift = i * frame_sampling
    current_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_shift)
    current_datetime = current_datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
    current_subsectime = int(int(current_datetime_obj.strftime('%f')) / 1000)

    timestamp_cmd = ('{} -P -m -overwrite_original "-DateTimeOriginal={}" "-OffsetTimeOriginal={}"'
                     ' "-SubSecTimeOriginal={}" "{}"')\
        .format(exiftool_path, current_datetime, video_rec_timezone, current_subsectime, f)
    timestamp = os.system(timestamp_cmd)
    i += 1

print('\n{}'.format(ui_text_locale.get('process_geotagging')))
geotagging_cmd = '{} -P -geotag "{}" "-geotime<SubSecDateTimeOriginal" -overwrite_original "{}/{}_f*.jpg"'\
    .format(exiftool_path, gpx_path, output_path, video_file_name)
geotagging = os.system(geotagging_cmd)


input('\n{}'.format(ui_text_locale.get('ui_end')))
