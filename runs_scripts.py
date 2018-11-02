import sumoTools.simulationHelpers as SH
import sumoTools.bruteForceHelpers as BF
import sumoTools.simulationConstants as Const
import os


def run_trip_analysis(file_name, period):
    # Run simple simulation
    SH.script_run_simulations(file_name=file_name, period=period, execute_simulations=True)

    # Run plot insertion rate
    SH.script_plot_trip_insertion_rate(file_name=file_name, period=period,
                                       file_number=0, offset=10)


def run_brute_force(file_name, period):
    # SH.generate_random_route_files(file_name=file_name, period=period)
    # SH.create_and_set_cfg_file(file_name=file_name, period=period)
    # SH.run_simulations(file_name=file_name, period=period)
    # BF.script_run_brute_force(file_name=file_name, period=period)
    BF.plot_two_graphs(
        input_file_path_1=os.path.join(Const.WORKING_DIRECTORY, file_name, 'out', file_name + '-' + str(period) + '-0.out.xml'),
        input_file_path_2=os.path.join(Const.WORKING_DIRECTORY, file_name, 'out-tl', file_name + '-' + str(period) + '-28.out.xml'),
        output_file=os.path.join(Const.WORKING_DIRECTORY, file_name, 'plot-tl', file_name + '-compare-' + str(period) + '.png'),
        title='cross (period=' + str(period) + ')',
        line_1_legend='Semáforo default',
        line_2_legend='Semáforo otimizado'
    )


if __name__ == '__main__':
    run_brute_force(file_name='cross_test', period=2.0)
