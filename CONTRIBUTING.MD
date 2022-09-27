## Development setup

* Python >= 3.9. Refer Dockerfile to know which version is used officialy.
* [Activate your virtual environment](https://docs.python.org/3/library/venv.html)
* Install `make`. Or you can read the `Makefile` to use the commands directly.
* Install dev dependencies: `make install-req-dev`

### Generate dependencies list

If you want to add dependencies into `requirements.txt` or `dev-requirements.txt`:

* Install `pip-tools`: `pip install pip-tools`
* Add your dependencies into `pyproject.toml`
* Generate everything (and install them): `make all-dep-actions`

### Build Docker image

TBD

## Contributing

* Fork the project
* Make changes, test your changes
* Create PR to `main`
* Make changes, test your changes
* Create PR to `main`
