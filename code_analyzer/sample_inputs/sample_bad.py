import os
class myclass:
    def DoSomething(self,X):
        y=X+1
        if y>0:
            if y>10:
                if y>20:
                    if y>30:
                        print("deep")
        return y
    def process_data(self, data_list):
        result = []
        for item in data_list:
            if item % 2 == 0:
                if item > 10:
                    if item < 100:
                        result.append(item * 2)
                    else:
                        result.append(item)
                else:
                    result.append(0)
            else:
                result.append(-1)
        return result

def add(a,b): return a+b

x = 1; y = 2; z = x+y
# fix this
def calculate_something_with_a_really_long_name_that_definitely_exceeds_the_line_length_limit(a, b, c):
    return a + b + c
