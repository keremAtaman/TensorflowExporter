class Normalizer:
    mean = 0.0
    stdev = 0.0
    def __init__(self, mean:float, stdev:float):
        self.mean = mean
        self.stdev= stdev

    def normalize(self, x):
        return (1.0*x - self.mean) / self.stdev

    def unnormalize(self,x):
        return 1.0*x*self.stdev + self.mean
