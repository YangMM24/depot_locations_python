from __future__ import annotations

from math import pi, sqrt, cos
import warnings

from typing import TYPE_CHECKING, List, Optional, Union, Tuple

from plotting_utilities import plot_country, plot_path

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.figure import Figure


def travel_time(
    distance: float,
    different_regions: int,
    locations_in_dest_region: int,
    speed: float = 4.75,
) -> float:
    """
    Calculate travel time between two locations.

    Parameters
    ----------
    distance: float
        Physical distance between the locations, in metres. 
        Must be a non-negative number.
    different_regions: int or float
        "Different Regions" is equal to 1 if the locations 
        belong to different regions, and 0 otherwise.
        Only accepts 0, 1, 0.0, or 1.0. Other values will raise a ValueError.
    locations_in_dest_region: int
        “Locations in Destination Region” is equal to the number 
        of locations in the same region as themdestination location
        (including the destination itself).
        If less than 1, it will be set to 1.
    speed : float, default: 4.75
        Travel speed in meters per second. 
        The default speed is 4.75 m/s. 
        If a different speed is needed, specify it as a float.

    Returns
    -------
    float
        The calculated travel time in hours.
    """
    #
    if distance < 0:
        raise ValueError("Distance must be a non-negative number.")

    # Ensure different_regions is exactly 0, 1, 0.0, or 1.0
    if different_regions not in {0, 1, 0.0, 1.0}:
        raise ValueError("Different_regions must be 0, 1, 0.0, or 1.0.")
    
    # If locations_in_dest_region is less than 1, it will be set to 1.
    locations_in_dest_region = max(1, int(locations_in_dest_region))

    time = (1 / 3600) * (distance / speed) * (1 + (different_regions * locations_in_dest_region) / 10)
    return time

