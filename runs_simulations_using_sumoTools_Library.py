import sumoTools.sumoHelpers as SH

if __name__ == '__main__':
    for file in ['cross']:
        for period in [1.5]:
            SH.script_run_simulations(file_name=file, period=period)
            SH.script_plot_trip_insertion_rate(file_name=file, period=period,
                                               file_number=0, offset=10)
