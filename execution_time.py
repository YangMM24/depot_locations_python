import numpy as np
import timeit
import matplotlib.pyplot as plt
from utilities import regular_n_gon

def measure_execution_time(n_locs_values):
    """
    Measure the execution time of the Nearest Neighbor Algorithm (NNA) for various numbers of locations.

    Args:
        n_locs_values: numpy.ndarray
            Array of location counts to test.

    Returns:
        list: 
            A list of execution times corresponding to each value in n_locs_values.
    """
    execution_times = []

    for n_locs in n_locs_values:
        # Use regular_n_gon to generate a Country object directly
        test_country = regular_n_gon(n_locs)

        # Select the first depot as the starting point for the NNA
        starting_depot = test_country.depots[0]

        # Measure the execution time of the nn_tour method
        time_taken = timeit.timeit(lambda: test_country.nn_tour(starting_depot), number=1)
        execution_times.append(time_taken)

        # Print progress for debugging purposes
        print(f"Number of Locations: {n_locs}, Execution Time: {time_taken:.6f} seconds")

    return execution_times

def plot_execution_times(n_locs_values, execution_times, output_path="report/nna_execution_times.png"):
    """
    Plot the execution times of the NNA against the number of locations and save the plot.

    Args:
        n_locs_values: numpy.ndarray
            Array of location counts tested.
        execution_times: list
            Execution times corresponding to n_locs_values.
        output_path: string 
            File path to save the resulting plot.
    """
    # Create a line plot with markers
    plt.figure()
    plt.plot(n_locs_values, execution_times, marker='o', linestyle='-', label='Execution Time')

    # Customize the plot appearance
    plt.xlabel('Number of Locations (N_locs)', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.title('Execution Time of NNA vs Number of Locations', fontsize=14)
    plt.grid(True)
    plt.legend()
    plt.xscale('log')  # Use logarithmic scale for better visualization
    plt.yscale('log')  # Logarithmic scale for execution times if values span multiple magnitudes

    # Save the plot to the specified file path
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")
    plt.show()


def main():
    """
    Main function to orchestrate the measurement and plotting of NNA execution times.
    """
    # Generate logarithmically spaced values for the number of locations
    n_locs_values = np.unique(np.logspace(0, 9, base=2, num=75, dtype=int))

    # Measure execution times for the given location counts
    execution_times = measure_execution_time(n_locs_values)

    # Plot and save the execution times
    plot_execution_times(n_locs_values, execution_times)


if __name__ == "__main__":
    main()