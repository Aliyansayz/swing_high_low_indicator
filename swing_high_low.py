class swing_high_low(fisher_transform_inverse_fisher_stochastic):

    def swing_high_low_lookback(self, bar_list, period=9, lookback=10, swing_direction=False):

        symbols, values = 0, 1
        swing_high_low_list = [[]] * len(bar_list[values])
        swing_direction_crossover_list = [[]] * len(bar_list[values])
        for symbol, ohlc in enumerate(bar_list[values]):

            open, high, low, close = ohlc['Open'], ohlc['High'], ohlc['Low'], ohlc['Close']
            # get_pivot_high_low(self, pivot_point, period)
            pivot_highs, pivot_lows = self.pivot_high_low(open, high, low, close, period)

            status = self.swing_pattern( open, high, low, close, pivot_highs, pivot_lows)
            swing_direction_value, swing_status_crossover  = self.get_swing_status_value(status) # -1 , 1

            swing_direction_crossover = [[swing_direction_value[z], swing_status_crossover[z]]  for z in range(len(swing_status_crossover)) ]
            if lookback: status, swing_direction_crossover = status[-lookback:], swing_direction_crossover[-lookback:]
            swing_high_low_list[symbol], swing_direction_crossover_list[symbol] = status, swing_direction_crossover


        # print( len(swing_high_low_list),len(swing_direction_value_list) )
        if swing_direction : return  swing_high_low_list , swing_direction_crossover_list
        else:
             return  swing_high_low_list

    def get_swing_status_value(self, status):

        swing_status_value = [ -1 if 'HH' in status_name or 'LH' in status_name else 1  for status_name in status  ]
        swing_status_value = np.array(swing_status_value)
        
        prev_swing_status = np.roll(swing_status_value, 1)
        swing_status_crossover = np.where((prev_swing_status < 0) & (swing_status_value > 0), 1,
                             np.where((prev_swing_status > 0) & (swing_status_value < 0), -1, 0))
        # print(swing_status_value)
        # print(swing_status_crossover)
        return swing_status_value, swing_status_crossover

    def swing_pattern(self, o, h, l, c, pivot_highs, pivot_lows):

        diff = abs(c-o)
        o1, c1 = np.roll(o,1), np.roll(c,1) #
        min_oc = np.where( o < c , o , c )
        max_oc = np.where( o > c , o , c )
        
        pattern = np.where(
            np.logical_and(np.logical_and(pivot_lows != False, min_oc - l > diff), h - max_oc < diff ), ' Hammer',
             np.where(np.logical_and( np.logical_and(pivot_lows != False, h - max_oc > diff), min_oc - l < diff ), ' Inverted Hammer',
              np.where(np.logical_and( np.logical_and(c > o, c1 < o1), np.logical_and(c > o1, o < c1) ), ' Bullish Engulfing',
               np.where(np.logical_and(pivot_highs != False, min_oc - l > diff), ' Hanging Man',
                np.where(np.logical_and( np.logical_and(pivot_highs != False, h - max_oc > diff), min_oc - l < diff ),
                            ' Shooting Star',
                 np.where(np.logical_and(np.logical_and(c > o, c1 < o1), np.logical_and(c > o1, o < c1) ), ' Bearish Engulfing',
                                ' None' ) ) ) ) ) )

        phy, phy_index = self.first_non_nan(pivot_highs)
        ply, ply_index = self.first_non_nan(pivot_lows)

        # Initialize status list with the first values
        status = [""] * len(pattern)

        # Loop from the next index to the end
        for index, (ph_value, pl_value) in enumerate(zip(pivot_highs, pivot_lows)):
            if ph_value != False : # not np.isnan(ph_value):
                h_value = 'HH' if (ph_value > phy) else 'LH'  # ===== DOWNTREND  xxxx  DOWNTREND
                phy     = ph_value
                status[index] = h_value + str(pattern[index])

            elif pl_value != False : # not np.isnan(pl_value):
                l_value = 'LL' if (pl_value < ply) else 'HL' # ===== UPTREND xxxx  UPTREND
                ply     = pl_value
                status[index] = l_value + str(pattern[index])
            else:
                # if status:
                status[index] =  status[index-1]
        # print(status)
        return status


    def pivot_high_low(self, open, high, low, close, period):
        # Iterate through data and identify patterns based on conditions
        min_low   = self.moving_min(low,  period)
        max_high  = self.moving_max(high, period)

        # Calculate pivot point (average of high, low, and close)
        pivot_point = (max_high + min_low + close) / 3

        pivot_highs, pivot_lows = self.get_pivot_high_low(high, low, pivot_point, period)
        return  pivot_highs, pivot_lows

    def first_non_nan(self, arr):
        for idx, val in enumerate(arr):
            if val != False :
                return val, idx
        return np.nan, np.nan

    def moving_min(self, array, period):
      
        moving_min = np.empty_like(array)
        moving_min = np.full(moving_min.shape, np.nan)
        for i in range(period, len(array)):
            moving_min[i] = np.min(array[i - period:i])

        # to be changed
        moving_min[np.isnan(moving_min)] = np.nanmean(moving_min)
        return moving_min

    def moving_max(self, array, period):
      
        moving_max = np.empty_like(array)
        moving_max = np.full(moving_max.shape, np.nan)
        # moving_max[:period] = np.max(array[:period])
        for i in range(period, len(array)):
            moving_max[i] = np.max(array[i - period:i])
        # to be changed
        moving_max[np.isnan(moving_max)] = np.nanmean(moving_max)
        return moving_max
  
    def get_pivot_high_low(self, high, low, pivot_point, period ):
        pass
        # previous_low , previous_high
        # current_low  , current_high
        pivot_low, pivot_high = [False]* len(pivot_point), [False]* len(pivot_point)


        for i in range(period, len(high) ):

            # current_high  = np.max(pivot_point[i:period+i]) === 3--> 4 - 3 + 1 = 2 : 5
            current_low  = np.min(pivot_point[i- period + 1 :i+1]) # current_low  < pivot_low[pivot_index-1]  or # or current_low  > pivot_low[pivot_index-1]
            current_high = np.max(pivot_point[i- period + 1 :i+1]) # current_high > pivot_high[pivot_index-1] or  # or current_high < pivot_high[pivot_index-1]

            period_lowest_low   = np.min(low[i-period :i-1])
            period_highest_high = np.max(high[i -period:i-1])

            current_low  = low[i]
            current_high = high[i]

            pivot_low[i]  = current_low  if current_low  > period_lowest_low   else False #np.nan 
            pivot_high[i] = current_high if current_high > period_highest_high else False #np.nan 

        return pivot_high, pivot_low

