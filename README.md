<br>
<div style="text-align: center;">
<img src="_images\fltools_logo.jpg"  width="100%" height="100%">
</div>

## Overview

flTools is a series of scripts I developed to help me on some projects I've worked using Maya.

These scripts are not dependant or related, and each one has its own `README` file with instructions on how to use them.

```
 └─📁flTools
    └─📁scripts
       ├─📁archive_scenes
       |  └─🖹README.md
       ├─📁camera_keyframer
       |  └─🖹README.md
       └─📁[...]
```

> [!NOTE]
> All scripts were tested on **Maya 2026**.

## Available tools

- [Archive Scenes](https://github.com/filipelopes2/flTools/tree/main/scripts/archive_scenes) - creates a zip file with all resources for each Maya scene selected


- [Camera Keyframer](https://github.com/filipelopes2/flTools/tree/main/scripts/camera_keyframer) - creates keyframes on the selected camera, and it's respective aim ( if it exists )


- [Collapse UVs](https://github.com/filipelopes2/flTools/tree/main/scripts/collapse_uvs) - copies UVs from different UV Sets to a `map1` UV Set and deletes the other UV Sets


- [Duplicate Camera](https://github.com/filipelopes2/flTools/tree/main/scripts/duplicate_camera) - creates a new camera with the same parameters of a selected camera, but baked


- [Fix Normals](https://github.com/filipelopes2/flTools/tree/main/scripts/fix_normals) - fix face normals of a polygon mesh


- [Lookdev Scenes](https://github.com/filipelopes2/flTools/tree/main/scripts/lookdev_scenes) - imports a scene to help create lookdevs


- [Move All Maker](https://github.com/filipelopes2/flTools/tree/main/scripts/move_all_maker) - creates three controls parented to a joint and connects them to the selected objects


- [Random Color Shaders](https://github.com/filipelopes2/flTools/tree/main/scripts/random_color_shaders) - creates an aiStandardSurface shader with a random color for each selected object


- [USD Tools](https://github.com/filipelopes2/flTools/tree/main/scripts/usd_tools) - not actually a collection of tools, but some tests of features of the technology


- [Yeti Tools](https://github.com/filipelopes2/flTools/tree/main/scripts/yeti_tools) - functions to help create initial graph nodes for hair and fur creation


- [Zip Render](https://github.com/filipelopes2/flTools/tree/main/scripts/zip_render) - compacts renders into a zip file with the project's directory structure

## How to install

- download the code and unzip it on any location ( e.g. `D:/Maya_Scripts` )


- edit the file `flTools.mod` with the path for the flTools folder. e.g:

```
+ flTools any D:/Maya_https://github.com/filipelopes2/flTools/tree/main/scripts/flTools
```

- copy `flTools.mod` into Maya's modules folder ( e.g. `C:\Program Files\Autodesk\Maya2026\modules` )

```
 └─📁[...]
    └─📁Autodesk
       └─📁Maya[version]
          └─📁modules
             └─🖹flTools.mod
```

- start Maya and you'll find the tools on the top menu

## How it works

- upon start, Maya reads the .mod file and adds the script folder as a module


- userSetup.py is executed and the menu is created


- inside the script files there are a number of attributes that are read by the startup script and each tool is added to the menu

<p align="center">
<img src="_images\fltools_menu.jpg"  width="100%">
</p>
