from fabric.api import local

SERVICE_NAME = 'dddesign'


def build():
    local(f'docker-compose build {SERVICE_NAME}')


def _run_command_container(command):
    container_id = local(f"docker ps | grep '{SERVICE_NAME}' | awk '{{ print $1 }}' | head -n 1", capture=True)
    if container_id:
        local(f'docker exec -it {container_id} bash -c "{command}"')
    else:
        local(f'docker-compose run --rm {SERVICE_NAME} bash -c "{command}"')


def tests():
    _run_command_container('pytest')


def linters():
    _run_command_container(
        "(ruff check . --config ruff.toml --fix && echo 'Ruff check completed'); "
        "(ruff format . --config ruff.toml && echo 'Ruff format completed'); "
        "(ty check --config-file ty.toml && echo 'Ty completed'); "
        "(complexipy && echo 'Complexipy completed'); "
    )


def execute(command):
    _run_command_container(command)


def shell():
    _run_command_container('python -m IPython')


def bash():
    _run_command_container('bash')


### Helpers for working with docker


def kill():
    local('docker kill $(docker ps -q)')


def remove_none_images():
    local('docker rmi -f $(docker images -f "dangling=true" -q)')


def remove_all_containers():
    local('docker rm -f $(docker ps -aq)')
    local('docker volume rm -f $(docker volume ls -q)')
