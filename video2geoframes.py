#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""video2geoframes.py
Python program to generate a collection of geotagged images from a video and a GPS track.
Designed for contribution to street-level imagery projects like Mapillary or Panoramax.
"""

__author__ = "Lucas MATHIEU (@campanu)"
__license__ = "GPL-3.0-or-later"
__version__ = "2.0-alpha12"
__maintainer__ = "Lucas MATHIEU (@campanu)"
__email__ = "campanu@luc-geo.fr"

import os
import codecs
import platform
from datetime import datetime, timedelta

import cv2
import piexif
from tomlkit import loads
from tqdm import tqdm


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


def existing_items(expected_items: list, items: list):
    presents_items = []
    duplicated_items = []
    missing_items = []

    for eit in expected_items:
        i = 0
        for it in items:
            if it == eit:
                i += 1

        if i == 0:
            missing_items.append(eit)
        elif i == 1:
            presents_items.append(eit)
        else:
            duplicated_items.append(eit)

    return {'presents': presents_items, 'duplicated': duplicated_items, 'missing': missing_items}


def list_enumerator(item_list: list, intermediate_separator: str, last_separator: str):
    i = 1
    enumerated_list = []

    for it in item_list:
        if i == 1:
            enumerated_list = it
        elif 1 < i < len(item_list):
            enumerated_list = '{}{}{}'.format(enumerated_list, intermediate_separator, it)
        else:
            enumerated_list = '{}{}{}'.format(enumerated_list, last_separator, it)

        i += 1

    return enumerated_list


def video_metadata_reader(video_path: str):
    video_md = {}

    video = cv2.VideoCapture(video_path)
    video_md['fps'] = video.get(cv2.CAP_PROP_FPS)
    video_md['width'] = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_md['height'] = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_md['frame_number'] = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video = None

    return video_md


# Start
print("# video2geoframes.py (v{})\n".format(__version__))

# Configuration settings
base_path = unix_path(os.path.dirname(__file__))
conf_file_path = '{}/video2geoframes_conf.toml'.format(base_path)
conf_file_err = False

# Default values
mandatory_parameters = ['locale', 'exiftool_path']
mandatory_settings1 = ['video_file', 'gps_track_file', 'output_folder']
mandatory_settings2 = ['frame_sampling']
mandatory_settings3 = ['timelapse', 'start_datetime', 'rec_timezone']
optional_settings = ['frame_height', 'time_offset']
minimal_md = ['author', 'camera_maker', 'camera_model']
locale = 'en_us'
min_frame_samp = 0.5
max_frame_samp = 60.0
min_timelapse_fps = 1
max_timelapse_fps = 15
min_frame_height = 480
max_frame_height = 9000
min_time_offset = -10.0
max_time_offset = 10.0

# Platform-dependent default paths
if platform.system() == 'Windows':
    exiftool_path = '{}/dependencies/exiftool.exe'.format(base_path)
else:
    exiftool_path = 'exiftool'

try:
    # Configuration file reading
    try:
        if os.path.exists(conf_file_path):
            with codecs.open(conf_file_path, mode='r', encoding='utf-8') as f:
                conf_toml = loads(f.read())
                f.close()
        else:
            raise FileNotFoundError

        # Configuration check
        reading_parameters = conf_toml['system'].keys()
        check_result = existing_items(mandatory_parameters, reading_parameters)

        if len(check_result['missing']) != 0:
            missing_parameters_list = list_enumerator(check_result['missing'], ', ', ' and ')

            if len(missing_parameters_list) > 1:
                verb = 'is'
            else:
                verb = 'are'

            print("(!) {} {} missing in configuration file.".format(missing_parameters_list, verb))
            raise ValueError
        else:
            # Configuration assignment
            locale = conf_toml['system']['locale']
            exiftool_path = unix_path(conf_toml['system']['exiftool_path']).replace('./', '{}/'.format(base_path))
    except (FileNotFoundError, ValueError):
        print("\nError... configuration file doesn't exists or invalid.")
        default_conf = str(input("Use default configuration instead (Y/N) ? ").upper())

        if default_conf != 'Y':
            raise InterruptedError

    # Localization
    locale_file_path = '{}/locales/{}.toml'.format(base_path, locale)

    if os.path.exists(locale_file_path):
        with codecs.open(locale_file_path, mode='r', encoding='utf-8') as f:
            locale_toml = loads(f.read())
            f.close()
    else:
        print("\nError.... file for locale \"{}\" doesn't exists or invalid.".format(locale))
        raise InterruptedError

    user_agree = locale_toml['user']['agree'][0].upper()
    user_disagree = locale_toml['user']['disagree'][0].upper()
    path_error = locale_toml['ui']['paths']['path_err']

    # Introduction text
    print(locale_toml['ui']['info']['intro'])

    # User input
    # TOML setting file
    toml_setting = input('\n{}'.format(locale_toml['ui']['parameters']['toml_setting'].format(user_agree, user_disagree)))

    if toml_setting.upper() == user_agree:
        # TOML setting file path input
        while True:
            toml_setting_path = unix_path(input('{}'.format(locale_toml['ui']['paths']['toml_file']))).strip()

            if os.path.exists(toml_setting_path):
                break
            elif toml_setting_path == '':
                print('{}'.format(locale_toml['ui']['info']['cancel']))
                raise InterruptedError
            else:
                print('{}\n'.format(locale_toml['ui']['paths']['path_err']))
                True

        # TOML file checking
        print("\n{}".format(locale_toml['processing']['reading_toml_setting']))

        try:
            if os.path.exists(toml_setting_path):
                with codecs.open(toml_setting_path, mode='r', encoding='utf-8') as f:
                    setting_toml = loads(f.read())
                    f.close()

                reading_settings1 = setting_toml['paths'].keys()
                reading_settings2 = setting_toml['process_settings'].keys()
                reading_settings3 = setting_toml['video'].keys()
                reading_metadata = setting_toml['metadata'].keys()

                check_settings1 = existing_items(mandatory_settings1, reading_settings1)
                check_settings2 = existing_items(mandatory_settings2, reading_settings2)
                check_settings3 = existing_items(mandatory_settings3, reading_settings3)
                check_metadata = existing_items(minimal_md, reading_metadata)

                missing_settings = []
                missing_settings.extend(check_settings1['missing'])
                missing_settings.extend(check_settings2['missing'])
                missing_settings.extend(check_settings3['missing'])

                missing_metadata = check_metadata['missing']

                if len(missing_settings) > 0:
                    missing_settings_list = list_enumerator(missing_settings, ', ', ' and ')

                    if len(missing_settings) == 1:
                        verb = 'is'
                    else:
                        verb = 'are'

                    print("(!) {}".format(locale_toml['ui']['toml_setting']['incomplete_err'].format(missing_settings_list, verb)))
                    raise ValueError
                else:
                    video_path = unix_path(setting_toml['paths']['video_file'])

                    if os.path.exists(video_path):
                        print('> {}'.format(locale_toml['ui']['toml_setting']['video_file'].format(video_path)))
                        video_md = video_metadata_reader(video_path)

                        if video_md['frame_number'] > 0:
                            video_fps = video_md['fps']
                            video_width = video_md['width']
                            video_height = video_md['height']
                            video_frame_number = video_md['frame_number']
                        else:
                            raise ValueError
                    else:
                        current_file = video_path
                        raise FileNotFoundError

                    gps_track_path = unix_path(setting_toml['paths']['gps_track_file'])

                    if os.path.exists(gps_track_path):
                        print('> {}'.format(locale_toml['ui']['toml_setting']['gps_track_file'].format(gps_track_path)))
                    else:
                        current_file = gps_track_path
                        raise FileNotFoundError

                    output_folder = unix_path(setting_toml['paths']['output_folder'])

                    timelapse = bool(setting_toml['video']['timelapse'][0])
                    timelapse_fps = int(setting_toml['video']['timelapse'][1])

                    if timelapse and min_timelapse_fps <= timelapse_fps <= max_timelapse_fps:
                        print("> {}".format(locale_toml['ui']['toml_setting']['timelapse_mode'].format(timelapse_fps)))
                    elif timelapse and (timelapse_fps < min_timelapse_fps or timelapse_fps > max_timelapse_fps):
                        raise ValueError
                    else:
                        frame_sampling = float(setting_toml['process_settings']['frame_sampling'])

                        if min_frame_samp <= frame_sampling <= max_frame_samp:
                            print("> {}".format(locale_toml['ui']['toml_setting']['classic_mode'].format(frame_sampling)))
                        else:
                            raise ValueError

                    video_start_datetime_obj = setting_toml['video']['start_datetime']
                    video_rec_timezone = str(setting_toml['video']['rec_timezone'])

                    if 'time_offset' in setting_toml['process_settings']:
                        time_offset = setting_toml['process_settings']['time_offset']

                        if time_offset != 0:
                            if min_time_offset <= time_offset <= max_time_offset:
                                time_offset = float(time_offset)
                            else:
                                raise ValueError
                        else:
                            time_offset = 0

                    if video_height <= max_frame_height:
                        max_frame_height = int(round(video_height, 0))

                    if 'frame_height' in setting_toml['process_settings']:
                        frame_height = int(setting_toml['process_settings']['frame_height'])

                        if min_frame_height <= frame_height <= max_frame_height:
                            print("> {}".format(locale_toml['ui']['toml_setting']['resizing'].format(video_height, frame_height)))
                            pass
                        elif frame_height == 0 or frame_height > max_frame_height:
                            frame_height = max_frame_height
                        elif frame_height < min_frame_height:
                            print("> {}".format(locale_toml['ui']['toml_setting']['resizing'].format(video_height, min_frame_height)))
                            frame_height = min_frame_height
                    else:
                        print("> {}".format(locale_toml['ui']['toml_setting']['resizing'].format(video_height, max_frame_height)))
                        frame_height = max_frame_height

                if len(missing_metadata) > 0:
                    raise ValueError
                else:
                    author = setting_toml['metadata']['author']
                    make = setting_toml['metadata']['camera_maker']
                    model = setting_toml['metadata']['camera_model']
            else:
                current_file = toml_setting_path
                raise FileNotFoundError
        except FileNotFoundError:
            print('(!) {}'.format(locale_toml['ui']['error']['file_not_found'].format(current_file)))
        except ValueError:
            print('{}'.format(locale_toml['ui']['error']['invalid_toml_key']))
    # Paths
    else:
        print('\n{}'.format(locale_toml['ui']['info']['paths_title']))

        # Video file
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

        # Video metadata extraction
        video_md = video_metadata_reader(video_path)
        video_fps = video_md['fps']
        video_width = video_md['width']
        video_height = video_md['height']
        video_frame_number = video_md['frame_number']

        # GPS track file
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

        # Output folder
        output_folder = unix_path(input(locale_toml['ui']['paths']['output_folder']))

        # Parameters
        print('\n{}'.format(locale_toml['ui']['info']['parameters_title']))

        # Timelapse video
        timelapse = input(locale_toml['ui']['parameters']['timelapse'].format(user_agree, user_disagree)).upper()

        if timelapse == user_agree:
            timelapse = True

            # Timelapse framerate parameter
            while True:
                try:
                    timelapse_fps = int(input(locale_toml['ui']['parameters']['timelapse_fps'].format(min_timelapse_fps,
                                                                                                      max_timelapse_fps)))
                    if max_timelapse_fps >= timelapse_fps >= min_timelapse_fps:
                        break
                    else:
                        print('\n{}'.format(locale_toml['ui']['parameters']['timelapse_fps_err'].format(min_timelapse_fps,
                                                                                          max_timelapse_fps)))
                        True
                except ValueError:
                    print('\n{}'.format(locale_toml['ui']['parameters']['timelapse_fps_err'].format(min_timelapse_fps, max_timelapse_fps)))
                    True
        else:
            # Frame sampling parameter
            while True:
                try:
                    frame_sampling = float(input(locale_toml['ui']['parameters']['frame_samp'].format(min_frame_samp,
                                                                                                      max_frame_samp)))

                    if max_frame_samp >= frame_sampling >= min_frame_samp:
                        break
                    else:
                        print('\n{}'.format(locale_toml['ui']['parameters']['frame_samp_err'].format(min_frame_samp, max_frame_samp)))
                        True
                except ValueError:
                    print('\n{}'.format(locale_toml['ui']['parameters']['frame_samp_err'].format(min_frame_samp, max_frame_samp)))
                    True

        # Frame height parameter
        if video_height <= max_frame_height:
            max_frame_height = int(round(video_height, 0))

        while True:
            try:
                frame_height = int(input(locale_toml['ui']['parameters']['frame_height'].format(min_frame_height,
                                                                                                max_frame_height)))

                if max_frame_height >= frame_height >= min_frame_height:
                    break
                elif frame_height == 0:
                    break
                else:
                    print('\n{}'.format(locale_toml['ui']['parameters']['frame_height_err'].format(min_frame_height, max_frame_height)))
                    True
            except ValueError:
                print('\n{}'.format(locale_toml['ui']['parameters']['frame_height_err'].format(min_frame_height, max_frame_height)))
                True

        # Video start datetime parameter
        while True:
            try:
                video_start_datetime = input(locale_toml['ui']['parameters']['video_start_datetime'])
                video_start_datetime_obj = datetime.strptime(video_start_datetime, '%Y-%m-%dT%H:%M:%S.%f')
                break
            except ValueError:
                print('\n{}'.format(locale_toml['ui']['parameters']['video_start_datetime_err']))
                True

        # Video recording timezone
        video_rec_timezone = input(locale_toml['ui']['parameters']['rec_timezone'])

        # Time offset parameter
        while True:
            try:
                time_offset = float(input(locale_toml['ui']['parameters']['time_offset'].format(min_time_offset,
                                                                                                max_time_offset)))

                if max_time_offset >= frame_sampling >= min_time_offset:
                    break
                else:
                    print('\n{}'.format(locale_toml['ui']['parameters']['time_offset_err'].format(min_time_offset, max_time_offset)))
                    True
            except ValueError:
                print('\n{}'.format(locale_toml['ui']['parameters']['time_offset_err'].format(min_time_offset, max_time_offset)))
                True

        # User-defined metadata
        print('\n{}'.format(locale_toml['ui']['info']['tags_title']))

        make = input(locale_toml['ui']['metadata']['make'])
        model = input(locale_toml['ui']['metadata']['model'])
        author = input(locale_toml['ui']['metadata']['author'])

    # Video metadata formatting
    print('\n{}'.format(locale_toml['processing']['reading_metadata']))
    video = cv2.VideoCapture(video_path)

    video_file_name = os.path.basename(video_path)
    video_file_size = byte_multiple(os.stat(video_path).st_size)
    video_duration = video_frame_number / video_fps

    video_start_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_offset)
    video_start_datetime = video_start_datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    video_start_subsectime = int(int(video_start_datetime_obj.strftime('%f')) / 1000)

    # metadata recap
    print('\n{}'.format(locale_toml['ui']['info']['metadata'].format(video_file_name,
                                                                      round(video_file_size[0], 3), video_file_size[1],
                                                                      video_duration, video_start_datetime,
                                                                      '{:03d}'.format(video_start_subsectime),
                                                                      video_rec_timezone)))

    # Output folder creation
    output_folder = '{}/{}'.format(output_folder, video_file_name)
    existing_path(output_folder)

    # Processes
    # Frame sampling + tagging (OpenCV + piexif)
    print('\n{}'.format(locale_toml['processing']['sampling']))

    i = 0

    if timelapse == True:
        frame_sampling = float(1 / video_fps)
        frame_interval = float(1 / timelapse_fps)
    else:
        frame_interval = frame_sampling

    cv2_tqdm_unit = locale_toml['ui']['unit']['cv2_tqdm']
    cv2_tqdm_range = int(video_duration / frame_sampling)

    for i in tqdm(range(cv2_tqdm_range), unit=cv2_tqdm_unit):
        t = frame_sampling * i * 1000
        video.set(cv2.CAP_PROP_POS_MSEC, t)
        ret, frame = video.read()

        # Image resizing
        if frame_height != video_height:
            resize_factor = frame_height / video_height
            image_height = frame_height
            image_width = int(round(video_width * resize_factor, 0))

            frame = cv2.resize(frame, (image_width, image_height), interpolation=cv2.INTER_LANCZOS4)

        frame_name = '{:05d}'.format(i)
        image_name = "{}_f{}.jpg".format(video_file_name.split('.')[0], frame_name)
        image_path = "{}/{}".format(output_folder, image_name)

        cv2.imwrite(image_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 88, cv2.IMWRITE_JPEG_PROGRESSIVE, 1, cv2.IMWRITE_JPEG_SAMPLING_FACTOR, 0x221111])

        # Time tags formatting
        time_shift = i * frame_interval
        current_datetime_obj = video_start_datetime_obj + timedelta(seconds=time_shift)
        current_datetime = current_datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
        current_subsec_time = int(int(current_datetime_obj.strftime('%f')) / 1000)

        # piexif code
        image_exif = piexif.load(image_path)

        image_tags = {
            piexif.ImageIFD.Make: make,
            piexif.ImageIFD.Model: model,
            piexif.ImageIFD.Artist: author,
            piexif.ImageIFD.Copyright: "{}, {}".format(author, video_start_datetime_obj.strftime('%Y')),
            piexif.ImageIFD.Software: 'video2geoframes.py (v{})'.format(__version__)
        }

        exif_tags = {
            piexif.ExifIFD.DateTimeOriginal: current_datetime,
            piexif.ExifIFD.SubSecTime: str(current_subsec_time),
            piexif.ExifIFD.OffsetTimeOriginal: video_rec_timezone
        }

        image_exif['0th'] = image_tags
        image_exif['Exif'] = exif_tags

        image_exif_bytes = piexif.dump(image_exif)
        piexif.insert(image_exif_bytes, image_path)

        i += 1

    # Geo-tagging (ExifTool)
    print('\n{}'.format(locale_toml['processing']['geotagging']))

    geotagging_cmd = '{} -P -geotag "{}" "-geotime<SubSecDateTimeOriginal" -overwrite_original "{}/{}_f*.jpg"'\
        .format(exiftool_path, gps_track_path, output_folder, video_file_name.split('.')[0])
    geotagging = os.system(geotagging_cmd)

    # End
    input('\n{}'.format(locale_toml['ui']['info']['end']))
except NotImplementedError:
    print('\n{}'.format(locale_toml['ui']['error']['not_implemented']))
except InterruptedError:
    input("\nEnd of program, press Enter to quit.")

