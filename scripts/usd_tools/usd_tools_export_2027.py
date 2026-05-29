import maya.cmds as cmds
import mayaUsd.ufe
from usd_component_creator_plugin import create_component, export_options
from usd_component_creator_plugin.filepath import RemoveFileContext
from AdskUsdComponentCreator import Options, ComponentAPI
from typing import List

from startup.ui_functions import UiFunctions


class UsdToolsLogic2027:

    def __init__(self):
        self.asset_name = None
        self.base_folder = None
        self.stage = None
        self.options = None
        self.variant_list = None
        self.variant_selection = None
        self.variant_set = None

    def export_usd(self) -> None:
        self._set_options()
        self._create_multi_variants_component_from_nodes(self.variant_selection, self.options)
        self._save_layers()

    def _set_options(self) -> None:
        # These options will override the default options on
        # usd_component_creator_plugin.export_options._get_full_export_options_text

        self.options = Options()
        self.options.at_origin = False
        self.options.center_component = False
        self.options.component_filename = f'{self.asset_name}.usd'
        self.options.component_folder = self.base_folder
        self.options.component_name = self.asset_name
        self.options.component_prim_path_pattern = '/root'
        self.options.dropped_paths = []
        self.options.erased_paths = []
        self.options.file_extension = 'usda'
        self.options.filename_pattern = '{component_folder}/{component_name}/{component_filename}.{file_extension}'
        self.options.flatten_source = False
        self.options.ignore_incompatibilities = False
        self.options.imageable_purpose = ''
        self.options.include_bindings = True
        self.options.include_materials = True
        self.options.include_meshes = True
        self.options.variant_set_name_pattern = self.variant_set
        self.options.variant_set_numbered_pattern = f'{self.variant_set}_<n>'

    def _create_multi_variants_component_from_nodes(self, nodes: List[str], options: Options) -> None:
        # code adapted from maya usd plugin
        # C:\Program Files\Autodesk\MayaUSD\Maya2027\0.36.0\mayausd\MayaUSD\lib\python\usd_component_creator_plugin

        # input_usd_filename = create_component.create_component._generate_unique_temp_filename(options)
        input_usd_filename = create_component._generate_unique_temp_filename(options)
        with RemoveFileContext(input_usd_filename, ignore_errors=True):
            # Note: we process the nodes in reverse alphabetical order so that the
            #       first node alphabetically becomes the default variant, by virtue
            #       of being processed last. Variants in USD are ordered alphabetically,
            #       and we will want the first one set as default.
            for node in reversed(sorted(nodes, key=lambda n: n.split('|')[-1])):
                # create_component.create_component._update_options_for_node(options, node, None)
                # create_component.export_options.export_to_USD_for_component_creation([node], input_usd_filename)
                create_component._update_options_for_node(options, node, None)
                export_options.export_to_USD_for_component_creation([node], input_usd_filename)
                component_info = ComponentAPI.CreateFromFile(input_usd_filename, options)
                # Track the component from each info to make sure strong references are kept
                # for the variant layers of each create call. The proxy shape is not created yet,
                # so the component's layer wont automatically be tracked.
                create_component.MayaComponentManager.GetInstance().AddComponent(component_info.stage)

        target_default_variant = True
        create_component._post_creation_finalization(component_info, nodes, target_default_variant)

    def _save_layers(self) -> None:
        proxy_name = 'mayaUsdProxy1'
        proxy_shape = cmds.listRelatives(proxy_name, shapes=True, f=True)[0]
        stage = mayaUsd.ufe.getStage(proxy_shape)
        layers = stage.GetUsedLayers()
        for layer in layers:
            if not layer.anonymous:
                print(layer.identifier)
                layer.Save()
        cmds.delete(proxy_name)
