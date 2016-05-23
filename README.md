# swarm-python
Swarm CLI Developed by Python


##### HOW TO USE

* Move the folder into /usr/local/

* Add the following line into ~/.bash_profile and save

        PYTHONPATH=/usr/local/swarm-python/lib
        PATH=/usr/local/swarm-python/bin:$PATH
        export PYTHONPATH
        export $PATH

* issue the following command, ensure the environment variable takes effect

        $ source ~/.bash_profile
        $ echo $PYTHONPATH

* docker-py is packaged into swarm-python, but extra packages that docker-py deponds on may need to be installed additionally

        $ pip install requests six websocket-client

* `swarm api` is a new command for swarm api settings including swarm api version, swarm api url; this must be the first step to enable further commands

        $ swarm api set api1=tcp://192.168.1.1:3375 api2=tcp://192.168.1.2:3375 api3=tcp://192.168.1.3:3375
        $ swarm api version 1.20
        $ swarm api get all
        $ swarm api use api1
        $ swarm api get current
        $ swarm api unset api3

* swarm [command] is very similar to docker [command], issure `swarm [command] -h` for command help

* NOT all commands are compatible with docker remote api
