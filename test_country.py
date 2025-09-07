from pathlib import Path
import pytest
from country import travel_time, Location, Country
from math import pi, sqrt

"""
Tests for the travel_time function
"""

# Constants for test setup
locations_csv_file = Path("./data/locations.csv").resolve()
default_speed = 4.75
# Travelling this distance without any penalties at the default speed should take 1 hour.
one_hour_distance = 3_600 * default_speed


@pytest.fixture
def setup_test_locations():
    """Fixture for creating test Location instances."""
    return [
        Location("Riverwood", "Whiterun Hold", 49_877.15654485528, -1.1153081421843865, False),
        Location("Heartwood Mill", "The Rift", 164_031.25924652288, -0.6236682227787959, True),
    ]


@pytest.fixture
def setup_test_country(setup_test_locations):
    """Fixture for creating a test Country instance."""
    return Country(setup_test_locations)


class TestTravelTime:
    @pytest.mark.parametrize(
        "distance,different_regions,locations_in_dest_region,speed,expected",
        [
            (one_hour_distance, 0., 3., default_speed, 1.0),
            (one_hour_distance, 0., 0., default_speed / 2, 2.0),
            (one_hour_distance, 1, 20, default_speed, 3.0),
            (0, 0, 3, default_speed, 0.0),
            (1000, 1, 0, default_speed, (1000 / (3600 * default_speed)) * (1 + 1 / 10)),
        ],
    )
    def test_valid_cases(self, distance, different_regions, locations_in_dest_region, speed, expected):
        result = travel_time(distance, different_regions, locations_in_dest_region, speed)
        assert abs(result - expected) < 1e-10

    @pytest.mark.parametrize(
        "distance,different_regions,locations_in_dest_region,speed",
        [
            (-100, 0, 3, default_speed),  # Negative distance
            (1000, -1, 3, default_speed),  # Negative regions
            (1000, 1.5, 3, default_speed),  # Invalid regions
        ],
    )
    def test_invalid_inputs(self, distance, different_regions, locations_in_dest_region, speed):
        with pytest.raises(ValueError):
            travel_time(distance, different_regions, locations_in_dest_region, speed)

    def test_large_distance(self):
        distance = 1e6
        different_regions = 0
        locations_in_dest_region = 3
        speed = default_speed
        expected = 1e6 / (3600 * default_speed)
        result = travel_time(distance, different_regions, locations_in_dest_region, speed)
        assert abs(result - expected) < 1e-10

    def test_custom_speed_twice_default(self):
        distance = 1000
        different_regions = 0
        locations_in_dest_region = 3
        speed = default_speed * 2
        expected = 1000 / (3600 * speed)
        result = travel_time(distance, different_regions, locations_in_dest_region, speed)
        assert abs(result - expected) < 1e-10

    def test_maximum_penalty_with_many_locations(self):
        distance = 1000
        different_regions = 1
        locations_in_dest_region = 100
        speed = default_speed
        expected = (1000 / (3600 * default_speed)) * (1 + 100 / 10)
        result = travel_time(distance, different_regions, locations_in_dest_region, speed)
        assert abs(result - expected) < 1e-10


