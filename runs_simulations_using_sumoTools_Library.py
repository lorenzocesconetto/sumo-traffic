import sumoTools.sumoHelpers as SH

if __name__ == '__main__':
    for file in ['simple_T']:
        for period in [1.4]:
            SH.script_run_complete(file_name=file, period=period)
