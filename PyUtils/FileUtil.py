__author__ = "blu3crab"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"

# Create a CSV file
import tempfile
_, filename = tempfile.mkstemp()

with open(filename, 'w') as f:
    f.write("""Line 1
Line 2
Line 3
  """)
