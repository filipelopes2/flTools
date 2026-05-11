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
       └─📁archive_scenes
          └─🖹README.md
       └─📁camera_keyframer
          └─🖹README.md
       └─📁[...]
```

> [!NOTE]
> All scripts were tested on **Maya 2026**.

## How to install

- download the code and unzip it on any location ( e.g. `D:/Maya_Scripts` )


- edit the file `flTools.mod` with the path for the flTools folder. e.g:

```
+ flTools any D:/Maya_Scripts/flTools
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

<br>
<div style="text-align: center;">
<img src="_images\fltools_menu.jpg"  width="100%" height="100%">
</div>
