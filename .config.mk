# Below is an example of pulling the current version of a node app.

#VERSION is being deprecated by APP_VERSION - no changes necessary - see Makefile
#APP_VERSION=$(shell awk '/version/ {gsub(/[",]/,""); print $$2}' package.json)

GIT_AUTHOR_NAME ?= $(shell git config --get user.name)
GIT_AUTHOR_EMAIL ?= $(shell git config --get user.email)
GIT_COMMITTER_NAME ?= $(GIT_AUTHOR_NAME)
GIT_COMMITTER_EMAIL ?= $(GIT_AUTHOR_EMAIL)
