# video2geoframes.py

![Gitea Release](https://img.shields.io/gitea/v/release/lumathieu/video2geoframes.py?gitea_url=https%3A%2F%2Fgit.luc-geo.fr&include_prereleases&sort=semver&display_name=release&style=flat&link=https%3A%2F%2Fgit.luc-geo.fr%2Flumathieu%2Fvideo2geoframes.py%2Freleases)

_🇬🇧 version_

Python program to generate a collection of geotagged images from a video and a GPS track.

Designed for ease contribution to street-level imagery projects like Mapillary or Panoramax.

## Quick start

Nothing simpler : collect your video, your GPS track, execute Python script and follow the guide !

In detail, the program is built around a TUI or _Textual User Interface_, allowing to launch video process easily with
step-by-step parameter input.

Input is guided by textual help indicating expected values.

Before script starting, you need to have :
* a video file (export limited to 10000 frames)
* known the exact timestamp (start) in local time or UTC
* a clean GPS tack file covering video duration
* a working directory.

## Documentation

_Coming soon._

## Features

Program allows in one process to execute following tasks :
* video sampling according to a time interval
* incremental timestamp of frame sequence
* frames export to JPEG format
* exported frames geotagging from GPS track.

It also includes :
* timelapse video support
* frame resizing to a less resolution than original video with ratio keeping
* metadata adding in EXIF tags `artist`, `make`, `model` et `copyright` (see [documentation ExifTool](https://exiftool.org/TagNames/EXIF.html))
* millisecond accuracy timestamp
* local time support with UTC offset
* temporal offset adding for correlate video and GPS.

### Features v1 / v2

| Features                    | v1-beta    | v2-alpha9  |
|-----------------------------|------------|------------|
| Timelapse video support     | ✔️         | ✔️         |
| EXIF tags writing           | ✔️         | ✔️         |
| Extended tags support       | ✔️         | ❌          |
| Milliseconds support        | ✔️         | ✔️         |
| Progress displaying         | 🟡 raw     | ✔️         |
| Multilingual TUI 🇺🇳       | 🟡 limited | ✔️         |
| Configuration customization | ❌          | 🟡 partial | 
| JPEG quality customization  | ❌          | 🔄 planned |
| TOML process setting        | ❌          | 🔄 planned |

## Languages
 
TUI is multilingual thanks to "locales" base in the form of TOML files (`locales/*.toml`) easily extensible.

| Languages    | Locale  | Support    | Maintainer   |
|--------------|---------|------------|--------------|
| 🇺🇸 English | `en_us` | ✔️ 100 %   | @lumathieu   |
| 🇫🇷 French  | `fr_fr` | ✔️ 99 %    | @lumathieu   |
| 🇮🇹 Italian | `it_it` | 🔄 planned | @lumathieu ? |

## Versions

See [_Releases_](https://git.luc-geo.fr/lumathieu/video2geoframes.py/releases).

## Setup

To set up program, be enough to clone Git repository, set up software dependencies and build Python environnement.
Recommended to use a virtual environnement (venv).

### Python

Entire project is developed and tested on **Python 3.11** (Windows x86-64).

### Dependencies

Core script uses following Python libraries (see also `requirements.txt`) :
- `numpy`
- `opencv-python`
- `piexif`
- `tomlkit`
- `tqdm`.

It also uses [`ExifTool`](https://exiftool.org/) for frame geotagging.
Call by a system command, this dependency is intended to be removed in future versions.

## Compatibility

Code is designed to be platform-independent.

At time, code as been "tested" on Windows and Linux platforms (partially under Debian / Ubuntu).

## Contribution

_Coming soon._

If you are interested to project contribution, you can send a mail to campanu@luc-geo.fr.

## License

This repository, except dependencies, is licensed under **GNU GPL v3**.

Dependencies are included in repository for development and keep their original license
(see `dependencies/EXTRA_LICENSES.md`).
