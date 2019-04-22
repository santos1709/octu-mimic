import time, os
from subprocess import call

n = 1
max_load_per_second = 30
seconds = 0
# name = "api-service-{}"
# volumes = "../mindtitan_sampletask:/usr/src/app"
# ports = "500{}:8080"


def upscale():
    n = n + 1
    max_load_per_second = n*max_load_per_second
    call(['../auto-scale.sh {}'.format(n)])


while True:
    time.sleep(1)
    seconds = 1
    count_call = int(os.environ['COUNTCALL'])

    if count_call/seconds == (max_load_per_second/n):
        upscale()
