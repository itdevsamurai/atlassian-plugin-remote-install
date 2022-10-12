# Atlassian Plugin Remote Install

[![Publish Docker Image](https://github.com/itdevsamurai/atlassian-plugin-remote-install/actions/workflows/publish-docker-image.yml/badge.svg)](https://github.com/itdevsamurai/atlassian-plugin-remote-install/actions/workflows/publish-docker-image.yml)

Remotely install Atlassian plugins to Jira, Confluence server/datacenter/cloud.

[Documentation](https://itdevsamurai.github.io/atlassian-plugin-remote-install/)

## Usage

We will only focus on the latest version of the tool as Docker image, hosted at
[Github Package](https://github.com/orgs/itdevsamurai/packages/container/package/atlassian-plugin-remote-install)

Docker tags:

* `latest`: latest stable release.
* `main`: latest build on `main` branch. This is a beta build.
* Semver tags (`0.4.0`, `0.3.1`...): for archiving purpose, can be used to rollback if
you have any issue with stable build.

### Quick Start

```shell
docker run --rm -i \
    --pull=always \
    ghcr.io/itdevsamurai/atlassian-plugin-remote-install \
    install-plugin-server \
    -url https://jira.example.com \
    -u username \
    -p passwordhere \
    -n "slack://xoxb-token-here/#channel-name-here" \
    - < path/plugin-file.obr
```

This command will install plugin from `path/plugin-file.obr` to Jira
instance `https://jira.example.com` with credentials `username/passwordhere`.

It will then notify you via Slack on channel `#channel-name-here`

For more info about commands & options, see [CLI reference](https://itdevsamurai.github.io/atlassian-plugin-remote-install/cli/)

### Notification

Powered by [Apprise](https://github.com/caronc/apprise-api), it supports a large
number of services (SMS, email, Slack, Discord, Teams...)

See the list & configuration URL here: [Apprise Wiki](https://github.com/caronc/apprise/wiki)

### In pipelines

Can be used in Bitbucket, Github Actions... to quickly build your plugin & deploy to staging instance.

See [Pipelines](https://itdevsamurai.github.io/atlassian-plugin-remote-install/pipelines/)

### Non-Docker

See [CONTRIBUTING](CONTRIBUTING.MD) to install the dependencies.

Invoke `python src/main.py` to see help.

### Environment Variables

Only if you don't want to use arguments in the CLI.

* `LOG_LEVEL`: log level, defaults to `INFO`
* `ATLAS_URL`: base url of Atlassian instance. Can be override in command option.
* `ATLAS_USERNAME`: username to login to Atlassian instance. Can be override in command option.
* `ATLAS_PASSWORD`: password to login to Atlassian instance. Can be override in command option.

### Feature status

Status:

* [ ] Server/datacenter
  * [x] Jira
  * [ ] Confluence
* [ ] Cloud
  * [ ] Jira
  * [ ] Confluence

## Contributing

See [CONTRIBUTING](CONTRIBUTING.MD) for development setup & contributing guide.
