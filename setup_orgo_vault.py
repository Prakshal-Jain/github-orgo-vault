#!/usr/bin/env python3
"""
Setup Orgo VM with Vault and Browser Use
This script creates an Orgo computer, installs the vault repository, and sets up browser-use.

Usage:
    export ORGO_API_KEY="sk_live_..."
    python3 setup_orgo_vault.py
"""

import os
import time
from orgo import Computer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ORGO_API_KEY = os.environ.get("ORGO_API_KEY")
PROJECT_NAME = "samantha-vault"
VAULT_REPO_URL = "https://github.com/Prakshal-Jain/example-vault.git"  # Example GitHub repo - replace with your vault
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # Optional, for browser-use

if not ORGO_API_KEY:
    raise ValueError("ORGO_API_KEY environment variable is required")


def install_system_dependencies(computer):
    """Install system dependencies: git, python, curl, etc."""
    print("📦 Installing system dependencies...")
    
    commands = [
        "sudo apt-get update -qq",
        "sudo apt-get install -y -qq python3 python3-pip python3-venv git curl wget unzip",
        "sudo apt-get install -y -qq build-essential libssl-dev libffi-dev",
    ]
    
    for cmd in commands:
        result = computer.bash(cmd)
        if result.exit_code != 0:
            print(f"⚠️  Warning: Command failed: {cmd}")
            print(f"   Output: {result.output}")
        else:
            print(f"✓ {cmd.split()[0]} installed/updated")


def configure_git(computer, username="Samantha AI", email="samantha@example.com"):
    """Configure Git with user information."""
    print("⚙️  Configuring Git...")
    
    commands = [
        f'git config --global user.name "{username}"',
        f'git config --global user.email "{email}"',
        'git config --global init.defaultBranch main',
        'mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null || true',
    ]
    
    for cmd in commands:
        result = computer.bash(cmd)
        if result.exit_code != 0:
            print(f"⚠️  Warning: Git config failed: {cmd}")
        else:
            print(f"✓ {cmd}")


def clone_vault_repo(computer, repo_url):
    """Clone the vault repository."""
    print(f"📥 Cloning vault repository: {repo_url}")
    
    # Remove existing vault directory if it exists
    computer.bash("rm -rf ~/vault")
    
    # Clone the repository
    # Note: If using SSH, you'll need to set up SSH keys first
    # For HTTPS, you may need credentials or use a public repo
    clone_cmd = f"git clone {repo_url} ~/vault"
    result = computer.bash(clone_cmd)
    
    if result.exit_code != 0:
        print(f"❌ Failed to clone repository")
        print(f"   Error: {result.output}")
        print("\n💡 Tips:")
        print("   - If using SSH: Set up SSH keys first with generate_ssh_key()")
        print("   - If using HTTPS: Make sure the repo is public or use a personal access token")
        return False
    
    print(f"✓ Vault cloned to ~/vault")
    return True


def generate_ssh_key(computer):
    """Generate SSH key pair for GitHub access."""
    print("🔑 Generating SSH key...")
    
    # Generate key if it doesn't exist
    result = computer.bash(
        'test -f ~/.ssh/id_ed25519 || ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "orgo-vm"'
    )
    
    if result.exit_code != 0:
        print(f"⚠️  Warning: SSH key generation may have failed")
    
    # Get public key
    pub_key_result = computer.bash("cat ~/.ssh/id_ed25519.pub")
    public_key = pub_key_result.output.strip() if pub_key_result.exit_code == 0 else ""
    
    if public_key:
        print("✓ SSH key generated")
        print(f"\n📋 Public SSH Key (add this to GitHub):\n{public_key}\n")
        return public_key
    else:
        print("❌ Failed to retrieve public key")
        return None


