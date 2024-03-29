# To-do

The whole state idea, for each class that creates stuff, add it to the state file
Have a CLI to clear state, maybe of certain resources
When you delete from ado, it should also delete from state
Maybe show a type when adding to state too, like "Add": abc
This lets us store and perhaps revert updates?

Resources that are entirely state managed:
Build -*
BuildDefinition -*
ReleaseDefinition
Release
Repo -*
VariableGroup -*

Soon:
Pull Request, Commit

-* = Supports edits/updates too

-----

Integrations testing, we already kind of do that, but with variable groups + repos + builds?

Add "Update" to more stuff, prevent updates on uneditable attributes in state_managed_abc/update

When I am testing .from_request_payload, maybe use the plan object's data?

TODO: Look into Pushes vs Commits <https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pushes/get?view=azure-devops-rest-5.1&tabs=HTTP#gitpush>

Also, Releases need vigerous testing - kinda wip, ReleaseDef - Update

Get this packaged up!

Perhaps when creating stuff, use a "while True" loop with user input, if they input "y", go to the next step?

Rollback a commit? Tricky...

Update the state file on startup, and have an option to disable it - DONE
Maybe add the alternative way? I.E. if it's changed in real resources

Script plan mode?

Teams.get_members(recursive=True)  Not sure that Teams are the right thing, maybe Groups? Idk

<https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict>
This might allow us to remove "as_json"

For state, have lifecycle policies, split each id into id -> {data, lifecyclepolicy, run_id?}

Look into tags for resources?
<https://learn.microsoft.com/en-us/rest/api/azure/devops/git/annotated-tags/get?view=azure-devops-rest-7.1&tabs=HTTP>

-----

Pylint command:
pylint *.py
mypy . --strict
black . --line-length 140
pytest tests/ -vvvv -s
python3.11 -m client --delete-everything
python3.11 -m client --delete-everything --state-file "test_state.state"
python3.11 -m client --refresh-resources-on-startup
pytest tests/ -vvvv -s -m wip

Re-run on "connction error"

For the plans, have a new folder, called "plan_resources", which has all the same resources, but a few differences:

1. Each object will hold a dictionary of key=tuple, with first item, request type, second item, regex pattern (for the url) to match against. The value of each key, value pair will be a fake requets object with it's json set to a dump of what it normally returns, with ids containing a new singleton.
2. When we want planned things, we should decorate functions, which when run, will take over requests.get or whatever to use our custom classes.
3. On startup, the plan will refresh all state, and if it tried to fetch stuff that's not in state, it'll also try in the real world
4. The ado_client should have a "is_planning" bool, which will dictate stuff.
5. When we are in planning mode, we should have an in memory state, which will start as a duplicate of the updated local state
6. This local state will get updated when we create or destroy things
