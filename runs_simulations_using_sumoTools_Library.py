import sumoTools.sumoHelpers as SH

if __name__ == '__main__':
    for file in ['manhattan', 'cross', 'principal', 'simple_T', 'spider']:
        for period in [1, 1.5, 2]:
            SH.script_run_complete(file_name=file, period=period)
