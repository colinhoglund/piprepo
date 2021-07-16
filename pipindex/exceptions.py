class InvalidFileName(ValueError):
    def __init__(self, filename):
        self.message = 'Invalid file name: {}'.format(filename)
        super(ValueError, self).__init__(self.message)
