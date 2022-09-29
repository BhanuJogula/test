# # Makefile Usage
#
# Run `make test` to start the local Thumbnail server (docker container),
# and run all the tests.
#
# Use this Makefile to do various actions with this repository.
# It can start and stop the Thumbnail server Docker container.
# It (re)builds the Docker image if needed.
# Actions that require the server will start it if needed.
#
# # Set Configs
# ```
# export BIFROST_URL="your bifrost url"
# export BIFROST_SECRET="your Bifrost secret"
# ```

SHELL := bash
ROOT := $(shell pwd)

NAME := thumbnail
DOCKER_TAG := $(NAME)
DOCKER_NAME := $(NAME)
DOCKER_BUILD := /tmp/$(NAME)_docker_build
DOCKER_RUN := /tmp/$(NAME)_docker_run
DOCKER_HISTORY := /tmp/$(NAME)-bash-history

MAN_FILE := man/man1/$(NAME).1
MAN_TMP := /tmp/$(NAME).md

DOCKER_BUILD_DEPS := \
    Dockerfile \
    Makefile \
    Pipfile \
    Pipfile.lock \

APP_BIFROST_CONF := config/dev/bifrost.json

TOKEN_FILE := config/token.jwt
TEST_READY := $(DOCKER_RUN) $(TOKEN_FILE)

ifneq (,$(shell command -v jq)) 
JQ := jq
BIFROST_CLIENT_BRAND := $(shell cat $(APP_BIFROST_CONF) | jq .test_brand)
BIFROST_CLIENT_ACCOUNT := $(shell cat $(APP_BIFROST_CONF) | jq .test_account)
else
JQ := cat; echo
BIFROST_CLIENT_BRAND := $(shell cat $(APP_BIFROST_CONF) | grep 'test_brand' | awk -F': ' '{ print $2 }' | tr -d '",')
BIFROST_CLIENT_ACCOUNT := $(shell grep test_account $(APP_BIFROST_CONF) | | grep 'test_account' | awk -F': ' '{ print $2 }' | tr -d '",')
endif

TEST_DEMO := \
    test-hello \

o ?= -s --color=yes
pytest-opts ?= $o

PORT ?= 8000
SERVER_URL := http://localhost:$(PORT)/v1


.DELETE_ON_ERROR:

#------------------------------------------------------------------------------
# # Makefile Targets
#------------------------------------------------------------------------------
#
default: help

#------------------------------------------------------------------------------
# ## Local Setup
#------------------------------------------------------------------------------
#
# * `make setup`
#
#   Install `pipenv` for Python dependency management.
#   This is only required if you need to add new deps or would like to run
#   locally.
#   Otherwise you can use the docker container.
#
# * Installing New Dependencies
#
#       pipenv install <pip_module>
#
#   This command works the same as pip, except it will also add the new
#   dependency to Pipfile and regenerate Pipfile.lock.
#   Both Pipfile and Pipfile.lock should be committed to git.
#
setup:
ifeq (,$(shell command -v pip3))
	$(error 'pip3' is required but not installed)
endif
ifeq (,$(shell command -v pyenv))
	$(error 'pyenv' is required but not installed)
endif

#------------------------------------------------------------------------------
# ## Testing Targets
#------------------------------------------------------------------------------
#
# * `make test`
#
#   Runs `make test-pytest`.
#
test: test-pytest

# * `make test-all`
#
#   Runs `make test-pytest test-demo`.
#
test-all: test-pytest test-demo

# * `make test-pytest`
#
#   Run pytest tests in container.
#
test-pytest: $(DOCKER_RUN)
	@echo '*** Running pytest in container ***'
	docker exec -t \
	    $(DOCKER_NAME) \
	    pytest $(pytest-opts)

# * `make test-demo`
#
#   Run curl demo tests.
#
test-demo: $(TEST_DEMO)


#------------------------------------------------------------------------------
# ## Docker Thumbnail Server Targets
#------------------------------------------------------------------------------
#
# * `make build`
#
#   (Re)Build the 'thumbnail' Docker image.
#   This normally happens automatically when the image is needed.
#
build:
	docker build -t $(DOCKER_TAG) .
	touch $(DOCKER_BUILD)

$(DOCKER_BUILD): $(DOCKER_BUILD_DEPS)
ifneq (,$(wildcard $(DOCKER_RUN)))
	@$(MAKE) stop
endif
	@echo '*** Building Docker image $(DOCKER_TAG) ***'
	docker build -t $(DOCKER_TAG) .
	touch $@
	@echo