class TestLocation:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures for Location tests."""
        self.riverwood = Location(
            name="Riverwood",
            region="Whiterun Hold",
            r=49_877.15654485528,
            theta=-1.1153081421843865,
            depot=False
        )
        self.heartwood_mill = Location(
            name="Heartwood Mill",
            region="The Rift",
            r=164_031.25924652288,
            theta=-0.6236682227787959,
            depot=True
        )

    @pytest.mark.parametrize(
        "name, region, r, theta, depot, expected_name, expected_region, expected_r, expected_theta, expected_depot",
        [
            ("Test Place", "Test Region", 100.0, 0.0, False, "Test Place", "Test Region", 100.0, 0.0, False),
        ],
    )
    def test_valid_initialization(self, name, region, r, theta, depot, expected_name, expected_region, expected_r, expected_theta, expected_depot):
        """Test valid initialization of Location object."""
        loc = Location(name, region, r, theta, depot)
        assert loc.name == expected_name, "Name mismatch."
        assert loc.region == expected_region, "Region mismatch."
        assert loc.r == expected_r, "Radius mismatch."
        assert loc.theta == expected_theta, "Theta mismatch."
        assert loc.depot == expected_depot, "Depot flag mismatch."

    @pytest.mark.parametrize(
        "name, region, expected_name, expected_region",
        [
            ("test place", "test region", "Test Place", "Test Region"),
        ],
    )
    def test_name_and_region_capitalization(self, name, region, expected_name, expected_region):
        """Test capitalization of name and region."""
        with pytest.warns(UserWarning, match="Name was capitalized from"):
            loc = Location(name, region, 100.0, 0.0, False)
        assert loc.name == expected_name, "Name capitalization failed."
        assert loc.region == expected_region, "Region capitalization failed."

    @pytest.mark.parametrize(
        "name, region, r, theta, depot, error_type, error_message",
        [
            ("Test", "Region", 100.0, 0.0, 1, TypeError, "Depot must be a boolean value."),
            (123, "Region", 100.0, 0.0, False, TypeError, "Name and region must be strings"),
        ],
    )
    def test_invalid_type_initialization(self, name, region, r, theta, depot, error_type, error_message):
        """Test invalid data types during initialization."""
        with pytest.raises(error_type, match=error_message):
            Location(name, region, r, theta, depot)

    @pytest.mark.parametrize(
        "name, region, r, theta, depot, error_type, error_message",
        [
            ("Test", "Region", -100.0, 0.0, False, ValueError, "R must be non-negative."),
            ("Test", "Region", 100.0, 4 * pi, False, ValueError, "Theta must be between −𝜋 and 𝜋"),
        ],
    )
    def test_invalid_value_initialization(self, name, region, r, theta, depot, error_type, error_message):
        """Test invalid values during initialization."""
        with pytest.raises(error_type, match=error_message):
            Location(name, region, r, theta, depot)

    @pytest.mark.parametrize(
        "loc_a, loc_b, expected_distance",
        [
            # Same location
            ("riverwood", "riverwood", 0.0),
            # 90-degree angle
            (Location("A", "Region", 3.0, 0.0, False), Location("B", "Region", 3.0, pi / 2, False), 3 * sqrt(2)),
            # Same angle, different radius
            (Location("C", "Region", 3.0, 0.0, False), Location("D", "Region", 4.0, 0.0, False), 1.0),
            # Opposite angles
            (Location("E", "Region", 3.0, 0.0, False), Location("F", "Region", 3.0, pi, False), 6.0),
        ],
    )
    def test_distance_to(self, loc_a, loc_b, expected_distance):
        """Test distance calculation between locations."""
        if loc_a == "riverwood":
            loc_a = self.riverwood
        if loc_b == "riverwood":
            loc_b = self.riverwood
        assert loc_a.distance_to(loc_b) == pytest.approx(expected_distance), "Distance calculation failed."

    @pytest.mark.parametrize(
        "loc_a, loc_b, expected_equal",
        [
            (Location("Test", "Region", 100.0, 0.0, False), Location("Test", "Region", 200.0, pi / 2, True), True),
            (Location("Test", "Region", 100.0, 0.0, False), Location("Different", "Region", 100.0, 0.0, False), False),
        ],
    )
    def test_equality_operator(self, loc_a, loc_b, expected_equal):
        """Test equality operator for Location."""
        assert (loc_a == loc_b) == expected_equal, "Equality check failed."

    @pytest.mark.parametrize(
        "loc_a, loc_b, expected_same_hash",
        [
            (Location("Test", "Region", 100.0, 0.0, False), Location("Test", "Region", 200.0, pi / 2, True), True),
            (Location("Test", "Region", 100.0, 0.0, False), Location("Different", "Region", 100.0, 0.0, False), False),
        ],
    )
    def test_hash(self, loc_a, loc_b, expected_same_hash):
        """Test hash consistency for Location."""
        assert (hash(loc_a) == hash(loc_b)) == expected_same_hash, "Hash consistency failed."

class TestCountry:
    @pytest.fixture(scope="module")
    def locations(self):
        """Fixture for a list of Location instances."""
        return [
            Location("Riverwood", "Whiterun Hold", 100, 0.0, False),
            Location("Whiterun", "Whiterun Hold", 200, 0.5, True),
            Location("Helgen", "Falkreath Hold", 150, -0.5, False),
        ]

    @pytest.fixture(scope="module")
    def country(self, locations):
        """Fixture for a Country instance with predefined locations."""
        return Country(locations)

    def test_country_initialization(self, locations):
        """Test Country initialization with valid locations."""
        country = Country(locations)
        assert len(country._all_locations) == len(locations), "Number of locations mismatch."
        assert isinstance(country._all_locations, tuple), "Location storage type mismatch."

    @pytest.mark.parametrize(
        "duplicate_locations, error_message",
        [
            (
                [
                    Location("Riverwood", "Whiterun Hold", 100, 1.0, False),
                    Location("Riverwood", "Whiterun Hold", 100, 1.0, False),  # Duplicate
                ],
                "Duplicate locations found",
            ),
        ],
    )
    def test_country_duplicate_locations(self, duplicate_locations, error_message):
        """Test Country initialization with duplicate locations."""
        with pytest.raises(ValueError, match=error_message):
            Country(duplicate_locations)

    def test_country_properties(self, country):
        """Test properties of Country (depots and settlements)."""
        assert len(country.depots) == 1, "Number of depots mismatch."
        assert country.depots[0].name == "Whiterun", "First depot name mismatch."
        assert len(country.settlements) == 2, "Number of settlements mismatch."
        assert country.settlements[0].name == "Riverwood", "First settlement name mismatch."

    def test_travel_time(self, country, locations):
        """Test travel time between locations."""
        loc1, loc2, _ = locations
        travel_time = country.travel_time(loc1, loc2)
        assert travel_time > 0, "Travel time should be greater than zero."

        loc_outside = Location("Morthal", "Hjaalmarch", 300, -0.2, False)
        with pytest.raises(ValueError, match=r".*is not in the Country\."):
            country.travel_time(loc1, loc_outside)

        # Add boundary cases for travel time
        # Same location
        travel_time_same = country.travel_time(loc1, loc1)
        assert travel_time_same == 0, "Travel time between the same location should be zero."

        # Edge case: Zero distance location
        zero_distance_loc = Location("Zero", "Whiterun Hold", 0, 0, False)
        country_with_zero = Country(locations + [zero_distance_loc])
        travel_time_zero = country_with_zero.travel_time(zero_distance_loc, zero_distance_loc)
        assert travel_time_zero == 0, "Travel time should be zero for zero distance."

    def test_fastest_trip_from(self, country, locations):
        """Test finding the fastest trip from a location to candidates."""
        loc1, loc2, loc3 = locations
        closest_loc, time = country.fastest_trip_from(loc1, [loc2, loc3])
        assert closest_loc == loc3, "Closest location mismatch."
        assert time > 0, "Travel time should be greater than zero."

        # Test with default potential_locations
        closest_loc_default, time_default = country.fastest_trip_from(loc1)
        assert closest_loc_default == loc3, "Default closest location mismatch."
        assert time_default > 0, "Default travel time should be greater than zero."

        # Test with invalid settlement index (should raise IndexError)
        with pytest.raises(IndexError, match="Settlement index out of bounds"):
            country.fastest_trip_from(loc1, [10])

        # Test with mixed valid and invalid locations
        # Adjust the expectation: invalid locations are skipped silently
        closest_loc, time = country.fastest_trip_from(
            loc1, [loc2, Location("Invalid", "Nowhere", 0, 0, False)]
        )
        assert closest_loc == loc2, "Closest location mismatch when skipping invalid locations."
        assert time > 0, "Travel time should be calculated for valid locations only."

        # Test tie-breaking
        tie_loc1 = Location("A", "Whiterun Hold", 150, -0.5, False)
        tie_loc2 = Location("B", "Whiterun Hold", 150, -0.5, False)
        tie_country = Country(locations + [tie_loc1, tie_loc2])
        closest_loc_tie, _ = tie_country.fastest_trip_from(loc1, [tie_loc1, tie_loc2])
        assert closest_loc_tie == tie_loc1, "Tie-breaking failed: Closest location should be resolved alphabetically."

    def test_nn_tour(self, country, locations):
        """Test nearest neighbor tour starting from a depot."""
        loc1, loc2, loc3 = locations  # loc2 is the depot
        tour, total_time = country.nn_tour(loc2)
        assert tour[0] == loc2, "Tour should start at the depot."
        assert tour[-1] == loc2, "Tour should end at the depot."
        assert total_time > 0, "Total tour time should be positive."
        assert len(tour) == len(country.settlements) + 2, "Tour should include all settlements plus the depot twice."

        # Empty case: No settlements
        empty_country = Country([loc2])  # Only the depot
        tour, total_time = empty_country.nn_tour(loc2)
        assert tour == [loc2, loc2], "Tour should only include the depot when there are no settlements."
        assert total_time == 0.0, "Total time should be zero when there are no settlements."

        # Single settlement case
        single_settlement_country = Country([loc2, loc1])
        tour, total_time = single_settlement_country.nn_tour(loc2)
        assert tour == [loc2, loc1, loc2], "Tour should visit the single settlement and return to the depot."
        assert total_time > 0, "Total time should be positive with one settlement."

        # Edge case: Multiple settlements with the same distance
        tie_loc1 = Location("A", "Whiterun Hold", 150, -0.5, False)
        tie_loc2 = Location("B", "Whiterun Hold", 150, -0.5, False)
        tie_country = Country([loc2, tie_loc1, tie_loc2])
        tour, _ = tie_country.nn_tour(loc2)
        assert tour[1] == tie_loc1, "Tie-breaking failed: Settlements should be visited alphabetically."
        assert tour[2] == tie_loc2, "Tie-breaking failed: Settlements should be visited alphabetically."


    def test_best_depot_site(self, country):
        """Test finding the best depot site."""
        best_depot = country.best_depot_site(display=False)
        assert best_depot == country.depots[0], "Incorrect best depot identified."

        # Empty case: No depots
        empty_country = Country(list(country.settlements))  # No depots
        with pytest.raises(ValueError, match="No depots in the country"):
            empty_country.best_depot_site()

        # Single depot
        single_depot_country = Country([country.depots[0]] + list(country.settlements))
        best_depot = single_depot_country.best_depot_site(display=False)
        assert best_depot == country.depots[0], "Single depot should be the best depot."

        # Edge case: Multiple depots with the same tour time
        tie_depot1 = Location("A Depot", "Region1", 100, 0, True)
        tie_depot2 = Location("B Depot", "Region1", 100, 0, True)
        tie_country = Country(list(country.settlements) + [tie_depot1, tie_depot2])
        best_depot = tie_country.best_depot_site(display=False)
        assert best_depot == tie_depot1, "Tie-breaking failed: Best depot should be resolved alphabetically."