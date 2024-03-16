from fabric.api import local


def run():
    local('docker-compose run --rm runner-linters')


def build():
    local('docker-compose build runner-linters')


def shell():
    local('docker-compose run --rm runner-linters bash -c "python -m IPython"')


def bash():
    local('docker-compose run --rm runner-linters bash')


def kill():
    local('docker kill $(docker ps -q)')
