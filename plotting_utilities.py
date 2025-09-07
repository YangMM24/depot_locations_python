"""
This file contains the code for the various plotting functions that we provide
to you as part of this assignment.

You should keep this file in the same location as your country.py file.

You are not required to document or test any functions that are included as part
of this file.
You are welcome to delete this file from your final submission if you so wish; though
if you do so you should also remove the corresponding plotting functions from country.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import numpy as np
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from country import Country, Location


def polar_to_xy(data: np.ndarray[float]) -> np.ndarray[float]:
    """

    Converts polar to Cartesian coordinates

    Parameters
    ----------
    data : 2D array of shape (n, 2)
        (n, 2) theta, r pairs.

    Returns
    -------
    2D array of shape (n, 2)
        x,y pairs for the input polar coordinates.
    """
    xy_data = np.zeros_like(data)
    xy_data[:, 0] = data[:, 1] * np.cos(data[:, 0])
    xy_data[:, 1] = data[:, 1] * np.sin(data[:, 0])
    return xy_data


def plot_country(
    country: Country,
    distinguish_regions: bool = True,
    distinguish_depots: bool = True,
    location_names: bool = True,
    polar_projection: bool = True,
    save_to: Optional[Path | str] = None,
) -> Figure:
    """
    ABSTRACTED METHOD TO REDUCE VERBOSITY IN SUBMISSION FILES.
    See docstring in country.py:Country.plot_country
    """
    fig = plt.figure(figsize=(10.0, 10.0))
    if polar_projection:
        ax = fig.add_subplot(projection="polar")
    else:
        ax = fig.add_subplot()

    MARKERS = {"default": "o", "depot": "o"}
    if distinguish_depots:
        MARKERS["depot"] = "x"

    all_regions = set(loc.region for loc in country._all_locations)
    n_regions = len(all_regions)
    region_colourmap = {region: "b" for region in all_regions}
    if distinguish_regions and n_regions > 1:
        RGB_COLOURS = [
            wavelength_to_rgb(rgba)
            for rgba in np.linspace(380, 780, n_regions, endpoint=True)
        ]
        region_colourmap = {
            region: RGB_COLOURS[i] for i, region in enumerate(list(all_regions))
        }

    for region in all_regions:
        colour = region_colourmap[region]

        for is_depot in [True, False]:
            marker = MARKERS["depot"] if is_depot else MARKERS["default"]
            label = f"{region} (depots)" if is_depot and distinguish_depots else region

            locations_in_region = [
                loc
                for loc in country._all_locations
                if loc.region == region and loc.depot == is_depot
            ]
            data = np.array(
                [(loc.theta, loc.r) for loc in locations_in_region],
                dtype=(float, float),
            )
            if data.size == 0:
                continue
            elif not polar_projection:
                data = polar_to_xy(data)

            ax.scatter(
                data[:, 0],
                data[:, 1],
                c=colour,
                marker=marker,
                label=label,
            )

            if location_names:
                for i, loc in enumerate(locations_in_region):
                    if distinguish_depots and is_depot:
                        ax.annotate(loc.name.upper(), data[i, :], ha="center", va="top")
                    else:
                        ax.annotate(loc.name, data[i, :], ha="center", va="bottom")

    if distinguish_depots or distinguish_regions:
        ax.legend(
            bbox_to_anchor=(0.0, 1.04, 1.0, 0.2),
            loc="lower left",
            mode="expand",
            ncols=3,
        )
    fig.tight_layout()

    if save_to is not None:
        fig.savefig(save_to, bbox_inches="tight")
    else:
        fig.show()

    return fig


def plot_path(
    country: Country,
    path: List[Location],
    distinguish_regions: bool = True,
    distinguish_depots: bool = True,
    location_names: bool = True,
    polar_projection: bool = True,
    save_to: Optional[Path | str] = None,
) -> Figure:
    """
    ABSTRACTED METHOD TO REDUCE VERBOSITY IN SUBMISSION FILES.
    See docstring in country.py:Country.plot_path
    """
    fig = country.plot_country(
        distinguish_regions=distinguish_regions,
        distinguish_depots=distinguish_depots,
        location_names=location_names,
        polar_projection=polar_projection,
        save_to=None,  # Don't save in the internal method
    )

    # Pre-populated scatter diagram of the country, to save repeating.
    ax = fig.axes[0]
    is_polar = ax.name == "polar"

    # We just need to draw lines between the relevant points, so let's do that
    data = np.array([(loc.theta, loc.r) for loc in path], dtype=(float, float))
    if not is_polar:
        data = polar_to_xy(data)
    ax.plot(data[:, 0], data[:, 1], "--", marker=None)

    if save_to is not None:
        fig.savefig(save_to, bbox_inches="tight")
    else:
        fig.show()

    return fig


def wavelength_to_rgb(wavelength, gamma=0.8):
    """
    This converts a given wavelength of light within [380, 750]nm to an
    approximate RGB color value.
    Additionally the alpha value is set to 0.5 outside this range.

    Parameters
    ----------
    wavelength : float
        A wavelength value in nm between the visible range [380, 750].
    gamma : float, optional
        Desired alpha value of the output (the default is 0.8).

    Attention
    ---------
    This code is used in the plotting functions that we have provided to you.
    You are NOT required to document, test, nor edit this function.
    You are welcome to delete this function from your final submission,
    if you so wish.


    Notes
    -----
    Taken from http://www.noah.org/wiki/Wavelength_to_RGB_in_Python.

    Based on code by Dan Bruton http://www.physics.sfasu.edu/astro/color/spectra.html,
    """
    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 750:
        A = 1.0
    else:
        A = 0.5
    if wavelength < 380:
        wavelength = 380.0
    if wavelength > 750:
        wavelength = 750.0
    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 <= wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif 490 <= wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 <= wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif 580 <= wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif 645 <= wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    return (R, G, B, A)
