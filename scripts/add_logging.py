#!/usr/bin/env python3
"""
Script to add logging to all module handlers
Adds imports and logging calls to callback_query and message handlers
"""

import re
from pathlib import Path

# Module files to update
MODULE_FILES = [
    "m2_breach.py",
    "m3_courses.py",
    "m4_jobs.py",
    "m5_tools.py",
    "m6_productivity.py",
    "m7_devtools.py",
    "m8_cybersec.py",
    "m9_osint.py",
    "m10_fun.py"
]

# Import statements to add
LOGGING_IMPORTS = """from app.database import Database
from app.utils.logger import log_button_click, log_search, log_action
"""

# Logging template for callback_query handlers
CALLBACK_LOG_TEMPLATE = """    # Log button click
    db = Database.get_db()
    await log_button_click(db, callback.from_user.id, "{callback_data}", "{module_name}")
    
"""

# Logging template for message handlers (search/action)
MESSAGE_LOG_TEMPLATE = """    # Log user action
    db = Database.get_db()
    await log_search(db, message.from_user.id, message.text or "action", "{module_name}", {{"action": "{action_type}"}})
    
"""

def add_logging_to_file(filepath: Path, module_name: str):
    """Add logging to a module file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if logging already added
    if "from app.utils.logger import" in content:
        print(f"✓ {filepath.name} already has logging imports")
        return False
    
    # Add imports after existing imports
    # Find the last import line
    import_pattern = r'(from app\.bot\.keyboards\.main_menu import.*?\n)'
    match = re.search(import_pattern, content)
    
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + LOGGING_IMPORTS + content[insert_pos:]
        print(f"✓ Added logging imports to {filepath.name}")
    
    # Find all callback_query handlers and add logging
    callback_pattern = r'(@router\.callback_query\(F\.data == "([^"]+)"\)\nasync def \w+\(callback: CallbackQuery[^\)]*\):\n    """[^"]*"""\n)'
    
    def add_callback_log(match):
        decorator_and_def = match.group(0)
        callback_data = match.group(2)
        
        # Skip if already has logging
        if "log_button_click" in decorator_and_def:
            return decorator_and_def
        
        log_code = CALLBACK_LOG_TEMPLATE.format(
            callback_data=callback_data,
            module_name=module_name
        )
        return decorator_and_def + log_code
    
    content = re.sub(callback_pattern, add_callback_log, content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Added logging calls to {filepath.name}")
    return True

def main():
    """Main function"""
    handlers_dir = Path("/home/salman/Documents/Projects/EverythingInBot/app/bot/handlers")
    
    for module_file in MODULE_FILES:
        filepath = handlers_dir / module_file
        if not filepath.exists():
            print(f"✗ {module_file} not found")
            continue
        
        # Extract module name (m2, m3, etc.)
        module_name = module_file.split('_')[0] + "_" + module_file.split('_')[1].replace('.py', '')
        
        add_logging_to_file(filepath, module_name)
        print()

if __name__ == "__main__":
    main()
    print("\\n✅ Logging integration complete!")