class Location:
    def __repr__(self):
        """
        Do not edit this function.
        You are NOT required to document or test this function.

        Not all methods of printing variable values delegate to the
        __str__ method. This implementation ensures that they do,
        so you don't have to worry about Locations not being formatted
        correctly due to these internal Python caveats.
        """
        return self.__str__()
    
    # Creating Locations
    def __init__(self, name, region, r, theta, depot):
        """
        Initializes a Location instance with name, region, polar coordinates, and depot status.
        
        Parameters
        ----------
        name : str
            Name of the location.
        region : str
            Region of the location.
        r : float
            Radial distance (non-negative).
        theta : float
            Angle in radians 
            (Is greater than or equal to minus pi is less than or equal to pi).
        depot : bool
            True if the location is a depot, otherwise False.
            Depot must be a boolean value
        
        Raises
        ------
        TypeError : If name or region is not a string, or if depot is not a boolean.
        ValueError : If r is negative, or theta is out of the specified range.
        """

        # The depot value should always be passed in as a bool.
        # Validate and set depot
        if not isinstance(depot, bool):
            raise TypeError("Depot must be a boolean value.")
        self._depot = depot
        
        # The polar radius and polar angle should always be stored as floats.
        # Validate and set r (radius)
        try:
            self.r = float(r)
        except ValueError:
            raise ValueError("R must be convertible to float.")
        # The polar radius should be a non-negative value
        if self.r < 0:
            raise ValueError("R must be non-negative.")
            
        # Validate and set theta (angle)
        try:
            self.theta = float(theta)
        except ValueError:
            raise ValueError("Theta must be convertible to float")
        # The polar angle should be restricted to the range −𝜋 ≤ 𝜃 ≤ 𝜋
        if self.theta < -pi or self.theta > pi:
            raise ValueError("Theta must be between −𝜋 and 𝜋")
            
        # The name and region should both be strings.
        # Validate and set name and region
        if not isinstance(name, str) or not isinstance(region, str):
            raise TypeError("Name and region must be strings")
            
        # Correct the values
        proper_name = ' '.join(word.capitalize() for word in name.split())
        proper_region = ' '.join(word.capitalize() for word in region.split())
        
        # Issue a suitable warning to the user informing them that a name was updated.
        if proper_name != name:
            warnings.warn(f"Name was capitalized from '{name}' to '{proper_name}'")

            warnings.warn(
            "The name should have each word in them capitalised, "
            "and remaining characters in each word should be lowercase."
        )
            
        if proper_region != region:
            warnings.warn(f"Region was capitalized from '{region}' to '{proper_region}'")

            warnings.warn(
            "The region should have each word in them capitalised, "
            "and remaining characters in each word should be lowercase."
            )
            
        self.name = proper_name
        self.region = proper_region

    @property
    def depot(self):
        """Get the depot status of the location.
        
        Returns
        -------
        bool
            True if the location is a depot, False otherwise.
        """
        return self._depot

    @depot.setter
    def depot(self, value):
        """Set the depot status of the location.
        
        Parameters
        ----------
        value : bool
            True if the location is a depot, False otherwise.
        
        Raises
        ------
        TypeError
            If the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise TypeError("depot must be a boolean value")
        self._depot = value

    @property
    def settlement(self):
        """Get the settlement status of the location.
        
        Returns
        -------
        bool
            True if the location is a settlement, False if it is a depot.
        """
        return not self.depot

    # Displaying Locations
    def __str__(self) -> str:
        """Return a string representation of the Location object.
        
        The string includes the name, type (depot or settlement), region, and polar coordinates.
        """
        location_type = "depot" if self.depot else "settlement"
        theta_over_pi = round(self.theta / pi, 2)
        r = round(self.r, 2)
        return f"{self.name} [{location_type}] in {self.region} @ ({r}m, {theta_over_pi}pi)"
        
    def distance_to(self, other):
        """
        Calculates the distance from this location to 
        another location using polar coordinates.

        Parameters
        ----------
        other : Location
            Another Location object.

        Returns
        -------
        float
            The calculated distance between the two locations.
        
        Raises
        ------
        ValueError
            If the input is not a Location instance.
        """
        if not isinstance(other, Location):
            raise ValueError("Distance_to requires another Location object.")
        return sqrt(self.r**2 + other.r**2 - 2 * self.r * other.r * cos(self.theta - other.theta))
    
    def __eq__(self, other):
        """Compare two Location objects for equality.
        
        Two Locations are considered equal if they have the same name and region.
        
        Parameters
        ----------
        other : Location
            The other Location object to compare against.
        
        Returns
        -------
        bool
            True if the two Locations are equal, False otherwise.
        """
        if not isinstance(other, Location):
            return NotImplemented
        return (self.name, self.region) == (other.name, other.region)

    def __hash__(self) -> str:
        """Create a hash value for the Location object.
        
        The hash value is based on the combination of the name and region.
        """
        return hash(self.name + self.region)
"""
The Country Class: 
We need the ability to group together Locations in order to represent countries.
"""
class Country:
    """
    A class representing a country containing locations (settlements and depots).
    
    The Country class manages a collection of Location objects and provides
    methods for calculating travel times, finding optimal routes, and analyzing
    depot placements.
    """
    # Creating a Country
    def __init__(self, list_of_locations: List[Location]):
        """
        Initialize a Country object with a list of locations.

        Parameters
        ----------
        list_of_locations
            List of Location objects representing places in the country.
            
        Raises
        ------
        ValueError
            If duplicate locations are found in the input list.
        """
        location_set = set(list_of_locations)
        if len(location_set) != len(list_of_locations):
            raise ValueError("Duplicate locations found in the input list")
        
        # Store locations as tuple
        self._all_locations = tuple(list_of_locations)
    
    """
    Helpful Country Properties
    """
    @property
    def settlements(self) -> Tuple[Location, ...]:
        """Return tuple of settlement locations."""
        return tuple(loc for loc in self._all_locations if not loc.depot)
    
    @property
    def n_settlements(self) -> int:
        """Return number of settlements."""
        return len(self.settlements)
    
    @property
    def depots(self) -> Tuple[Location, ...]:
        """Returns a tuple containing those Locations in _all_locations that are depots."""
        return tuple(loc for loc in self._all_locations if loc.depot)
    
    @property
    def n_depots(self) -> int:
        """Return number of depots."""
        return len(self.depots)

    def travel_time(self, start_location, end_location) -> float:
        """
        Calculate travel time between two locations within the country.

        Parameters
        ----------
        start_location : str
            The name of the starting location.
        end_location : str
            The name of the destination location.

        Returns
        -------
        float
            The travel time between the two locations in hours.

        Raises
        ------
        ValueError
            If either the start_location or end_location is not in the country.
        """
        # Check if both locations are in the country
        if start_location not in self._all_locations:
            raise ValueError(f"{start_location} is not in the Country.")
        if end_location not in self._all_locations:
            raise ValueError(f"{end_location} is not in the Country.")
            
        # Compute the physical distance between the two locations
        distance = start_location.distance_to(end_location)

        # Determine whether the locations belong to different regions
        different_regions = 1 if start_location.region != end_location.region else 0

        # Count the number of locations in the destination's region
        locations_in_dest_region = sum(
            1 for loc in self._all_locations if loc.region == end_location.region
        )

        # Call the travel_time function and return the result
        return travel_time(
            distance=distance,
            different_regions=different_regions,
            locations_in_dest_region=locations_in_dest_region,
        )

    def fastest_trip_from(
        self,
        current_location: Location,
        potential_locations: Optional[List[Union[Location, int]]] = None,
    ) -> Tuple[Optional[Location], Optional[float]]:
        """
        Find the closest location by travel time from the current location.

        Parameters
        ----------
        current_location : Location
            The current location from which the travel begins.
        potential_locations : list of Location or list of int, optional
            A list of potential destination locations. Can be a mix of `Location`
            objects and integer indices representing locations in `self.settlements`.
            If `None`, all settlements in the country are considered.

        Returns
        -------
        tuple
            A tuple `(closest_location, travel_time)` where:
            - `closest_location` is the Location object for the closest destination.
            - `travel_time` is the time to travel to that destination in hours.
            Returns `(None, None)` if no valid destination is found.

        Raises
        ------
        IndexError
            If an integer index in `potential_locations` is out of bounds.
        ValueError
            If a travel time cannot be calculated due to invalid locations.

        Notes
        -----
        - The method removes the `current_location` from the set of destinations,
        if present.
        - If there are ties in travel time, destinations are sorted by name and
        then by region to ensure a consistent result.
        """
        # Handle default case
        if potential_locations is None:
            potential_locations = list(self.settlements)
        
        # Process input locations/indices
        locations_to_check = set()
        for loc in potential_locations:
            if isinstance(loc, int):
                if loc < 0 or loc >= len(self.settlements):
                    raise IndexError("Settlement index out of bounds")
                locations_to_check.add(self.settlements[loc])
            else:
                locations_to_check.add(loc)
                
        # Remove current location if it's in the potential locations
        locations_to_check.discard(current_location)
        
        if not locations_to_check:
            return None, None
            
        # Calculate travel times and find minimum
        travel_times = []
        for loc in locations_to_check:
            try:
                time = self.travel_time(current_location, loc)
                travel_times.append((loc, time))
            except ValueError:
                continue
                
        if not travel_times:
            return None, None
            
        # Sort by time, then name, then region to handle ties
        sorted_trips = sorted(
            travel_times,
            key = lambda x: (x[1], x[0].name, x[0].region)
        )
        
        return sorted_trips[0]

    def nn_tour(self, starting_depot: Location) -> Tuple[List[Location], float]:
        """
        Implement the nearest neighbor algorithm to find a tour starting and ending at a depot.

        Parameters
        ----------
        starting_depot : Location
            The depot location where the tour starts and ends.

        Returns
        -------
        tuple
            A tuple `(tour, total_time)` where:
            - `tour` is a list of Location objects representing the order of the tour.
            - `total_time` is the total travel time to complete the tour.

        Raises
        ------
        ValueError
            If `starting_depot` is not a valid depot in the country.

        Notes
        -----
        - If there are no settlements, the method returns a tour containing only the depot 
        and a total time of 0.0.
        - The algorithm visits the nearest unvisited settlement at each step and finally
        returns to the starting depot.
        - Settlements are visited in the order determined by the nearest neighbor heuristic.
        """
        if starting_depot not in self.depots:
            raise ValueError("Starting location must be a depot in the country")
            
        # Handle empty settlement case
        if self.n_settlements == 0:
            return [starting_depot, starting_depot], 0.0
            
        # Initialize tour with starting depot
        tour = [starting_depot]
        unvisited = set(self.settlements)
        total_time = 0.0
        current = starting_depot
        
        # Visit each settlement using nearest neighbor
        while unvisited:
            next_loc, time = self.fastest_trip_from(current, list(unvisited))
            tour.append(next_loc)
            total_time += time
            unvisited.remove(next_loc)
            current = next_loc
            
        # Return to starting depot
        final_time = self.travel_time(current, starting_depot)
        total_time += final_time
        tour.append(starting_depot)
        
        return tour, total_time

    def best_depot_site(self, display: bool = True) -> Location:
        """
        Find the depot that provides the shortest tour using the nearest neighbor algorithm.

        Parameters
        ----------
        display : bool, optional
            Whether to display the results of the best depot and its tour (default is True).

        Returns
        -------
        Location
            The depot location that provides the shortest tour.

        Raises
        ------
        ValueError
            If there are no depots in the country.

        Notes
        -----
        - This method evaluates the nearest neighbor tour starting from each depot.
        - Depots are considered in a sorted order based on their names and regions to ensure consistency.
        - If multiple depots result in the same tour time, the one appearing first in the sorted order is selected.
        - If `display` is True, the method prints the best depot, the tour, and the total travel time.
        """
        if not self.depots:
            raise ValueError("No depots in the country")
            
        # Calculate tour time for each depot
        best_time = float('inf')
        best_depot = None
        best_tour = None
        
        for depot in sorted(self.depots, key=lambda x: (x.name, x.region)):
            tour, time = self.nn_tour(depot)
            if time < best_time:
                best_time = time
                best_depot = depot
                best_tour = tour
                
        if display and best_depot and best_tour:
            print(f"Best depot: {best_depot}")
            print("NNA tour is:")
            for loc in best_tour:
                print(f"\t{loc}")
            print(f"Which will take {best_time:.2f} h to complete.")
            
        return best_depot

    def plot_country(
        self,
        distinguish_regions: bool = True,
        distinguish_depots: bool = True,
        location_names: bool = True,
        polar_projection: bool = True,
        save_to: Optional[Path | str] = None,
    ) -> Figure:
        """

        Plots the locations that make up the Country instance on a
        scale diagram, either displaying or saving the figure that is
        generated.

        Use the optional arguments to change the way the plot displays
        the information.

        Attention
        ---------
        You are NOT required to write tests or documentation for this
        function; and you are free to remove it from your final
        submission if you wish.

        You should remove this function from your submission if you
        choose to delete the plotting_utilities.py file.

        Parameters
        ----------
        distinguish_regions : bool, default: True
            If True, locations in different regions will use different
            marker colours.
        distinguish_depots bool, default: True
            If True, depot locations will be marked with crosses
            rather than circles.  Their labels will also be in
            CAPITALS, and underneath their markers, if not toggled
            off.
        location_names : bool, default: True
            If True, all locations will be annotated with their names.
        polar_projection : bool, default: True
            If True, the plot will display as a polar
            projection. Disable this if you would prefer the plot to
            be displayed in Cartesian (x,y) space.
        save_to : Path, str
            Providing a file name or path will result in the diagram
            being saved to that location. NOTE: This will suppress the
            display of the figure via matplotlib.
        """
        return plot_country(
            self,
            distinguish_regions=distinguish_regions,
            distinguish_depots=distinguish_depots,
            location_names=location_names,
            polar_projection=polar_projection,
            save_to=save_to,
        )

    def plot_path(
        self,
        path: List[Location],
        distinguish_regions: bool = True,
        distinguish_depots: bool = True,
        location_names: bool = True,
        polar_projection: bool = True,
        save_to: Optional[Path | str] = None,
    ) -> Figure:
        """
        Plots the path provided on top of a diagram of the country,
        in order to visualise the path.

        Use the optional arguments to change the way the plot displays
        the information. Refer to the plot_country method for an
        explanation of the optional arguments.

        Attention
        ---------
        You are NOT required to write tests or documentation for this
        function; and you are free to remove it from your final
        submission if you wish.

        You should remove this function from your submission if you
        choose to delete the plotting_utilities.py file.

        Parameters
        ----------
        path : list
            A list of Locations in the country, where consecutive
            pairs are taken to mean journeys from the earlier location to
            the following one.
        distinguish_regions : bool, default: True,
        distinguish_depots : bool, default: True,
        location_names : bool, default: True,
        polar_projection : bool, default: True,
        save_to : Path, str

        See Also
        --------
        self.plot_path for a detailed description of the parameters
        """
        return plot_path(
            self,
            path,
            distinguish_regions=distinguish_regions,
            distinguish_depots=distinguish_depots,
            location_names=location_names,
            polar_projection=polar_projection,
            save_to=save_to,
        )
