# The dev container CLI

The dev container CLI uses a devcontainer.json, like the one in this workspace, and creates and configures a dev container based on it.
This is handy for using the SDK without VS Code UI.

## Installation

- docker installation

Ensure to have node version greater 16 and not above 18

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
export NODE_MAJOR=18
arch=$(dpkg --print-architecture)
echo "deb [arch=$arch signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install nodejs
```

Then install dev container CLI itself

```bash
sudo apt install npm
sudo npm install -g @devcontainers/cli
```

## Setup dev container

- Building: `devcontainer up --workspace-folder ./ebcl_template/`
- Execute a command inside `devcontainer exec --workspace-folder ./ebcl_template/ <command>`

## Build an image

Building an image can be done quite similar to the usual workflow in VS Code.

```bash
devcontainer exec --workspace-folder ./ebcl_template/ bash
(venv) ebcl@25b055e27967:/workspace$ cd images/amd64/appdev/qemu/ebcl_1.x_crinit
(venv) ebcl@25b055e27967:/workspace/images/amd64/appdev/qemu/ebcl_1.x_crinit$ task build
```

## Build and deploy an application

Building an application can be done as described as the alternative method in [here](../apps/index.md#build).

For deploying the built application the following steps can be used:

1. Start Qemu in an additional terminal:

```
devcontainer exec --workspace-folder ./ebcl_template/ bash
(venv) ebcl@25b055e27967:/workspace$ cd images/amd64/appdev/qemu/ebcl_1.x_crinit
(venv) ebcl@25b055e27967:/workspace/images/amd64/appdev/qemu/ebcl_1.x_crinit$ task
```

2. Ensure the ssh conection from your original decontainer session:

```
TARGET=<preset> source /workspace/apps/common/deployment.targets && /workspace/apps/common/check_and_update_ssh_key.sh  --prefix "$SSH_PREFIX"  --port $SSH_PORT --user $SSH_USER --target $TARGET_IP
```

Where `<preset>` is the one also used when building the to be deployed application.

3. Deploy the application from your original decontainer session:

```
TARGET=<preset> source /workspace/apps/common/deployment.targets && $SSH_PREFIX rsync -rlptv -e "ssh -p $SSH_PORT" --exclude */include/* --exclude *.debug /workspace/results/apps/<application>/qemu-aarch64/build/install/ $SSH_USER@[$TARGET_IP]:/
```

Where `<preset>` is again the one also used when building the to be deployed application.

4. Execute the application in the devcontainer with the QEMU session e.g., 

```
root@appdev:~# MyJsonApp 
Exemplary application linked with jsoncpp library to parse a structure into json document
{
	"age" : 30,
	"city" : "New York",
	"name" : "John Doe"
}
```