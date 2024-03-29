# pylint: disable-all

from datetime import datetime

from secret import email, ado_access_token, ado_org, ado_project  # , EXISTING_REPO_NAME

# from secret import email, alterative_ado_access_token, old_ado_org, old_ado_project

from client import AdoClient

from resources.projects import Project
from resources.variable_groups import VariableGroup
from resources.users import AdoUser, Member, Reviewer
from resources.repo import Repo
from resources.commits import Commit
from resources.pull_requests import PullRequest
from resources.builds import Build, BuildDefinition
from resources.branches import Branch
from resources.releases import Release, ReleaseDefinition

ado_client = AdoClient(email, ado_access_token, ado_org, ado_project)

# print(f'{AdoUser.get_by_email(ado_client, "")!r}')

print("Done")


# variable_group = VariableGroup.get_by_name(ado_client, "ben-test")
# data = VariableGroup("123", "my_name", "my_description", {"key": "value", "another_key": "another_value"}, datetime.now(), Member("my_user_name", "UNKNOWN", "my_user_id"),  Member("my_user_name2", "UNKNOWN", "my_user_id2"), datetime.now()).to_json()
# rint("To JSON:", data)
# assert variable_group is not None
# ado_client.import_into_state("VariableGroup", variable_group.variable_group_id)
# rint(VariableGroup.from_json(data))
# rint("Before:", variable_group.to_json())
# variable_group.update(ado_client, "variables", {'abc': '12345'})
# rint("After:", variable_group.to_json())  # type: ignore
# rint("After:", VariableGroup.get_by_name(ado_client, "ben-test").to_json())  # type: ignore
# rint(variable_group.to_json())


# repo = Repo.create(ado_client, "ado-api-test-repo-for-create-delete-commit")
# Commit.create(ado_client, repo.repo_id, "main", "test-branch", {"test.txt": "Delete me!"}, "add", "Test commit")
# pull_request = PullRequest.create(ado_client, repo.repo_id, "test-branch", "Test PR", "Test PR description")
# repo = Repo.get_by_name(ado_client, "ado-api-test-repo-for-create-delete-commit")
# rint(repo.repo_id)
# ado_client.import_into_state("Repo", "87655251-199f-4465-bc2a-af43d09a5613")

# pull_request = PullRequest.create(ado_client, repo.repo_id, "test-branch", "Test PR", "Test PR description")
# assert pull_request.title == "Test PR"
# assert pull_request.description == "Test PR description"

# projects = Project.get_all(ado_client)
# rint(projects)

# ado_client = AdoClient(email, alterative_ado_access_token, old_ado_org, old_ado_project)

# from repository import Repo
# Repo.create(ado_client, "ado-api-test-repo")