def install_browser_use(computer):
    """Install browser-use library and dependencies."""
    print("🌐 Installing browser-use...")
    
    # Create installation script to handle long-running operations
    install_script = """#!/bin/bash
set -e

echo "Creating Python virtual environment..."
python3 -m venv ~/browser-use-env

echo "Activating virtual environment and installing browser-use..."
~/browser-use-env/bin/pip install --upgrade pip
~/browser-use-env/bin/pip install browser-use playwright

echo "Installing Chromium browser..."
~/browser-use-env/bin/playwright install chromium

echo "Installing system dependencies for Chromium..."
sudo ~/browser-use-env/bin/playwright install-deps chromium

echo "Verifying installation..."
~/browser-use-env/bin/python -c "import browser_use; print('browser-use installed successfully')"

echo "INSTALL_COMPLETE"
"""
    
    # Write script to file using heredoc (properly formatted)
    heredoc_cmd = f"""cat > /tmp/install-browser-use.sh << 'SCRIPT_EOF'
{install_script}
SCRIPT_EOF"""
    write_result = computer.bash(heredoc_cmd)
    if write_result.exit_code != 0:
        print(f"⚠️  Warning: Failed to write install script: {write_result.output}")
        return False
    
    chmod_result = computer.bash("chmod +x /tmp/install-browser-use.sh")
    if chmod_result.exit_code != 0:
        print(f"⚠️  Warning: Failed to make script executable: {chmod_result.output}")
        return False
    
    # Run installation in background (can take several minutes)
    print("   Running installation (this may take 5-10 minutes)...")
    computer.bash("nohup /tmp/install-browser-use.sh > /tmp/browser-use-install.log 2>&1 &")
    
    # Wait for installation to complete
    max_attempts = 60  # 5 minutes max
    for i in range(max_attempts):
        time.sleep(10)
        check_result = computer.bash(
            'grep -q "INSTALL_COMPLETE" /tmp/browser-use-install.log 2>/dev/null && echo "DONE" || echo "PENDING"'
        )
        
        if "DONE" in check_result.output:
            print("✓ browser-use installed successfully")
            
            # Verify installation
            verify_result = computer.bash(
                '~/browser-use-env/bin/python -c "import browser_use; print(\'Verified\')"'
            )
            if verify_result.exit_code == 0:
                return True
            else:
                print("⚠️  Installation completed but verification failed")
                return False
        
        if i % 6 == 0:  # Print status every minute
            print(f"   Still installing... ({i * 10}s elapsed)")
    
    # Check for errors
    log_result = computer.bash("tail -20 /tmp/browser-use-install.log")
    print("⚠️  Installation timed out. Last log entries:")
    print(log_result.output)
    return False


def setup_browser_use_example(computer):
    """Create an example script showing how to use browser-use."""
    print("📝 Creating browser-use example script...")
    
    example_script = """#!/usr/bin/env python3
'''
Browser-Use Example Script
This demonstrates how to use browser-use in the Orgo VM

Documentation: https://docs.browser-use.com
'''

import os
import asyncio
from browser_use import Agent
from langchain_anthropic import ChatAnthropic

# Example: Use browser-use to navigate and interact with web pages
async def example_browser_use():
    # Initialize LLM (Anthropic Claude)
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        temperature=0,
    )
    
    # Create browser agent
    agent = Agent(
        task="Navigate to https://example.com, find the main heading, and tell me what it says",
        llm=llm,
        browser_config={"headless": False},  # Set to True for headless mode
    )
    
    result = await agent.run()
    print(f"Task result: {result}")
    return result

async def example_search_task():
    """Example: Search Google for information"""
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        temperature=0,
    )
    
    agent = Agent(
        task="Search Google for 'browser-use python library' and summarize the first result",
        llm=llm,
    )
    
    result = await agent.run()
    print(f"Search result: {result}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        asyncio.run(example_search_task())
    else:
        asyncio.run(example_browser_use())
"""
    
    # Write example script using bash heredoc (more reliable than exec for multiline)
    example_heredoc = f"""cat > /root/browser-use-example.py << 'EXAMPLE_EOF'
{example_script}
EXAMPLE_EOF"""
    write_result = computer.bash(example_heredoc)
    if write_result.exit_code != 0:
        print(f"⚠️  Warning: Failed to write example script: {write_result.output}")
        return
    
    chmod_result = computer.bash("chmod +x /root/browser-use-example.py")
    if chmod_result.exit_code != 0:
        print(f"⚠️  Warning: Failed to make example script executable")
        return
    
    # Also install langchain-anthropic if not already installed
    install_result = computer.bash("~/browser-use-env/bin/pip install langchain-anthropic")
    if install_result.exit_code == 0:
        print("✓ langchain-anthropic installed")
    else:
        print("⚠️  Warning: Failed to install langchain-anthropic (may need manual install)")
    
    print("✓ Example script created at ~/browser-use-example.py")


