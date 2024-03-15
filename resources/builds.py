from datetime import datetime
from typing import Any, Literal
from dataclasses import dataclass, field

import requests

from client import AdoClient
from utils import from_ado_date_string, DeletionFailed
from state_managed_abc import StateManagedResource
from resources.users import Member
from resources.repo import Repo

BuildStatus = Literal["notStarted", "inProgress", "completed", "cancelling", "postponed", "notSet", "none"]
QueuePriority = Literal["low", "belowNormal", "normal", "aboveNormal", "high"]

# ========================================================================================================


def get_build_definition(
    name: str, repo_id: str, repo_name: str, path_to_pipeline: str, description: str, project: str, agent_pool_id: str
) -> dict[str, Any]:
    return {
        "name": f"{name}",
        "description": description,
        "repository": {"id": repo_id, "name": repo_name, "type": "TfsGit", },
        "project": project,
        "process": {
            "yamlFilename": path_to_pipeline,
            "type": 2,
        },
        "type": "build",
        "queue": {"id": agent_pool_id},
    }


# ========================================================================================================


@dataclass(slots=True)
class Build(StateManagedResource):
    """https://learn.microsoft.com/en-us/rest/api/azure/devops/build/builds?view=azure-devops-rest-7.1"""
    build_id: str
    build_number: str
    status: BuildStatus
    requested_by: Member
    repo: Repo
    parameters: dict[str, str]
    start_time: datetime | None = field(default=None)
    finish_time: datetime | None = field(default=None)
    queue_time: datetime | None = field(default=None)
    reason: str = field(default="An automated build created by the ADO-API")
    priority: QueuePriority = field(default="normal")

    def __str__(self) -> str:
        return f"{self.build_number} ({self.build_id}), {self.status}"

    @classmethod
    def from_request_payload(cls, data: dict[str, Any]) -> "Build":
        requested_by = Member(data["requestedBy"]["displayName"], data["requestedBy"]["uniqueName"], data["requestedBy"]["id"])
        repo = Repo(data["repository"]["id"], data["repository"]["name"])
        return cls(str(data["id"]), str(data["buildNumber"]), data["status"], requested_by, repo, data.get("templateParameters", {}),
                   from_ado_date_string(data.get("startTime")), from_ado_date_string(data.get("finishTime")),
                   from_ado_date_string(data.get("queueTime")), data["reason"], data["priority"])  # fmt: skip

    @classmethod
    def get_by_id(cls, ado_client: AdoClient, build_id: str) -> "Build":
        response = requests.get(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/builds/{build_id}?api-version=7.1",
            auth=ado_client.auth,
        ).json()
        return cls.from_request_payload(response)

    @classmethod
    def create(cls, ado_client: AdoClient, definition_id: str, source_branch: str="refs/heads/main") -> "Build":
        request = requests.post(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/builds?definitionId={definition_id}&sourceBranch={source_branch}&api-version=7.1",
            json={"reason": "An automated build created by the ADO-API"}, auth=ado_client.auth,  # fmt: skip
        ).json()
        return cls.from_request_payload(request)

    @staticmethod
    def delete_by_id(ado_client: AdoClient, build_id: str) -> None:
        delete_request = requests.delete(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/builds/{build_id}?api-version=7.1",
            auth=ado_client.auth,
        )
        assert delete_request.status_code == 204

    # ============ End of requirement set by all state managed resources ================== #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # =============== Start of additional methods included with class ===================== #

    @classmethod
    def get_all_by_definition(cls, ado_client: AdoClient, definition_id: str) -> "list[Build]":
        response = requests.get(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/builds?api-version=7.1&definitions={definition_id}",
            auth=ado_client.auth,
        ).json()["value"]
        return [cls.from_request_payload(build) for build in response]

    def delete(self, ado_client: AdoClient) -> None:
        return self.delete_by_id(ado_client, self.build_id)


# ========================================================================================================


