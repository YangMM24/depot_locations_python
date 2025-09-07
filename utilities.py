from __future__ import annotations

import string

import numpy as np
from pathlib import Path

from country import Country, Location


def read_country_data(file_path: Path) -> Country:
    """
    Read location data from a CSV file and create a Country object.
    
    Parameters
    ----------
    file_path : Path
        Path to the CSV file containing location data.
        
    Returns
    -------
    Country
        A Country object containing all locations from the CSV file.
    """
    # Read CSV file with numpy
    data = np.genfromtxt(file_path, delimiter=',', dtype=None, encoding='utf-8', names=True)
    
    # Create Location objects
    locations = []
    for row in data:
        location = Location(
            name=row['location'].strip(),
            region=row['region'].strip(),
            r=float(row['r']),
            theta=float(row['theta']),
            depot=bool(row['depot'])
        )
        locations.append(location)
        
    # Create and return Country object
    return Country(locations)


def regular_n_gon(number_of_settlements: int) -> Country:
    """
    Returns a Country that has a single depot and number_of_settlements settlements.
    The settlements are arranged as the vertex points in a regular n-gon, each point
    of which is a distance 1.0 from the origin.

    The settlements are named alphabetically, starting from the settlement at the point
    (1.0, 0.0) and proceeding COUNTER-CLOCKWISE.
    Settlement names are generated as
        A, B, C, D, ... X, Y, Z, Za, Zb, Zc, ..., Zx, Zy, Zz, Zza, Zzb, ... etc.
    The depot at the origin is always named Origin. All settlements and the origin belong
    to a single region, named "Region".

    If you are still unsure about the arrangement of settlements within the Country that
    this function produces, we recommend you run the plot_country method on the output of
    this function for different input arguments. The assignment test also contains an
    illustration.

    SPECIAL CASES:
    - If the number of settlements is 0, there will be no settlements.
    - If the number of settlements is 1, a single settlement at (1.0, 0.0) will be placed.
    - If the number of settlements is 2, two settlements at (1.0, 0.0) and (1.0, pi) will be placed.

    Attention
    ---------
    You are not required to document or test THIS function, but you are welcome
    to use this function within your testing framework (to generate data, for example).
    Do not remove this function from your final submission.
    Do not make edits to this function.

    Parameters
    ----------
    number_of_settlement : int
        Number of settlement to be created

    Returns
    -------
    Country
        A Country that has a single depot and number_of_settlements settlements.
    """
    # Set region name
    region_name = "Region"
    # Origin is a depot
    origin = Location("Origin", region_name, 0.0, 0.0, True)

    if number_of_settlements == 0:
        settlements = []
    else:
        polar_angles = np.linspace(
            0.0, 2 * np.pi, endpoint=False, num=number_of_settlements
        )
        polar_angles[polar_angles > np.pi] -= 2 * np.pi

        settlements = [
            Location(
                (("z" * (i // 26)) + string.ascii_lowercase[i % 26]).capitalize(),
                region_name,
                1.0,
                theta,
                False,
            )
            for i, theta in enumerate(polar_angles)
        ]
    return Country(settlements + [origin])
