# video2geoframes.py

![Gitea Release](https://img.shields.io/gitea/v/release/lumathieu/video2geoframes.py?gitea_url=https%3A%2F%2Fgit.luc-geo.fr&include_prereleases&sort=semver&display_name=release&style=flat&link=https%3A%2F%2Fgit.luc-geo.fr%2Flumathieu%2Fvideo2geoframes.py%2Freleases)

_version 🇫🇷_

Programme Python permettant de générer un ensemble d'images géotaguées depuis une vidéo et une trace GPS.

Conçu pour faciliter la contribution à des projets de photo-cartographie de rue tels que Mapillary ou Panoramax.

## Démarrage rapide

Rien de plus simple : rassemblez votre vidéo, votre trace GPS, lancez le script Python et suivez le guide !

En détail, le programme est entièrement construit autour d'une TUI ou _Textual User Interface_, qui permet de lancer
facilement le traitement de la vidéo par la saisie pas-à-pas des paramètres.

La saisie est guidée par une aide textuelle indiquant les valeurs attendues.

Avant de lancer le script, vous avez besoin d'avoir :
* un fichier vidéo avec son horodatage exact (début) en temps local ou UTC 
* un fichier de trace GPS propre couvrant la durée de la vidéo
* un dossier de travail.

## Documentation

_A venir._

## Fonctionnalités

Le programme permet d'exécuter en un seul traitement les tâches suivantes :
* le séquençage de la vidéo selon un intervalle de temps
* l'horodatage incrémental de la séquence d'image
* l'export des images au format JPEG
* le géotaguage des images exportées à partir de la trace GPS.

Il inclut également :
* le support des vidéos timelapse
* le redimensionnement des images à une résolution inférieure à la vidéo d'origine tout en conservant le ratio
* l'ajout de métadonnées avec les tags EXIF `artist`, `make`, `model` et `copyright` (cf. [documentation ExifTool](https://exiftool.org/TagNames/EXIF.html))
* l'horodatage à la précision de la milliseconde
* le support du temps local décalé par rapport à UTC.
* l'ajout d'un décalage temporel pour mieux corréler la vidéo et la trace GPS.

Lors de l'export, un sous-dossier nommé selon la vidéo est créé automatiquement dans le répertoire de sortie.

### Comparaison v1 / v2

| Fonctionnalité                       | v1-beta    | v2-alpha9    |
|--------------------------------------|------------|--------------|
| Support des vidéos timelapse         | ✔️         | ✔️           |
| Écriture des tags EXIF               | ✔️         | ✔️           |
| Support des tags étendus             | ✔️         | ❌            |
| Support des millisecondes            | ✔️         | ✔️           |
| Affichage de la progression          | 🟡 brut    | ✔️           |
| TUI multilingue 🇺🇳                 | 🟡 limitée | ✔️           |
| Personnalisation de la configuration | ❌          | 🟡 partielle | 
| Personnalisation qualité JPEG        | ❌          | 🔄 planifié  |
| Paramétrage via TOML                 | ❌          | 🔄 planifié  |

## Langues
 
La TUI est multilingue grâce une base de "locales" sous forme de fichiers TOML (`locales/*.toml`) facilement extensible.

| Langue        | Locale  | Support     | Mainteneur   |
|---------------|---------|-------------|--------------|
| 🇺🇸 Anglais  | `en_us` | ✔️ 100 %    | @lumathieu   |
| 🇫🇷 Français | `fr_fr` | ✔️ 100 %    | @lumathieu   |
| 🇮🇹 Italien  | `it_it` | 🔄 planifié | @lumathieu ? |

## Versions

Voir [_Releases_](https://git.luc-geo.fr/lumathieu/video2geoframes.py/releases).

## Installation

Pour installer le programme, il suffit de cloner le dépôt Git, d'installer les dépendances logicielles et de construire
l'environnement Python. Il est recommandé d'utiliser un environnement virtuel (venv).

### Python

L'ensemble du projet est développé et testé avec **Python 3.11** (Windows x86-64).

### Dépendances

Le script principal utilise les librairies Python suivantes (voir aussi `requirements.txt`) :
- `numpy`
- `opencv-python`
- `piexif`
- `tomlkit`
- `tqdm`.

Il utilise également le programme [`ExifTool`](https://exiftool.org/) pour le géotaguage des images.
Appelée par une commande système, cette dépendance est prévue pour être supprimée dans les versions futures.

## Compatibilité

Le code est conçu pour être indépendant de la plateforme.

Les plateformes officiellement supportées sont Windows et Linux (partiellement testé sous Debian / Ubuntu).

## Contribution

_A venir._

Si vous intéressé pour contribuer au projet, vous pouvez envoyer un mail à campanu@luc-geo.fr.

## Licence

Ce dépôt, à l'exception des dépendances, est sous licence **GNU GPL v3**.

Les dépendances sont incluses au dépôt pour le développement et restent sous leur licence d'origine
(voir `dependencies/EXTRA_LICENSES.md`).