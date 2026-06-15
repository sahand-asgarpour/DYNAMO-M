"""Write agent attributes to a GeoTIFF.

================================ RECONSTRUCTED STUB ================================
Minimal reconstruction of ``utils.mapping.create_agent_geotif``. Called only by
``Nodes.export_agent_density`` / ``export_agent_exposure`` which are gated behind
``settings['general']['export_agent_tiffs']`` (False in the test). Implemented
functionally so it works if enabled, but not validated against the original.
===================================================================================
"""
import numpy as np
import rasterio
from rasterio.transform import Affine
from honeybees.library.raster import coords_to_pixels


def create_agent_geotif(array, attribute, coords, gt, output_fn):
    """Accumulate ``attribute`` values at ``coords`` into ``array`` and write a GeoTIFF.

    Args:
        array: 2D numpy array sized like the study-area raster (will be filled).
        attribute: 1D values to accumulate, one per coordinate.
        coords: (n, 2) array of (lon, lat) coordinates.
        gt: geotransformation as a GDAL 6-tuple or rasterio Affine.
        output_fn: output file path.
    """
    array = np.asarray(array).copy()
    coords = np.asarray(coords, dtype=np.float64)
    attribute = np.asarray(attribute)

    if isinstance(gt, Affine):
        gt_tuple = gt.to_gdal()
        transform = gt
    else:
        gt_tuple = tuple(gt)
        transform = Affine.from_gdal(*gt_tuple)

    pxs, pys = coords_to_pixels(coords, gt_tuple)
    height, width = array.shape
    valid = (pxs >= 0) & (pxs < width) & (pys >= 0) & (pys < height)
    np.add.at(array, (pys[valid].astype(np.int64), pxs[valid].astype(np.int64)),
              attribute[valid])

    with rasterio.open(
        output_fn, "w", driver="GTiff", height=height, width=width, count=1,
        dtype=array.dtype, crs="EPSG:4326", transform=transform,
    ) as dst:
        dst.write(array, 1)
    return output_fn