@dataclass(slots=True)
class BuildDefinition(StateManagedResource):
    """https://learn.microsoft.com/en-us/rest/api/azure/devops/build/definitions?view=azure-devops-rest-7.1"""
    build_definition_id: str = field(repr=True, metadata={"is_id_field": True}) # Static
    name: str = field(repr=True, metadata={"editable": True})
    description: str = field(repr=True, metadata={"editable": True})
    path: str
    created_by: Member
    created_date: datetime
    repo: Repo = field(repr=False)
    variables: dict[str, str] | None = field(default_factory=dict, repr=False)  # type: ignore[assignment]
    variable_groups: list[int] | None = field(default_factory=list, repr=False)  # type: ignore[assignment]

    def __str__(self) -> str:
        return f"{self.name}, {self.build_definition_id}, created by {self.created_by}, created on {self.created_date!s}"

    @classmethod
    def from_request_payload(cls, data: dict[str, Any]) -> "BuildDefinition":
        """Creates a build definition object from the response payload of a request to the ADO API. Repo is not always present"""
        created_by = Member(data["authoredBy"]["displayName"], data["authoredBy"]["uniqueName"], data["authoredBy"]["id"])
        repo = Repo(data.get("repository", {"id": "UNKNOWN"})["id"], data.get("repository", {"name": "UNKNOWN"})["name"])
        return cls(str(data["id"]), data["name"], data.get("description", ""), data.get("process", {"yamlFilename": "UNKNOWN"})["yamlFilename"], created_by,
                   from_ado_date_string(data["createdDate"]), repo, data.get("variables", None), data.get("variableGroups", None))  # fmt: skip

    @classmethod
    def get_by_id(cls, ado_client: AdoClient, build_definition_id: str) -> "BuildDefinition":
        response = requests.get(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/definitions/{build_definition_id}?api-version=7.1",
            auth=ado_client.auth,
        ).json()
        return cls.from_request_payload(response)

    @classmethod
    def create(
        cls, ado_client: AdoClient, name: str, repo_id: str, repo_name: str, path_to_pipeline: str, description: str, agent_pool_id: str, branch_name: str="main"
    ) -> "BuildDefinition":
        """Takes a list of variable group ids to include, and an agent_pool_id"""
        body = get_build_definition(name, repo_id, repo_name, path_to_pipeline, description, ado_client.ado_project, agent_pool_id)
        request = requests.post(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/definitions?sourceBranch={branch_name}&api-version=7.0",
            json=body,
            auth=ado_client.auth,
        ).json()
        resource = cls.from_request_payload(request)
        ado_client.add_resource_to_state(cls.__name__, request["id"], resource.to_json())  # type: ignore[arg-type]
        return resource

    @classmethod
    def delete_by_id(cls, ado_client: AdoClient, resource_id: str) -> None:
        request = requests.delete(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/definitions/{resource_id}?forceDelete=true&api-version=7.1",
            auth=ado_client.auth,
        )
        if request.status_code != 204:
            raise DeletionFailed(f"Failed to delete {cls.__name__} with id {resource_id}")
        ado_client.remove_resource_from_state(cls.__name__, resource_id)  # type: ignore[arg-type]

    # ============ End of requirement set by all state managed resources ================== #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # =============== Start of additional methods included with class ===================== #

    def get_all_builds_by_definition(self, ado_client: AdoClient) -> "list[Build]":
        return Build.get_all_by_definition(ado_client, self.build_definition_id)

    @classmethod
    def get_all_by_repo_id(cls, ado_client: AdoClient, repo_id: str) -> "list[BuildDefinition]":
        response = requests.get(
            f"https://dev.azure.com/{ado_client.ado_org}/{ado_client.ado_project}/_apis/build/definitions?repositoryId={repo_id}&repositoryType={'TfsGit'}&api-version=7.1",
            auth=ado_client.auth,
        ).json()["value"]
        return [cls.from_request_payload(build) for build in response]

    def delete(self, ado_client: AdoClient) -> None:
        return self.delete_by_id(ado_client, self.build_definition_id)


# ========================================================================================================