import os
import zarr
import zarrs
import numpy as np

zarr.config.set({"codec_pipeline.path": "zarrs.ZarrsCodecPipeline"})

for i in range(10):
    print(i, 'for loop')
    
'''
import os
import sys
import subprocess

from time import sleep

script = '/home/malcom3d/Documents/blender/loop.py'
output=subprocess.Popen([sys.executable, script], env={'PYTHONPATH': os.pathsep.join(sys.path)}, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
std_output = output.stdout
err_output = output.stderr
output.poll()

sleep(1)
std_output = output.stdout
for line in output.stdout:
    print(line.decode().strip(), flush=True)

output.communicate()
'''