# Zip Render

## Overview

The tool compacts renders into a zip file with the project's directory structure.

To work properly, download 7-Zip from the [download page](https://www.7-zip.org/download.html) and install it on the default location.

> 7-Zip is a free, open-source file archiver and compression utility for Windows, designed to create, manage, and extract compressed files

## Use cases

Send renders to a client/vendor/freelancer and keep the same project structure.

By maintaining the folder structure, the user can just decompress the zip file over the previous folder and the new files will be added to the correct locations.

## Known issues

- the script uses 7-Zip to compress the files. It will not work if it's not installed on the default path ( `C:\Program Files\7-Zip` ).

- if the amount of files if very large, it'll take a lot of time to be compressed. 

## How to use it

- select the folder to save the zip file
- select the base folder
- click `zip files`

## Base folder

The base folder is the main path that will **NOT** be included on the folder structure inside the zip file.

Its purpose is to avoid the creation of an unnecessary large folder structure inside the zip file.

Example:
 
<table>
<tr style="vertical-align: top;">
    <td>Without base folder set</td>
    <td>Base folder set to:<br>
        <pre>E:\Projects\[PROJECT NAME]\Maya\images</pre></td>
</tr>
<tr style="vertical-align: top;">
<td>
<pre>
──📁Projects
   └─📁[PROJECT NAME]
      └─📁Maya
         └─📁images
            └─📁RENDER
               └─📁ZOMBIE
                  └─📁CHAR
                     └─📁v3
</pre>
</td>
<td>
<pre>
└─📁RENDER
   └─📁ZOMBIE
      └─📁CHAR
         └─📁v3
</pre>
</td>
</tr></table>
