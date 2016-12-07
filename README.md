# swarm-python
Provides command line to manager swarm nodes, using the Python client (>=Python3.4 is recommended)


##### HOW TO USE

* Install depedency via pip

        $ pip install -r requirements.txt

* Move the folder into /usr/local/

* Add the following line into ~/.bash_profile and save

        PYTHONPATH=/usr/local/swarm-python/lib
        PATH=/usr/local/swarm-python/bin:$PATH
        export PYTHONPATH
        export PATH

* Issue the following command, ensure the environment variable take effect

        $ source ~/.bash_profile
        $ echo $PYTHONPATH

* `swarm api` is to set swarm api version, swarm api url; it must be the first step to enable other commands

        $ swarm api set api1=tcp://192.168.1.1:3375 api2=tcp://192.168.1.2:3375 api3=tcp://192.168.1.3:3375
        $ swarm api version 1.23
        $ swarm api list
        $ swarm api use api1
        $ swarm api unset api3

* swarm [command] is very similar to docker [command], issue `swarm [command] -h` for usage

* NOT all commands are compatible with docker remote api