def install_vault_dependencies(computer):
    """Install any additional dependencies needed for the vault."""
    print("📚 Installing vault dependencies...")
    
    # Check if vault has requirements.txt
    result = computer.bash("test -f ~/vault/requirements.txt && echo 'EXISTS' || echo 'NOT_FOUND'")
    
    if "EXISTS" in result.output:
        print("   Found requirements.txt, installing dependencies...")
        install_result = computer.bash(
            "cd ~/vault && pip3 install -r requirements.txt --break-system-packages"
        )
        if install_result.exit_code == 0:
            print("✓ Vault dependencies installed")
        else:
            print("⚠️  Some dependencies may have failed to install")
    else:
        print("   No requirements.txt found, skipping dependency installation")


def take_screenshot(computer, filename="vault-setup.png"):
    """Take a screenshot of the VM."""
    print(f"📸 Taking screenshot...")
    screenshot = computer.screenshot()
    screenshot.save(filename)
    print(f"✓ Screenshot saved to {filename}")


def main():
    """Main setup function."""
    print("🚀 Starting Orgo VM Setup with Vault and Browser-Use\n")
    
    # Create or connect to computer
    print("🖥️  Creating Orgo computer...")
    computer = Computer(
        project=PROJECT_NAME,
        name="samantha-vault-vm",
        ram=4,
        cpu=2,
        os="linux",
        verbose=True,
    )
    
    print(f"✓ Computer created: {computer.id}")
    print(f"   View at: {computer.url}\n")
    
    # Wait for VM to be ready
    print("⏳ Waiting for VM to be ready...")
    time.sleep(15)  # Give VM time to start
    
    try:
        # Step 1: Install system dependencies
        install_system_dependencies(computer)
        print()
        
        # Step 2: Configure Git
        configure_git(computer)
        print()
        
        # Step 3: Generate SSH key (optional, if using SSH for GitHub)
        # Uncomment if you need SSH access:
        # public_key = generate_ssh_key(computer)
        # if public_key:
        #     print("\n⚠️  IMPORTANT: Add this SSH key to your GitHub account:")
        #     print("   Settings > SSH and GPG keys > New SSH key")
        #     input("Press Enter after adding the key to GitHub...")
        # print()
        
        # Step 4: Clone vault repository
        if not clone_vault_repo(computer, VAULT_REPO_URL):
            print("\n⚠️  Repository clone failed. Continuing with other setup steps...\n")
        else:
            print()
        
        # Step 5: Install vault dependencies (if any)
        install_vault_dependencies(computer)
        print()
        
        # Step 6: Install browser-use
        if not install_browser_use(computer):
            print("\n⚠️  browser-use installation had issues. You may need to install manually.\n")
        else:
            print()
            
            # Step 7: Create example script
            setup_browser_use_example(computer)
            print()
        
        # Step 8: Take a screenshot
        take_screenshot(computer)
        print()
        
        print("✅ Setup complete!")
        print(f"\n📋 Summary:")
        print(f"   - Computer ID: {computer.id}")
        print(f"   - Computer URL: {computer.url}")
        print(f"   - Vault location: ~/vault")
        print(f"   - Browser-use: ~/browser-use-env")
        print(f"\n💡 Next steps:")
        print(f"   - Access the VM at: {computer.url}")
        print(f"   - Run browser-use example: ~/browser-use-example.py")
        print(f"   - Use computer.prompt() for AI-powered tasks")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Uncomment to destroy VM when done (for testing)
        # print("\n🗑️  Destroying computer...")
        # computer.destroy()
        print("\n💾 Computer left running. Destroy it manually when done:")
        print(f"   computer.destroy() or DELETE {computer.url}")


if __name__ == "__main__":
    main()

