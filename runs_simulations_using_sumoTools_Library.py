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
    pass
    # SH.generate_random_route_files(file_name=file_name, period=period)
    # BF.script_run_brute_force(file_name=file_name, period=period)

    # BF.plot_two_graphs(
    #     input_file_path_1=os.path.join(Const.WORKING_DIRECTORY, 'simple_T_test/out/simple_T_test-1.5-0.out.xml'),
    #     input_file_path_2=os.path.join(Const.WORKING_DIRECTORY, 'simple_T_test/out-tl/simple_T_test-1.5-61.out.xml'),
    #     output_file=os.path.join(Const.WORKING_DIRECTORY, 'simple_T_test/plot-tl/simple_T-compare-1.5.png'),
    #     title='simple_T (period=1.5)',
    #     line_1_legend='Semáforo default',
    #     line_2_legend='Semáforo otimizado'
    # )


def simulate(file_name, period):
    SH.script_run_simulations(file_name=file_name, period=period, execute_simulations=True)


if __name__ == '__main__':
    # for file in ['simple_T_test']:
    #     for period in [1.0]:
    #         run_brute_force(file_name=file, period=period)
