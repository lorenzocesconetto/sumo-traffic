import sumoTools.simulationHelpers as SH
import sumoTools.bruteForceHelpers as BF
import sumoTools.Constants as Const
import os


def run_trip_analysis(file_name, period):
    # Run simple simulation
    SH.script_run_simulations(file_name=file_name, period=period, execute_simulations=True)

    # Run plot insertion rate
    SH.script_plot_trip_insertion_rate(file_name=file_name, period=period,
                                       file_number=0, offset=10)


def plot_comparison(file_name: str, period: float):
    BF.plot_two_graphs(
        input_file_path_1=os.path.join(Const.WORKING_DIRECTORY, file_name, 'out', file_name + '-' + str(period) + '-0.out.xml'),
        input_file_path_2=os.path.join(Const.WORKING_DIRECTORY, file_name, 'out-tl', file_name + '-' + str(period) + '-0.out.xml'),
        output_file=os.path.join(Const.WORKING_DIRECTORY, file_name, 'plot-tl', file_name + '-compare-' + str(period) + '.png'),
        title=file_name.replace('_test', '') + ' (period=' + str(period) + ')',
        line_1_legend='Semáforo default',
        line_2_legend='Semáforo otimizado'
    )


if __name__ == '__main__':
    print(len(BF.generate_possibilities()))
    # for file in ['cross_test']:
    #     for p in [1.1]:
            # Generate route files
            # SH.generate_random_route_files(file_name=file, period=p)

            # Create CFG
            # SH.create_and_set_cfg_file(file_name=file, period=p)

            # Run simulations
            # SH.run_simulations(file_name=file, period=p)

            # Optimize traffic light
            # BF.pick_the_best_tl_program(file_name=file, period=p)

            # Plot P critical
            # BF.script_run_plot(file_name=file, period=p)

            # Plot Compare
            # plot_comparison(file_name=file, period=p)
