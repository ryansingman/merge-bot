import os
from typing import Dict, List
from urllib import response

import requests


GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")


def check_statuses_of_checks(checks: List[str], repository: str, head_sha: str, acceptable_statuses: List[str]) -> bool:
    """Returns true if all checks have acceptable check status.

    :param checks: checks to check status for
    :param repository: repository to check statuses for
    :param head_sha: head SHA to get check status for
    :param acceptable_statuses: list of acceptable statuses for checks
    :return: true if all checks have acceptable check status
    """
    gh_api_response: requests.Response = requests.get(
        f"https://api.github.com/repos/{repository}/commits/{head_sha}/check-runs",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    )

    assert gh_api_response.status_code == 200, "Bad response from GitHub checks API."

    response_dict: Dict = gh_api_response.json()

    checks_passed: List[bool] = []
    for check_response in response_dict.get("check_runs"):
        check_name = check_response.get("name")
        if check_name not in checks:
            continue

        check_status: str = check_response.get("conclusion")
        check_passed: bool = check_status in acceptable_statuses

        if not check_passed:
            print(f"Check {check_name} failed with status {check_status}")

        checks_passed.append(check_passed)

    return all(check_passed)


if __name__ == "__main__":

    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="Check for dependent checks success.")
    parser.add_argument(
        "--checks",
        help="list of checks to check, as comma separated list",
    )
    parser.add_argument(
        "--repository",
        help="repository to find check statuses for",
    )
    parser.add_argument(
        "--head-sha",
        dest="head_sha",
        help="head SHA to get check statuses for",
    )
    parser.add_argument(
        "--acceptable-check-statuses",
        dest="acceptable_check_statuses",
        help="list of acceptable check statuses, as comma separated list",
    )

    args = parser.parse_args()

    checks: List[str] = args.checks.split(",")
    acceptable_statuses: List[str] = args.acceptable_check_statuses.split(",")

    if not check_statuses_of_checks(checks, args.repository, args.head_sha, acceptable_statuses):
        exit(1)
