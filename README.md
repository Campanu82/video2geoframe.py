# video2geoframes.py

Python program to generate a collection of geotagged images from a video and a GPS track.

Designed for contribution to street-level imagery projects like Mapillary or Panoramax.

## Notes

This program was originally designed for personal use to contribute to Mapillary then Panoramax with a smartphone
(video mode) or a dashcam.

This v1 is the last version of the original code, published "as it is" with certain known bugs and limitations.

Since June 2024, a [v2](https://git.luc-geo.fr/lumathieu/video2geoframes.py/src/branch/v2) was started to develop with
the aim of :
* enhance performances
* fix known bugs
* clean code
* remove non-Python dependencies
* implement more flexible configuration with TOML.

## ⚠ Bugs and limitations

| Report                                                                                               | Workaround                                            |
|------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| [bug] in non-timelapse mode, **FFmpeg** doesn't extract first video frame and shifts every timestamp | 🔃 adding chosen framesampling interval to GPS offset |
| [bug] **ExifTool** timestamp very long (< 1 frame / s)                                               | ❌                                                     |  
| [bug] uncontrolled incrementation if export directory is on a Samba share (ZFS)                      | ❌                                                     |
| 9999 frames limit (naming model)                                                                     | ❌                                                     |

## License

This repository, except dependencies, is licensed under **GNU GPL v3**.

Dependencies are included in repository for development and keep their original license.