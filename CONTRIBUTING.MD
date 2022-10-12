# CONTRIBUTING

## Development setup

* Python >= 3.9. Refer [Dockerfile](Dockerfile) to know which version is used officially.
* [Activate your virtual environment](https://docs.python.org/3/library/venv.html)
* Install `make`. Or you can read the `Makefile` to use the commands directly.
* Install dev dependencies: `make install-req-dev`

### Generate dependencies list

If you want to add dependencies into `requirements.txt` or `dev-requirements.txt`:

* Install `pip-tools`: `pip install pip-tools`
* Add your dependencies into `pyproject.toml`
* Generate everything (and install them): `make all-dep-actions`

### Bump version

To bump the version of the project to `1.0.1`: `tbump 1.0.1`

### Build & test Docker image

To build for local testing:

```shell
docker build --rm -t ghcr.io/itdevsamurai/atlassian-plugin-remote-install .
```

Run your test just like [Quick Start](README.md#quick-start) but without `--pull=always`.

## Contributing guide

* [Fork the project](https://github.com/itdevsamurai/atlassian-plugin-remote-install/fork)
* Make changes
* Test your changes via local Python & via Docker
* Create PR to `main`
