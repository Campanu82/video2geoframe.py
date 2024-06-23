#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""video2geoframes.py
Python script to generate a collection of geotagged images from a video and a GPS track.
Designed for contribution to street-level imagery projects like Mapillary or Panoramax.
"""

__author__ = "Lucas MATHIEU (@campanu)"
__license__ = "AGPL-3.0-or-later"
__version__ = "2.0-alpha2"
__maintainer__ = "Lucas MATHIEU (@campanu)"
__email__ = "campanu@luc-geo.fr"

import os
import codecs
import platform
from datetime import datetime, timedelta

import cv2
from tomlkit import dumps, loads
from tqdm import tqdm
from exif import Image, GpsAltitudeRef

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
locale = 'en_us'
min_frame_samp = 0.5
max_frame_samp = float(60)
min_timelapse_fps = 1
max_timelapse_fps = 15

## Platform-dependent commands
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

        locale = configuration.get('ui_language')
        max_frame_samp = float(configuration.get('max_frame_sample'))
        ffmpeg_path = configuration.get('ffmpeg_path').replace('./', '{}/'.format(base_path))
        exiftool_path = configuration.get('exiftool_path').replace('./', '{}/'.format(base_path))
    except:
        print('\nError... not readable or incomplete ini file. Default configuration will be used.')

# Localization
locale_file_path = '{}/locales/{}.toml'.format(base_path, locale)

if os.path.exists(locale_file_path):
        with codecs.open(locale_file_path, mode='r', encoding='utf-8') as f:
            locale_toml = loads(f.read())
            f.close()
else:
    print("Error.... file for locale \"{}\" doesn't exists or invalid.".format(locale))
    ValueError

user_agree = locale_toml['user']['agree'][0].upper()
user_disagree = locale_toml['user']['disagree'][0].upper()
path_error = locale_toml['ui']['paths']['path_err']

# Introduction text
print(locale_toml['ui']['info']['intro'])

# User input
## TOML setting file
toml_setting = input('\n{}'.format(locale_toml['ui']['parameters']['toml_setting'].format(user_agree, user_disagree)))
i = 0

if toml_setting.upper() == 'O':
    while True:
        try:
            i += 1
            toml_file_path = unix_path(input('{}'.format(locale_toml['ui']['paths']['toml_file']))).strip()

            if os.path.exists(toml_file_path):
                break
            else:
                print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
                True
        except:
            print('{}\n'.format(locale_toml['ui']['paths']['path_err']))

    with codecs.open(toml_file_path, mode='r', encoding='utf-8') as f:
        setting_toml = loads(f.read())
        f.close()

    # <--coding in progress-->
    video_path = ''
    gps_track_path = ''

## Paths
else:
    print('\n{}'.format(locale_toml['ui']['info']['paths_title']))

    ### Video file
    while True:
        try:
            video_path = unix_path(input('{}'.format(locale_toml['ui']['paths']['video_file']))).strip()
            if os.path.exists(video_path):
                break
            else:
                print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
                True
        except:
            print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
            True

    ### GPS track file
    while True:
        try:
            gps_track_path = unix_path(input('{}'.format(locale_toml['ui']['paths']['gps_track']))).strip()
            if os.path.exists(gps_track_path):
                break
            else:
                print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
                True
        except:
            print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
            True

    ### Output folder
    output_folder = unix_path(input(locale_toml['ui']['paths']['output_folder']))

    ## Parameters
    print('\n{}'.format(locale_toml['ui']['info']['parameters_title']))

    ### Timelapse video
    timelapse = input(locale_toml['ui']['parameters']['timelapse'].format(user_agree, user_disagree))

    if timelapse.upper() == user_agree:
        ### Timelapse framerate parameter
        while True:
            try:
                timelapse_fps = int(input(locale_toml['ui']['parameters']['timelapse_fps'].format(min_timelapse_fps,
                                                                                                  max_timelapse_fps)))
                if max_timelapse_fps >= timelapse_fps >= min_timelapse_fps:
                    frame_sampling = 1 / timelapse_fps
                    break
                else:
                    print(locale_toml['ui']['parameters']['timelapse_fps_err'].format(min_timelapse_fps,
                                                                                      max_timelapse_fps))
                    True
            except ValueError:
                print(locale_toml['ui']['parameters']['timelapse_fps_err'].format(min_timelapse_fps, max_timelapse_fps))
                True

    else:
        ### Frame sampling parameter

        while True:
            try:
                frame_sampling = float(input(locale_toml['ui']['parameters']['frame_samp'].format(min_frame_samp,
                                                                                                  max_frame_samp)))

                if max_frame_samp >= frame_sampling >= min_frame_samp:
                    break
                else:
                    print(locale_toml['ui']['parameters']['frame_samp_err'].format(min_frame_samp, max_frame_samp))
                    True
            except ValueError:
                print(locale_toml['ui']['parameters']['frame_samp_err'].format(min_frame_samp, max_frame_samp))
                True

    ## Frame height parameter
    min_frame_height = 480
    max_frame_height = 6000

    while True:
        try:
            frame_height = int(input(locale_toml['ui']['parameters']['frame_height'].format(min_frame_height,
                                                                                            max_frame_height)))

            if max_frame_height >= frame_height >= min_frame_height:
                break
            else:
                print(locale_toml['ui']['parameters']['frame_height_err'].format(min_frame_height, max_frame_height))
                True
        except ValueError:
            print(locale_toml['ui']['parameters']['frame_height_err'].format(min_frame_height, max_frame_height))
            True

    ### Video start datetime parameter
    while True:
        try:
            video_start_datetime = input(locale_toml['ui']['parameters']['video_start_datetime'])
            video_start_datetime_obj = datetime.strptime(video_start_datetime, '%Y-%m-%dT%H:%M:%S.%f')
            break
        except ValueError:
            print(locale_toml['ui']['parameters']['video_start_datetime_err'])
            True

    ### Video recording timezone
    video_rec_timezone = input(locale_toml['ui']['parameters']['rec_timezone'])

    ### Time offset parameter
    min_time_offset = -10.0
    max_time_offset = 10.0

    while True:
        try:
            time_offset = float(input(locale_toml['ui']['parameters']['time_offset'].format(min_time_offset, max_time_offset)))

            if max_time_offset >= frame_sampling >= min_time_offset:
                break
            else:
                print(locale_toml['ui']['parameters']['time_offset_err'].format(min_time_offset, max_time_offset))
                True
        except ValueError:
            print(locale_toml['ui']['parameters']['time_offset_err'].format(min_time_offset, max_time_offset))
            True

    ### User-defined metadata
    make = input(locale_toml['ui']['metadatas']['make'])
    model = input(locale_toml['ui']['metadatas']['model'])
    author = input(locale_toml['ui']['metadatas']['author'])

# Video metadatas extraction
print('\n{}'.format(locale_toml['processing']['reading_metadatas']))

video = cv2.VideoCapture(video_path)
video_fps = video.get(cv2.CAP_PROP_FPS)
video_width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
video_height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
video_total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

video_file_name = os.path.basename(video_path)
video_file_size = byte_multiple(os.stat(video_path).st_size)
video_duration = video_total_frames / video_fps

video_start_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_offset)
video_start_datetime = video_start_datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
video_start_subsectime = video_start_datetime_obj.strftime('%f')

# Metadata recap
print('\n{}'.format(locale_toml['ui']['info']['metadatas'].format(video_file_name,
                                                                  round(video_file_size[0], 3), video_file_size[1],
                                                                  video_duration, video_start_datetime,
                                                                  int(int(video_start_subsectime) / 1000),
                                                                  video_rec_timezone)))

# Output folder creation
output_folder = '{}/{}'.format(output_folder, video_file_name)
existing_path(output_folder)

# Processes
## Frame sampling + tagging (OpenCV + exif)
i = 0

if timelapse == user_agree:
    frame_interval = frame_sampling / video_fps
else:
    frame_interval = frame_sampling

cv2_tqdm_unit = " {}".format(locale_toml['ui']['units']['cv2_tqdm'])
cv2_tqdm_range = int(video_duration / frame_interval)

for i in tqdm(range(cv2_tqdm_range), unit=cv2_tqdm_unit):
    t = frame_interval * i * 1000
    video.set(cv2.CAP_PROP_POS_MSEC, t)
    ret, frame = video.read()

    frame_name = '{:05d}'.format(i)
    image_name = "{}_f{}.jpg".format(video_file_name.split('.')[0], frame_name)
    image_path = "{}/{}".format(output_folder, image_name)

    cv2.imwrite(image_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 88, cv2.IMWRITE_JPEG_PROGRESSIVE, 1, cv2.IMWRITE_JPEG_SAMPLING_FACTOR, 0x411111])

    ## Time tags preparation
    time_shift = i * frame_sampling
    current_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_shift)
    current_datetime = current_datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
    current_subsec_time = int(int(current_datetime_obj.strftime('%f')) / 1000)

    with open(image_path, 'rb') as image_file:
        image = Image(image_file)
        image.make = make
        image.model = model
        image.author = author
        image.copyright = "{}, {}".format(author, video_start_datetime_obj.strftime('%Y'))
        image.datetime_original = current_datetime
        #image.offset_time_original = video_rec_timezone

        if current_subsec_time > 0 :
            image.subsec_time_original = str(current_subsec_time)

    with open(image_path, 'wb') as tagged_image_file:
        tagged_image_file.write(image.get_file())

    i += 1

# Geo-tagging (ExifTool)
print('\n{}'.format(locale_toml['processing']['geotagging']))
geotagging_cmd = '{} -P -geotag "{}" "-geotime<SubSecDateTimeOriginal" -overwrite_original "{}/{}_f*.jpg"'\
    .format(exiftool_path, gps_track_path, output_folder, video_file_name.split('.')[0])
geotagging = os.system(geotagging_cmd)

# End
input('\n{}'.format(locale_toml['ui']['info']['end']))
