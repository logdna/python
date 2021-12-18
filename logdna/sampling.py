import random

class Sampling:
    """
    Sampling class boilerplate that returns True no matter what.

    send_check is required.  It is the "decision interface".
    """

    def __init__(self): pass

    def send_check(self):
        """
        Decide if a log should be sent using a random selection over some distribution.
        """
        return True


class UniformSampling(Sampling):
    """
    Uniform distribution
    """

    def __init__(self, send_ratio=1.0):
        """
        send_ratio: percentage of logs to let through.  Defaults to always send
        """
        if send_ratio > 1.0 or send_ratio < 0.0:
            send_ratio = 1.0 # set to 1.0 if out of bounds: [0,1]
        self.send_ratio = send_ratio

    def send_check(self):
        """
        Binary send decision based on a uniform distribution.
        """
        # Send if random number is less than send_ratio
        return True if random.uniform(0.0,1.0) < self.send_ratio else False
