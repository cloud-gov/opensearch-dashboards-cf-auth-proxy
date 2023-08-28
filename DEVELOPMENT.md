# Development

## Getting started

Most development-related tasks are exposed in the `dev` script. To just get started developing,
running `./dev set-up-environment` will set up an environment for you. This does not touch anything
outside of this repository.

To see all of the available commands, run `./dev -h`.

## Running e2e tests locally

1. Update your `.env` file and uncomment/set values for the e2e test variables. You can find the necessary
variables in `.env-sample`. You can get the values used in the pipeline from the credentials file stored
on S3.
1. [Make sure your local development stack is up and running](./README.md#running-locally)
1. Run `./dev e2e-local`

## Code style

Code is styled with `black`, which is configured in `pyproject.toml`. This means you can (and
should) simply run `black` before committing, and everything will automagically be formatted consistently.

## Managing requirements

Requirements are managed with pip-compile. To add a new package to the environment, add the
loosest-version constraint to `pip-tools/requirements.in` (or `pip-tools/dev-requirements.in`
if it's a development requirement) then run ./dev update-requirements
