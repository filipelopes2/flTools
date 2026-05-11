# Lookdev Scene

## Overview

Imports a scene to help create lookdevs.

Usually the scene has standard lights, animations and render settings.

## Use cases

Have some standard scenes on a local network folder and use it across many projects.

## Known issues

The tool can only copy the files if is on an accessible folder. If a texture cannot be read, it will not be copied.

e.g. If a scene has a texture from the `C:/` folder, it might not be imported using another machine.

## How to use it

1. select the folder which the textures will be copied to. A folder inside the project is recommended


2. click on the thumbnail to import the scene

<br>
<div style="text-align: center;">
<img src="_images\lookdev_scenes-howto_1.png"  width="75%" height="75%">
</div>

>   **Note:** the script will import the scene, copy the scene files and adjust its nodes to use the files from the new location

<br>
<div style="text-align: center;">
<a href="_images\lookdev_scenes-howto_2.jpg" target="_blank">
<img src="_images\lookdev_scenes-howto_2.jpg"  width="75%" height="75%">
</a>
</div>


# How to add new scenes

- create a scene. If the tool is gonna be used on other machines, make sure all textures are located on a folder accessible to them, or else the script will not be able to copy the textures


- create a 480 x 270 thumbnail with the following pattern name
> `[name you want]_[plugin]-thumb.png`

example:
> `lookdev_base_arnold_001-thumb.png`

- save the scene and the thumbnail on the `resources\scenes` folder. The scene must have the same name of the thumbnail, except for the `-thumb.png` that must be `.ma`

example:
<pre>
└─📁[...]
   └─📁resources
      └─📁scenes
         └─📄day_time_arnold_001.ma
         └─🖼️day_time_arnold_001-thumb.png
         └─📄lookdev_base_arnold_001.ma
         └─🖼️lookdev_base_arnold_001-thumb.png
         └─📄studio_arnold_001.ma
         └─🖼️studio_base_arnold_001-thumb.png
         └─[...]
</pre>

