# Application A: Sliding Window Analytics (Real-time Aggregation

from collections import deque

class MovingAverageCalculator:
    def __init__(self,window_size:int):
        self.window=deque(maxlen=window_size)
    def process_request(self,value):
        self.window.append(value)
        calculate_average=sum(self.window)/len(self.window)
        return calculate_average


temp_stream=[22.5, 23.0, 23.5, 24.0, 25.0, 26.5]
calc=MovingAverageCalculator(window_size=3)


for temp in temp_stream:
    print(f"New temp: {temp} | 3-Tick Moving Avg: {calc.process_request(temp):.2f}")