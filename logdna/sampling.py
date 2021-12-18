import random

_DEV = False

class Sampling:
    """
    Sampling class boilerplate

    send_check is required
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

    def __init__(self, send_drop_ratio=1.0):
        """
        send_drop_ratio: percentage of logs to let through.  Defaults to always send
        """
        if send_drop_ratio > 1.0 or send_drop_ratio < 0.0:
            send_drop_ratio = 1.0 # set to 1.0 if out of bounds: [0,1]
        self.send_drop_ratio = send_drop_ratio

    def send_check(self):
        """
        Binary send decision based on a uniform distribution.
        """
        # Send if random number is less than send_drop_ratio
        return True if random.uniform(0.0,1.0) < self.send_drop_ratio else False
