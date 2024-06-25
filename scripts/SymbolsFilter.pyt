# -*- coding: utf-8 -*-import reimport arcpyfrom helpers import get_selected_featuressys.dont_write_bytecode = TrueDEBUG_MODE = Falseclass Toolbox:    def __init__(self):        """Define the toolbox (the name of the toolbox is the name of the        .pyt file)."""        self.label = "Geocover"        self.alias = "Geocover"        # List of tool classes associated with this toolbox        self.tools = [SymbolFilter]class SymbolFilter:    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "SymbolFilter"        self.description = ""    def getParameterInfo(self):        """Define the tool parameters."""        # First parameter        param0 = arcpy.Parameter(            displayName="Input Features",            name="in_features",            datatype="GPFeatureLayer",            parameterType="Required",            direction="Input",        )        # Second parameter        param1 = arcpy.Parameter(            displayName="Input File",            name="in_file",            datatype="DEFile",            parameterType="Required",            direction="Input",        )        param0.values = "Mapsheet"        param1.values = (            r"H:\code\lg-geology-data-model\exports\layer_symbols_rules.json"        )        params = [param0, param1]        return params    def isLicensed(self):        """Set whether the tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter. This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        from filter_symbols import process_layers_symbols        # from export_symbol_rules import arcgis_table_to_df  # Twice imported        from utils import arcgis_table_to_df  # Twice imported        import geopandas as gpd        import pandas as pd        import json        """from arcgis.geometry import Geometry        from shapely.geometry import shape"""        from filter_symbols import process_layer        inLayer = parameters[0].valueAsText        inSymbolsFile = parameters[1].valueAsText        spatial_filter = None        try:            # Read the mask file (shapefile or GeoJSON)            spatial_filter = get_selected_features(inLayer)            # Assuming the mask is a single geometry, you can dissolve to create a single unified geometry            # mask_geom = mask_gdf.unary_union            messages.addMessage(f"{spatial_filter}, type={type(spatial_filter)}")        except Exception as e:            messages.addErrorMessage(e)        messages.addMessage("{0} has no features.".format(spatial_filter))        with open(inSymbolsFile, "r") as f:            layers = json.load(f)        # messages.addMessage("{0} has no features.".format(layers.keys()))        results = {}        dataset = None        for layername in layers.keys():            messages.addMessage(f"--- {layername} ---")            data = layers.get(layername)            # messages.addMessage(data)            datasource = data.get("dataSource")            # messages.addMessage(f"datasource={datasource}")            dataset = None            m = re.findall(",Dataset=(.*)", datasource)            if m and len(m) > 0:                dataset = m[0]  # .split(".").pop()            feature_dataset = None            m = re.findall(",Feature Dataset=(.*),", datasource)            if m and len(m) > 0:                feature_dataset = m[0].split(".").pop()            # TTEC_LIM_TYP            try:                messages.addMessage(f"    dataset={dataset}")                messages.addMessage(f"    feature dataset={feature_dataset}")                renderer = data.get("renderer")            except Exception as e:                messages.addWarningMessage(                    f"    Cannot get renderer for {layername}: {e}"                )                continue            if dataset is None:                messages.addWarningMessage(f"    No dataset found for {layername}")                continue            feature_class_path = dataset            DEFAULT_WORKSPACE = r"h:/connections/GCOVERP@osa.sde"            arcpy.env.workspace = DEFAULT_WORKSPACE            # Get the selected features using a search cursor with spatial filter            selected_features = []            gdf = arcgis_table_to_df(feature_class_path, spatial_filter=spatial_filter)            """with arcpy.da.SearchCursor(                feature_class_path,                ["OID@", "SHAPE@"],                spatial_filter=spatial_filter,                search_order="SPATIALFIRST",            ) as cursor:                for row in cursor:                    selected_features.append(row)"""            # unfiltered_gdf = gpd.read_file(gdb_path, layer=dataset, bbox=bbox)            messages.addMessage(f"    count={len(gdf)}")            if DEBUG_MODE:                messages.addMessage(f"    {renderer}")                messages.addMessage(f"    {gdf.columns}")            # TODO: this should be dynamic            if "Bedrock_HARMOS" in layername:                df = arcgis_table_to_df("TOPGIS_GC.GC_BED_FORM_ATT")                messages.addMessage(df)                messages.addMessage(gdf)                gdf = gdf.merge(df, left_on="FORM_ATT", right_on="UUID")                messages.addMessage(f"     ====== MERGING")                messages.addMessage(gdf)                return            messages.addMessage(f"    {gdf.columns}")            rules = process_layer(layername, gdf, renderer)            results[layername] = rules            messages.addMessage(f"     {json.dumps(rules, indent=4)}")        # gdf = unfiltered_gdf[unfiltered_gdf.intersects(mask_geom)]        return    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        return