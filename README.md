# ado-api

This is a Python Package which works as an interface to the Azure DevOps API

It is essentially a wrapper for the horrible to work with ADO API, and supports OOP principals.

Any resource can be fetched by calling the `<resource>.get_by_id()` function.

It also includes a solution for managing resources created by this script, which is extremely useful for testing the creation of random resources.
To delete all resources created by this, run the main module with the "--delete-everything" flag.
