def numericGrade(value, lowerLimit, lowerSupportLimit):
    if value < lowerLimit:
        return 0.0


    if (value >= lowerLimit) and (value <= lowerSupportLimit):
        return (value - lowerLimit)/(lowerSupportLimit - lowerLimit)


    return 1.0


def reverseGrade(value, upperlimit, upperSupportLimit):
    if value > upperlimit:
        return 0.0


    if (value >= upperSupportLimit) and (value <= upperlimit):
        return (upperlimit - value)/(upperlimit - upperSupportLimit)


    return 1.0



def triangleGrade(value, lowerLimit, middle, upper):
    if value <= lowerLimit:
        return 0.0


    if (lowerLimit<value) and  (value <= middle):
        return (value - lowerLimit)/(middle - lowerLimit)


    if (middle < value) and (value < upper):
        return (upper - value)/(upper - middle)


    if value >= upper:
        return 0.0

    return 1.0


def grade(value, low, high, fuzzyVariable):
    med = (high - low) / 2.0

    fuzzyVariable.value = value
    fuzzyVariable.low = reverseGrade(value, med, low)
    fuzzyVariable.med = triangleGrade(value, low, med, high)
    fuzzyVariable.high = numericGrade(value, med, high)


class FuzzyVariable:
    def __init__(self, name, value, low, med, high):
        self.name = name
        self.value = value
        self.low = low
        self.med = med
        self.high = high

    def get_value(self):
        return FuzzyValue(self.value)

    def get_low(self):
        return FuzzyValue(self.low)


    def get_med(self):
        return FuzzyValue(self.med)

    def get_high(self):
        return FuzzyValue(self.high)



    def defuzzify(self, lowWeight, medWeight, highWeight):

        appliedTotal = (lowWeight * self.low) + (medWeight * med) + (highWeight * self.high)

        valueTotal = self.low + med + self.high

        return appliedTotal / valueTotal

class FuzzyValue:
    def __init__(self, value):
        self.value = value


    def fuzzyAnd(self, other):
        return FuzzyValue(self.value * other.value)


    def fuzzyOr(self, other):
        return FuzzyValue((self.value + other.value) - (self.value - other.value))


    def fuzzyNot(self):
        return FuzzyValue(1.0 - self.value)

if __name__ == "__main__":

        fuzzy = FuzzyVariable("", 0.0, 0.0, 0.0, 0.0)

        print("'Value', 'Low', 'Med', 'High'")

        for i in range(0, 100):
            grade(i, 0.0, 100.0, fuzzy)

            print("{0}, {1}, {2}, {3}".format(i, fuzzy.get_low().value, fuzzy.get_med().value, fuzzy.get_high().value))

