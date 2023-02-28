def scaling_func(api_in):
    api_in = api_in["features"]
    for key, value in api_in.items():
        if key == 'Project Description':
            value[0] = (value[0]-1)/(160-1)
        elif key == 'Country':
            value[0] = (value[0]+1)/(2)
        elif key == 'Project_life':
            value[0] = (value[0]-10110001)/(10433817-10110001)
        elif key == 'Region':
            value[0] = (value[0])/(166)
        elif key == 'LONG_FCST':
            value[0] = (value[0])/(404.11)
        elif key == 'Start_Year':
            value[0] = (value[0])/(12.29)
        elif key == 'MARGIN':
            value[0] = (value[0]+190.28)/(329.53+190.28)
        elif key == 'PROD_ID':
            value[0] = (value[0]-10001)/(33817-10001)
        elif key == 'LOC_ID':
            value[0] = (value[0]-101)/(104-101)
        elif key == 'TIER':
            value[0] = (value[0]-1)    
        elif key == 'CAPACITY':
            value[0] = (value[0]-193.21)/(9999-193.21)
        elif key == 'SIZE':
            value[0] = (value[0])/(0.9)
        elif key == 'COST':
            value[0] = (value[0])/(1994.29)
        elif key == 'PRICE':
            value[0] = (value[0]-0.82)/(2799-0.82)
    return api_in

