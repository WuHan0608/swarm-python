# swarm-python
Swarm CLI Developed by Python


##### HOW TO USE

* Move the folder into /usr/local/

* Add the following line into ~/.bash_profile and save

        PYTHONPATH=/usr/local/swarm-python/lib
        export PYTHONPATH

* issue the following command, ensure the environment variable takes effict

        $ source ~/.bash_profile
        $ echo $PYTHONPATH

* docker-py is packaged into swarm-python, but extra packages that docker-py deponds on may need to be installed additionally