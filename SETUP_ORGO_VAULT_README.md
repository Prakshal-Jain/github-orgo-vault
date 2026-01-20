# Orgo VM Setup Script

This script automates the setup of an Orgo computer (VM) with:
- Vault repository (GitHub)
- Browser-use library for web automation
- Python environment and dependencies

## Prerequisites

1. **Orgo API Key**: Get your API key from [orgo.ai/workspaces](https://www.orgo.ai/workspaces)
2. **Python 3.8+** with `orgo` package installed
3. **Optional**: Anthropic API key for browser-use examples

## Installation

```bash
# Install Orgo Python SDK
pip install orgo python-dotenv

# Or if using requirements.txt
pip install -r requirements.txt
```

## Configuration

1. Set your Orgo API key:
```bash
export ORGO_API_KEY="sk_live_your_api_key_here"
```

2. (Optional) Set Anthropic API key for browser-use:
```bash
export ANTHROPIC_API_KEY="sk-ant-your_key_here"
```

3. Edit `setup_orgo_vault.py` and update the vault repository URL:
```python
VAULT_REPO_URL = "https://github.com/your-username/your-vault.git"
```

## Usage

### Basic Usage

```bash
python3 setup_orgo_vault.py
```

### With SSH Key for Private Repos

If your vault repository is private and uses SSH:

1. Uncomment the SSH key generation section in `main()`:
```python
public_key = generate_ssh_key(computer)
if public_key:
    print("\n⚠️  IMPORTANT: Add this SSH key to your GitHub account:")
    print("   Settings > SSH and GPG keys > New SSH key")
    input("Press Enter after adding the key to GitHub...")
```

2. Update the `VAULT_REPO_URL` to use SSH format:
```python
VAULT_REPO_URL = "git@github.com:your-username/your-vault.git"
```

## What the Script Does

1. **Creates Orgo Computer**: Provisions a Linux VM with specified RAM/CPU
2. **Installs System Dependencies**: Python, Git, curl, build tools
3. **Configures Git**: Sets up user name and email
4. **Clones Vault Repository**: Downloads your vault from GitHub
5. **Installs Browser-Use**: Sets up browser-use library and Playwright
6. **Installs Vault Dependencies**: If vault has `requirements.txt`
7. **Creates Example Scripts**: Browser-use usage examples
8. **Takes Screenshot**: Captures the final state

## Example GitHub Repository

The script includes an example repository URL. Replace it with your own:

- **Example**: `https://github.com/Prakshal-Jain/example-vault.git`
- **Your repo**: Update `VAULT_REPO_URL` in the script

## Using Browser-Use

After setup, you can use browser-use in the VM:

```python
from orgo import Computer
from browser_use import Agent
from langchain_anthropic import ChatAnthropic

computer = Computer(computer_id="your-computer-id")

# Run browser-use example script
computer.bash("cd ~ && ~/browser-use-env/bin/python browser-use-example.py")
```

Or use Orgo's `prompt()` method for AI-powered browser automation:

```python
computer.prompt("Navigate to example.com and take a screenshot")
```

## Using the Vault

The vault is cloned to `~/vault` in the VM. You can:

- Access files: `~/vault/`
- Sync with GitHub: The script sets up automatic syncing (optional)
- Modify and commit: Use Git commands in the VM

## Cleanup

To destroy the computer when done:

```python
from orgo import Computer

computer = Computer(computer_id="your-computer-id")
computer.destroy()
```

Or use the Orgo dashboard at [orgo.ai/workspaces](https://www.orgo.ai/workspaces)

## Troubleshooting

### Repository Clone Fails

- **Public repo**: Use HTTPS URL
- **Private repo**: Set up SSH keys first (see SSH section above)
- **HTTPS with auth**: You may need to use a personal access token in the URL

### Browser-Use Installation Times Out

- Installation can take 5-10 minutes. The script waits up to 10 minutes.
- Check logs: `computer.bash("cat /tmp/browser-use-install.log")`
- Try manual installation: `computer.bash("~/browser-use-env/bin/pip install browser-use playwright")`

### VM Not Ready

- The script waits 15 seconds after creation. You may need to increase this.
- Check VM status: `computer.status()`
- Wait manually: `time.sleep(30)`

## References

- **Orgo Docs**: https://docs.orgo.ai
- **Browser-Use Docs**: https://docs.browser-use.com
- **Orgo Python SDK**: Install with `pip install orgo`

## Example Output

```
🚀 Starting Orgo VM Setup with Vault and Browser-Use

🖥️  Creating Orgo computer...
✓ Computer created: 550e8400-e29b-41d4-a716-446655440000
   View at: https://orgo.ai/workspaces/550e8400-e29b-41d4-a716-446655440000

⏳ Waiting for VM to be ready...
📦 Installing system dependencies...
✓ apt-get installed/updated
⚙️  Configuring Git...
✓ git config --global user.name "Samantha AI"
📥 Cloning vault repository: https://github.com/example/example-vault.git
✓ Vault cloned to ~/vault
🌐 Installing browser-use...
   Running installation (this may take 5-10 minutes)...
✓ browser-use installed successfully
📝 Creating browser-use example script...
✓ Example script created at ~/browser-use-example.py
📸 Taking screenshot...
✓ Screenshot saved to vault-setup.png

✅ Setup complete!

📋 Summary:
   - Computer ID: 550e8400-e29b-41d4-a716-446655440000
   - Computer URL: https://orgo.ai/workspaces/...
   - Vault location: ~/vault
   - Browser-use: ~/browser-use-env
```

