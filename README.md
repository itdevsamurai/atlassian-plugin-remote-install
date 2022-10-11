# atlassian-plugin-remote-install

Remotely install Atlassian plugins to Jira, Confluence server/datacenter/cloud.

Status:

* [ ] Server/datacenter
  * [x] Jira
  * [ ] Confluence
* [ ] Cloud
  * [ ] Jira
  * [ ] Confluence

See [CONTRIBUTING](CONTRIBUTING.MD) for development setup & contributing guide.

## Usage

### Docker

Quick start:

```shell
docker run --rm -it \
    ghcr.io/itdevsamurai/atlassian-plugin-remote-install \
    install-plugin-server \
    -url https://jira.example.com \
    -u username \
    -p passwordhere \
    -n "slack://xoxb-token-here/#channel-name-here" \
    path/plugin-file.obr
```

This command will install plugin from `path/plugin-file.obr` to Jira
instance `https://jira.example.com` with credentials `username/passwordhere`.

It will then notify you via Slack on channel `#channel-name-here`

### Notification

Powered by [Apprise](https://github.com/caronc/apprise-api), it supports a large
number of services (SMS, email, Slack, Discord, Teams...)

See the list & configuration URL here: [Apprise Wiki](https://github.com/caronc/apprise/wiki)

### Non-Docker

See [CONTRIBUTING](CONTRIBUTING.MD) to install the dependencies.

Invoke `python src/main.py` to see help.

### Environments

Only if you don't want to use arguments in the CLI.

* `LOG_LEVEL`: log level, defaults to `INFO`
* `ATLAS_URL`: base url of Atlassian instance. Can be override in command option.
* `ATLAS_USERNAME`: username to login to Atlassian instance. Can be override in command option.
* `ATLAS_PASSWORD`: password to login to Atlassian instance. Can be override in command option.

## Credits

* Notification powered by [Apprise](https://github.com/caronc/apprise-api)
* [atlassian-api/atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api)