# * `make start`
#
#   Run the 'thumbnail' Docker server container.
#   The container is automatically started if needed by the `test-*` rules.
#
start: check-run $(DOCKER_RUN)

$(DOCKER_RUN): $(DOCKER_BUILD)
ifeq (,$(wildcard DOCKER_RUN))
	@echo '*** Starting Docker Server ***'
ifeq (,$(wildcard $(DOCKER_HISTORY)))
	touch $(DOCKER_HISTORY)
endif
	docker run -d --rm \
	    --name $(DOCKER_TAG) \
	    -v $(ROOT)/bin:/usr/src/app/bin \
	    -v $(ROOT)/app:/usr/src/app/app \
	    -v $(ROOT)/test:/usr/src/app/test \
	    -v $(ROOT)/config:/usr/src/app/config \
	    -v $(DOCKER_HISTORY):/root/.bash_history \
	    -e BIFROST_URL \
	    -e BIFROST_SECRET \
	    --env-file config/alpha.env \
	    -p 8000:8000 \
	    $(DOCKER_TAG) > $@
	@sleep 1
	@echo
endif

# * `make stop`
#
#   Stop/kill the Docker server container.
#
stop:
ifeq (,$(wildcard $(DOCKER_RUN)))
	$(error Docker container '$(DOCKER_NAME)' is not running)
endif
	@echo '*** Stopping Docker Server ***'
	-docker kill $(DOCKER_NAME) || docker rm $(DOCKER_NAME)
	rm -f $(DOCKER_RUN)
	@echo

# * `make status`
#
#   Show if the Docker server is running or not.
#
status:
	docker ps -f name=$(DOCKER_NAME)

# * `make shell`
#
#   Start a Bash shell inside the running server container.
#   Command history is preserved between sessions.
#
shell: $(DOCKER_RUN)
	docker exec -it \
	    $(DOCKER_NAME) \
	    bash

#------------------------------------------------------------------------------
# ## Other Targets
#------------------------------------------------------------------------------
#
# * `make help`
#
#   Show this help.
#
help: $(MAN_FILE)
	@man $<

## Build help man page from README.md

# * `make README.md`
#
#   The README.md file is generated.
#   If you want to update it, change either `doc/help.md` or `Makefile` (which
#   cantains Markdown comments inline).
#   You need to run `make help` (or `make README.md man/man1/thumbnail.1`) to
#   update the generated files.
#
$(MAN_FILE): README.md
ifeq (,$(shell command -v ronn))
	$(info NOTICE: $@ needs update but 'ronn' not installed)
	@touch $@
else
	$(info Updating $@)
	@cp $< $(MAN_TMP)
	@ronn $(MAN_TMP) 2>/dev/null
	@perl -p0e 's/^\.\n\.IP\ ""\ \d+\n\n?//gm' $(MAN_TMP:%.md=%) > $@
	@rm -f $(MAN_TMP) $(MAN_TMP:%.md=%) $(MAN_TMP:%.md=%).*
endif

# * `make clean`
#
#   Remove all generated files.
#   This will also stop the server container if it is running.
#
clean:
ifneq (,$(wildcard $(DOCKER_RUN)))
	-$(MAKE) stop
endif
	rm -f $(DOCKER_BUILD) $(DOCKER_RUN) $(TOKEN_FILE)
	find . -type d -name __pycache__ | xargs rm -fr
	rm -fr .pytest_cache/

distclean: clean

#------------------------------------------------------------------------------
###  Internal targets
#------------------------------------------------------------------------------
check-run:
ifneq (,$(wildcard $(DOCKER_RUN)))
	$(info Docker container '$(DOCKER_NAME)' appears to be running.)
	$(info If that is not true, run 'make clean'.)
	$(error)
endif

$(TOKEN_FILE): $(DOCKER_RUN)
	docker exec $(DOCKER_NAME) \
	    python ./bin/create-token \
	        --brand $(BIFROST_CLIENT_BRAND) \
			--account $(BIFROST_CLIENT_ACCOUNT) \
	    > $@

## Build README.md from doc/help.md and Makefile comments
README.md: doc/help.md Makefile
	$(info Updating $@)
	@echo -e '<!-- DO NOT EDIT. GENERATED from $^ -->\n' > $@
	@cat $< >> $@
	@echo >> $@
	@grep -E '^#( |$$)' Makefile | cut -c3- >> $@
	@perl -pi -e 's/^#/##/' $@

# # TODO
#
# * Add rules to deploy to openshift with Makefile
# * Fix failures for `make test-pytest`
