import sumoTools.sumoHelpers as SH
import sys
import argparse

sys.argv = ["complete.py",
            "new_manhattan",
            "1.0",
            "10",
            "summary-output",
            "time",
            "meanWaitingTime",
            "-1",
            "0",
            "True",
            "False",
            "test"]

options_dict = {"time": "Time (s)",
                "loaded": "Total number of cars loaded (#)",
                "inserted": "Total number of cars inserted in the map (#)",
                "running": "Number of cars currently in the map (#)",
                "waiting": "Number of cars currently waiting at intersections (#)",
                "ended": "Total number of cars that left the map (#)",
                "meanWaitingTime": "Mean Waiting Time (s)",
                "meanTravelTime": "Mean Travel Time (s)",
                "duration": "Duration (?)",
                "depart": "Actual Period (s/veh)"}


def magic(args):

    # Checks directory and network exists; Checks number and period are valid
    SH.checks_random_cfg(file_name=args["file_name"], period=args["period"],
                         number=args["number"], output_type=args["output_type"])

    # Creates Dirs
    SH.create_dirs(args["file_name"], "cfg", "out", "plot", text=args["text"])

    # Generates rou.xml files
    SH.gen_random_trips(file_name=args["file_name"], period=args["period"], number=args["number"])

    # Creates sumo.cfg files
    SH.create_cfg(file_name=args["file_name"], period=args["period"], number=args["number"],
                  output_type=args["output_type"], base_cfg='base.sumo.cfg', text=args["text"])

    # Run simulation
    SH.run_simulation(file_name=args["file_name"], period=args["period"], number=args["number"], text=args["text"])

    # Get y data
    data = SH.get_data(file_name=args["file_name"], opt=args["y_opt"], period=args["period"],
                       number=args["number"], sorted_output=args["sorted_output"], integer_output=True, text=args["text"])
    size = SH.get_num_points(data)
    y = SH.get_avg(data, size)

    # Get x data
    all_x = SH.get_data_single(file_name=args["file_name"], opt=args["x_opt"], period=args["period"],
                               sorted_output=args["sorted_output"],
                               integer_output=True, text=args["text"], file_number=0)
    x = all_x[:size]

    # Get max and min vectors
    max_vector, min_vector = SH.get_max_min(data)

    # Check before plotting
    SH.check_plot(file_name=args["file_name"], x_opt=args["x_opt"], y_opt=args["y_opt"], options_dict=options_dict)

    # Plot data
    SH.plot_data(x=x, y=y, x_opt=args["x_opt"], y_opt=args["y_opt"], file_name=args["file_name"],
                 period=args["period"], file_number=args["file_number"], offset=0, text=args["text"],
                 fill_max_min=args["fill_max_min"], max_vector=max_vector, min_vector=min_vector)


def test(args):
    # Get y data
    data = SH.get_data(file_name=args["file_name"], opt=args["y_opt"], period=args["period"],
                       number=args["number"], sorted_output=args["sorted_output"], integer_output=True,
                       text="")
    size = SH.get_num_points(data)
    y = SH.get_avg(data, size)

    # Get x data
    all_x = SH.get_data_single(file_name=args["file_name"], opt=args["x_opt"], period=args["period"],
                               sorted_output=args["sorted_output"],
                               integer_output=True, text="", file_number=0)
    x = all_x[:size]

    # Get max and min vectors
    max_vector, min_vector = SH.get_max_min(data)

    # Plot data
    SH.plot_data(x=x, y=y, x_opt=args["x_opt"], y_opt=args["y_opt"], file_name=args["file_name"],
                 period=args["period"], file_number=args["file_number"], offset=0, text=args["text"],
                 fill_max_min=args["fill_max_min"], max_vector=max_vector, min_vector=min_vector)



if __name__ == '__main__':
    # Create and setup argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", type=str, help="file name")
    parser.add_argument("period", type=float, default=1, help="period float")
    parser.add_argument("number", type=int, default=10, help="number of files")
    parser.add_argument("output_type", type=str, default="summary-output", help="putput type")
    parser.add_argument("x_opt", type=str, default="time", help="X axis variable")
    parser.add_argument("y_opt", type=str, default="summary-output", help="Y axis variable")
    parser.add_argument("file_number", type=int, default=-1, help="Number of file plotted")
    parser.add_argument("offset", type=int, default=0, help="number of points to make avg")
    parser.add_argument("fill_max_min", type=bool, default=True, help="Fill max min range")
    parser.add_argument("sorted_output", type=bool, default=False, help="Sorted output from get_data")
    parser.add_argument("text", type=str, default="", help="extra text for specification")
    args = vars(parser.parse_args())

    test(args)













