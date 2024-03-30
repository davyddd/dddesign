from fabric.api import local


def build():
    local('docker-compose build dddesign')


def _run_command_container(command):
    container_id = local("docker ps | grep 'dddesign' | awk '{{ print $1 }}' | head -n 1", capture=True)
    if container_id:
        local(f'docker exec -it {container_id} bash -c "{command}"')
    else:
        local(f'docker-compose run --rm dddesign bash -c "{command}"')


def linters():
    _run_command_container(
        "ruff . --config ruff.toml --fix && echo 'Ruff check completed' "
        '&& ruff format . --config ruff.toml '
        '&& mypy --config mypy.toml'
    )


def tests():
    _run_command_container('pytest')


def shell():
    _run_command_container('python -m IPython')


def bash():
    _run_command_container('bash')


def kill():
    local('docker kill $(docker ps -q)')
