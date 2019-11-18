import os
from pprint import pprint
import logging

logging.basicConfig(level=logging.INFO)

from flask import Flask
from github_webhook import Webhook
from github import GithubIntegration, Github

log = logging.getLogger("main")

project_repo_map = {
    22: [  # Backends
        "api",
        "orchestra",
        "sysadmin",
        "pipeline",
        "backend-legacy",
        "collector",
    ],
    23: ["probe-engine", "jafar", "netx", "spec", "EvilGenius",],  # Measurements
    21: [  # Apps
        "probe-cli",
        "design-system",
        "probe-desktop",
        "probe-ios",
        "probe-android",
        "probe-legacy",
        "run",
        "probe-react-native",
        "explorer",
        "probe",
        "explorer-legacy",
        "design.ooni.io",
    ],
    24: [  # Research & Content
        "translations",
        "datk",
        "slides",
        "notebooks",
        "license",
        "code-style",
        "labs",
        "ooni.io",
        "gatherings",
    ],
}

app = Flask(__name__)
webhook = Webhook(app)  # Defines '/postreceive' endpoint

GH_PRIVATE_KEY_PATH = os.environ["GH_PRIVATE_KEY_PATH"]
def get_github():
    with open(GH_PRIVATE_KEY_PATH) as in_file:
        gh_integration = GithubIntegration(
            integration_id=47055, private_key=in_file.read()
        )

    installation = gh_integration.get_installation("ooni", "probe")
    access_token = gh_integration.get_access_token(
        installation_id=installation.id.value
    )
    return Github(login_or_token=access_token.token)


def build_repo_project_map(g):
    repo_project_map = {}
    projects = [p for p in g.get_organization("ooni").get_projects()]
    for project_id, repos in project_repo_map.items():
        # We use the html_url to determine the paths based on what appears in your browser
        project = list(
            filter(lambda p: p.html_url.endswith("/{}".format(project_id)), projects)
        )
        if len(project) != 1:
            raise Exception("Cannot find the project ID")
        project = project[0]

        icebox_column = None
        for c in project.get_columns():
            if c.name == "Icebox":
                icebox_column = c

        print("{}: {}".format(project, project_id))
        for repo in repos:
            if repo in repo_project_map:
                raise Exception("duplicate repo name")
            repo_project_map[repo] = {
                "project": project,
                "icebox_column": icebox_column,
            }
    return repo_project_map

def on_issue_opened(data):
    # TODO this should not be done on every hook trigger
    gh = get_github()
    repo_map = build_repo_project_map(gh)

    repo_name = data["repository"]["name"]
    issue_id = data["issue"]["id"]
    if repo_name not in repo_map:
        log.warn("{} is not in repo_map".format(repo_name))
        log.warn("ignoring {}".format(data["issue"]["html_url"]))
        return

    project = repo_map[repo_name]
    project["icebox_column"].create_card(content_id=issue_id, content_type="Issue")


@webhook.hook()
def on_push(data):
    print("Got push with: {0}".format(data))


@webhook.hook(event_type="issues")
def on_issues(data):
    print("Got issue with: {0}".format(data))
    if data["action"] == "opened":
        on_issue_opened(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
