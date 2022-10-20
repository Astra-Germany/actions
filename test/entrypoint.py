import json
import os
import sys

import github
from github import Github


def main():
    APP_REPO = os.getenv("GITHUB_REPOSITORY", None)
    if APP_REPO is None:
        APP_REPO = "Ludy87/xplora_watch"
    GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH", None)
    token = os.getenv("GITHUB_TOKEN", None)

    g = Github(token)

    limit = g.rate_limiting_resettime
    print(g.get_rate_limit())
    print(APP_REPO)
    pull_request: dict = {}
    with open(GITHUB_EVENT_PATH, "r") as f:
        result: dict = json.loads(f.read())
        pull_request: dict = result.get("pull_request", None)
        if pull_request:
            print(pull_request.get("number", None))
        print(result)
    sys.exit(0)
    try:
        repo = g.get_repo(APP_REPO)
        for issue in repo.get_issues(state="closed"):
            if not issue.pull_request:
                for event in issue.get_events():
                    if "connected" == event.event:
                        print(issue.number, event.event)
                if not issue.locked:
                    for label in issue.labels:
                        if "Version 2" not in label.name or "wontfix" in label.name:
                            print(issue.number)
                            print(issue.lock("resolved"))
                if issue.locked:
                    for label in issue.labels:
                        if "wait" in label.name:
                            print(issue.number, issue.remove_from_labels("wait"))
                        if "check for Bug" in label.name:
                            print(issue.number, issue.remove_from_labels("check for Bug"))
                        if "help wanted" in label.name:
                            print(issue.number, issue.remove_from_labels("help wanted"))
            elif issue.pull_request:
                if issue.user.login == "dependabot[bot]":
                    for event in issue.get_events():
                        if "merged" == event.event:
                            issue.add_to_labels("PR: released")
                            try:
                                issue.remove_from_labels("in progress")
                            except github.GithubException:
                                pass
                            continue
                        else:
                            issue.add_to_labels("PR: rejected")
                            try:
                                issue.remove_from_labels("in progress")
                            except github.GithubException:
                                pass
    except github.RateLimitExceededException as err:
        print(err)


if __name__ == "__main__":
    main()