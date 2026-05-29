# USD Tools

## Overview

For now, it is not actually a collection of tools, but some tests of features of the technology.

___

<details>

<summary><h2 style="display:inline-block">Export Assets - BETA</h2></summary>

## Export Assets - BETA

Create an USD asset with its variants from a single Maya scene. A main USD file references the variants from other USD files.

## Known issues

- for now, the tool only exports one variant set ( called `resolutionSet` )
- for now, there are no progress bars, so the only way to see something happening is on Maya's Script Editor

## How to

Select the asset root group and run the tool.

The interface is really simple and the only thing to select is the base folder, where the files will be created.

<p align="center">
<img src="_images\ui.png"  width="50%" height="50%">
</p>

## How it works

The script relies on the node hierarchy to create the USD structure and variant files.

The hierarchy is the following:

<pre>
└─🔲[ASSET_NAME]
   └─🔲MESH
      └─🔲_var_[variant_name]
         └─🔲geo
            ├─🔘[mesh1]
            ├─🔘[mesh2]
            ├─🔘[mesh3]
            ├─🔘[...]
</pre>

> **[ASSET_NAME]** - the name of the asset. It is used as the folder name where all data for the asset will be located and 
also the name of the main USD file. No USD prim is created on this level

> **MESH** - a required group. A Xform prim is created on this level and the variants will be connected on it.

> **\_var_[variant_name]** - the name of the variant with `_var_` prefix. When the script is creating the files,
the `_var_` is set where the variant geometries are. No prim is created at this level.

> **geo** - all geometries for the variant must be placed inside this group. This and all groups below it will become 
Scope prims.

The script will use all this information to create one USD file for each variant and another USD file to reference the 
variants.

Final file structure is the following:

<pre>
└─📁[base_folder]
   └─📁[ASSET_NAME]
      ├─📁variants
      |  ├─📄[first_variant_name].usda
      |  ├─📄[second_variant_name].usda
      |  └─📄[...].usda
      └─📄[ASSET_NAME].usda
</pre>

## Result

This is a comparison of an asset as geometries inside Maya ( left ) and as USD file ( right ): 

<p align="center">
<img src="_images\outliner_compare.png"  width="50%" height="50%">
</p>

The variants can be accessed on the `MESH` prim, as shown bellow:

<p align="center">
<img src="_images\variants.png"  width="50%" height="50%">
</p>

## How it ***<ins>REALLY</ins>*** works

- fetches initial information from selection


- create a USD stage for each variant


- from the asset root node, goes over each node on the hierarchy, fetches more information and adds it to a 
specific class ( `OutlinerNode` )


- goes on each `OutlinerNode` and create prims based on the information collected before ( prim name, type, path )


- if the prim is of the type `mesh`, the script collects all information from the geometry ( vertices counts, indexes 
and positions ) and the UV sets ( UV indices for each UV set ). This is done so I can have control over the 
creation of each prim ( deciding which type I would like to create ), instead of using what the standard USD export 
would create


- create another USD stage for the "master" USD file


- reference every variant USD at the `MESH` level


- export the USD file

</details>

<br>

<details>

<summary><h2 style="display:inline-block">Export Assets - Maya 2027</h2></summary>

## Export Assets - Maya 2027

Create an USD asset with its variants from a single Maya scene. A main USD file references the variants from other USD files.

The USD file is saved on a selected folder with additional USD files.

This method uses the Maya 2027 `Create Component` tool as base to save the USD files.

## Known issues

- the `USD Variant Manager` screen will open empty at the end of the process, but it is because I'm using the `Create Component` tool


- some shader nodes might not export correctly

## How to

Select the asset root group and run the tool.

The interface is really simple and the only thing to select is the base folder, where the files will be created.

<p align="center">
<img src="_images\ui_maya_2027.png"  width="50%" height="50%">
</p>

## How it works

The script relies on the node hierarchy on the outliner to create the USD structure and variant files.

The hierarchy is the following:

<pre>
└─🔲[ASSET_NAME]
   └─🔲[VARIANT_SET]
      └─🔲[variant_name]
         ├─🔘[mesh1]
         ├─🔘[mesh2]
         ├─🔘[mesh3]
         ├─🔘[...]
</pre>

> **[ASSET_NAME]** - the name of the asset. It is used as the folder name where all data for the asset will be located and 
also the name of the main USD file. No USD prim is created on this level.

> **[VARIANT_SET]** - the name of the variant set that will be created on the USD file.

> **[variant_name]** - the name of the variant. All geometries under it will be included on the variant.

The script will use all this information to create one USD file for each variant and another USD file to reference the 
variants.

Variants are exported with the assigned material converted to MaterialX.

Final file structure is the following:

<pre>
└─📁[base_folder]
   └─📁[ASSET_NAME]
      ├─📁bind
      |  └─📄bind.usda
      ├─📁geo
      |  ├─📄geo.usda
      |  ├─📄[VARIANT_SET]_[variant_name].usdc
      |  └─📄...
      ├─📁mtl
      |  ├─📄mtl.usda
      |  ├─📄[VARIANT_SET]_[variant_name].usdc
      |  └─📄...
      ├─📄[ASSET_NAME].usda
      └─📄payload.usda
</pre>

## Result

A comparison of an asset as geometries inside Maya ( left ), and as USD file ( middle ) and its variants ( right ): 

<p align="center">
<img src="_images\outliner_maya_2027.png"  width="50%" height="50%">
</p>

</details>
