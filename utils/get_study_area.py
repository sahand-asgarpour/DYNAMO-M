"""Build the ``study_area`` structure consumed by the model.

================================ RECONSTRUCTED STUB ================================
Reconstruction of ``utils.get_study_area``. The original was never committed. This
version is rebuilt from how ``study_area`` is consumed downstream:

  * honeybees ``Area`` requires ``xmin/xmax/ymin/ymax`` keys.
  * ``Nodes.initiate_agents`` iterates ``study_area['admin']`` (a list of GeoJSON-like
    feature dicts). Features whose ``properties['id']`` ends with ``flood_plain``
    become ``CoastalNode``s (and load precomputed household files from DataDrive);
    all others become ``InlandNode``s.
  * ``CoastalNode`` reads ``properties['region']['indices']`` (global pixel
    (rows, cols)) and ``properties['region']['gt']`` (the population-raster GDAL
    geotransform) to map cells/agents onto rasters.
  * ``node_properties.centroids`` reads ``properties['centroid']`` ([lon, lat]).
  * ``MapReader.sample_geom`` reads ``feature['geometry']`` as a GeoJSON geometry.

The admin polygons come from the precomputed merged shapefile
``DataDrive/SLR/admin/can_flood_gadm_<level>_merged.shp`` (or the GDL equivalent),
which already contains both the inland (``<key>``) and flood-plain
(``<key>_flood_plain``) polygons. Region pixel indices are obtained by rasterizing
each flood-plain polygon onto the GHS population grid.

CAVEAT: the rasterization here is a faithful-effort reconstruction. It is internally
consistent (pixel<->coord round-trips on the population grid), and the model's
``get_agent_indice_admin_cells`` nearest-cell fallback tolerates minor mismatches,
but exact cell membership may differ from whatever produced ``locations.npy``.
Treat downstream numerics as PLACEHOLDER until the original utils are restored.
===================================================================================
"""
import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.windows import Window
from rasterio.features import geometry_mask
from shapely.geometry import mapping

DATA_FOLDER = "DataDrive"
POPULATION_RASTER = os.path.join(DATA_FOLDER, "POPULATION", "GHS_POP_2015.tif")


def _as_area_list(area):
    return area if isinstance(area, (list, tuple)) else [area]


def _key_in_area(key, areas):
    """A merged-shapefile key (e.g. 'NLD.3_1' or 'NLD.3_1_flood_plain') is in scope
    if its ISO3 prefix matches one of the requested areas."""
    return any(key == a or key.startswith(a + ".") for a in areas)


def _household_folder_exists(base_key, admin_level):
    """Return True if precomputed household files exist for ``base_key`` under any
    size folder. Flood-plain features without agent data must be skipped, otherwise
    ``Nodes.initiate_agents`` raises FileNotFoundError."""
    root = os.path.join(DATA_FOLDER, "SLR", f"households_gadm_{admin_level}_2015")
    if not os.path.isdir(root):
        return False
    for size in os.listdir(root):
        candidate = os.path.join(root, size, base_key, "locations.npy")
        if os.path.exists(candidate):
            return True
    return False


def _rasterize_region(geom_shapely, src, gt_global):
    """Rasterize a single polygon onto the population grid and return the global
    pixel indices (rows, cols) plus the global GDAL geotransform."""
    minx, miny, maxx, maxy = geom_shapely.bounds

    # Window covering the polygon's bounding box (clamped to raster extent).
    row_start, col_start = src.index(minx, maxy)  # upper-left
    row_stop, col_stop = src.index(maxx, miny)    # lower-right
    row_off = max(0, min(row_start, row_stop))
    col_off = max(0, min(col_start, col_stop))
    row_end = min(src.height, max(row_start, row_stop) + 1)
    col_end = min(src.width, max(col_start, col_stop) + 1)
    height = max(1, row_end - row_off)
    width = max(1, col_end - col_off)

    window = Window(col_off, row_off, width, height)
    win_transform = src.window_transform(window)

    # invert=True -> True inside the polygon.
    mask_inside = geometry_mask(
        [mapping(geom_shapely)], out_shape=(height, width),
        transform=win_transform, invert=True, all_touched=True,
    )
    rows, cols = np.where(mask_inside)

    if rows.size == 0:
        # Fallback: use the single pixel containing the centroid.
        c = geom_shapely.centroid
        r, cc = src.index(c.x, c.y)
        rows = np.array([r], dtype=np.int64)
        cols = np.array([cc], dtype=np.int64)
    else:
        rows = (rows + row_off).astype(np.int64)
        cols = (cols + col_off).astype(np.int64)

    return {"indices": (rows, cols), "gt": gt_global}


def get_study_area(area, subdivision="GADM", admin_level="1", coastal_only=False):
    areas = _as_area_list(area)

    if subdivision == "GADM":
        shp = os.path.join(DATA_FOLDER, "SLR", "admin",
                           f"can_flood_gadm_{admin_level}_merged.shp")
    elif subdivision == "GDL":
        shp = os.path.join(DATA_FOLDER, "SLR", "admin", "can_flood_gdl_merged.shp")
    else:
        raise ValueError(f"Unknown subdivision '{subdivision}'")

    if not os.path.exists(shp):
        raise FileNotFoundError(f"Merged admin shapefile not found: {shp}")

    gdf = gpd.read_file(shp)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    gdf = gdf[gdf["keys"].astype(str).apply(lambda k: _key_in_area(k, areas))]
    if len(gdf) == 0:
        raise ValueError(f"No admin regions found for area={areas} in {shp}")

    src = rasterio.open(POPULATION_RASTER, "r")
    gt_global = src.transform.to_gdal()

    admin = []
    selected_geoms = []
    for _, row in gdf.iterrows():
        key = str(row["keys"])
        geom_shapely = row["geometry"]
        if geom_shapely is None or geom_shapely.is_empty:
            continue
        is_flood_plain = key.endswith("flood_plain")

        if coastal_only and not is_flood_plain:
            continue

        if is_flood_plain:
            base_key = key.replace("_flood_plain", "")
            if not _household_folder_exists(base_key, admin_level):
                # No precomputed agents -> skip to avoid a downstream crash.
                continue

        centroid = geom_shapely.centroid
        properties = {"id": key, "centroid": [centroid.x, centroid.y]}
        if is_flood_plain:
            properties["region"] = _rasterize_region(geom_shapely, src, gt_global)

        admin.append({
            "type": "Feature",
            "geometry": mapping(geom_shapely),
            "properties": properties,
        })
        selected_geoms.append(geom_shapely)

    src.close()

    if not admin:
        raise ValueError(
            f"No usable admin regions for area={areas} (subdivision={subdivision}). "
            "Check that the merged shapefile and household folders are present."
        )

    bounds = gpd.GeoSeries(selected_geoms, crs="EPSG:4326").total_bounds
    study_area = {
        "admin": admin,
        "xmin": float(bounds[0]),
        "ymin": float(bounds[1]),
        "xmax": float(bounds[2]),
        "ymax": float(bounds[3]),
    }
    return study_area

