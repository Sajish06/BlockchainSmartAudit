import os
import re
import json
import logging
from solcx import install_solc, set_solc_version, compile_standard, get_installed_solc_versions, get_installable_solc_versions

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CONTRACT_DIR = "contracts"
AST_DIR = "ast_json"
MIN_SUPPORTED_VERSION = "0.4.11" # Standard JSON requires >= 0.4.11

os.makedirs(AST_DIR, exist_ok=True)

def find_pragma_version(code):
    match = re.search(r"pragma solidity\s+([^;]+);", code)
    if match:
        version_str = match.group(1).strip()
        # Clean common symbols
        clean_v = version_str.replace("^", "").replace(">=", "").replace("<", "").replace(">", "").replace("=", "").split()[0]
        return clean_v
    return None

def get_best_version(requested_version):
    """
    Maps requested version to the best available or installable version.
    Standard JSON interface (compile_standard) usually requires >= 0.4.11.
    """
    if not requested_version:
        return "0.4.25" # Default fallback
    
    # Handle very old versions by mapping to 0.4.11
    parts = requested_version.split('.')
    if len(parts) >= 3:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        if major == 0 and minor == 4 and patch < 11:
            logger.warning(f"Version {requested_version} is too old for Standard JSON. Falling back to {MIN_SUPPORTED_VERSION}")
            return MIN_SUPPORTED_VERSION
            
    return requested_version

def ensure_solc_version(version):
    """Ensures a specific solc version is installed, with fallback to installed versions."""
    installed = [str(v) for v in get_installed_solc_versions()]
    
    # 1. Try exact version if already installed
    if version in installed:
        set_solc_version(version)
        return True
    
    # 2. Try the closest installed version in the same minor range (e.g., 0.4.x)
    version_prefix = ".".join(version.split(".")[:2]) + "."
    compatible_installed = [v for v in installed if v.startswith(version_prefix)]
    if compatible_installed:
        # Use the highest installed version in that range
        best_fallback = sorted(compatible_installed, reverse=True)[0]
        logger.info(f"Version {version} not installed. Falling back to already installed compatible version: {best_fallback}")
        set_solc_version(best_fallback)
        return True

    # 3. Try to install the requested version
    try:
        logger.info(f"Installing solc {version}...")
        install_solc(version)
        set_solc_version(version)
        return True
    except Exception as e:
        logger.error(f"Failed to install solc {version}: {e}")
        # Final fallback to any 0.4.x if possible
        if version.startswith("0.4."):
            # Check if we can install a known stable one
            fallback = "0.4.25"
            try:
                logger.info(f"Attempting to install stable fallback {fallback}...")
                install_solc(fallback)
                set_solc_version(fallback)
                return True
            except:
                pass
        
        # Ultimate fallback: Use ANY installed version
        if installed:
            last_resort = installed[0]
            logger.warning(f"ULTIMATE FALLBACK: Using {last_resort} for version {version}")
            set_solc_version(last_resort)
            return True
            
        return False

def main():
    files = [f for f in os.listdir(CONTRACT_DIR) if f.endswith(".sol")]
    total = len(files)
    
    for i, file in enumerate(files):
        path = os.path.join(CONTRACT_DIR, file)
        outpath = os.path.join(AST_DIR, file.replace(".sol", ".json"))
        
        # Skip if already exists (optional, but good for resuming)
        if os.path.exists(outpath):
            # logger.info(f"[{i+1}/{total}] Skipping {file} (already exists)")
            # continue
            pass

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        requested_v = find_pragma_version(source)
        target_v = get_best_version(requested_v)

        try:
            if not ensure_solc_version(target_v):
                logger.error(f"[{i+1}/{total}] FAILED: Could not setup solc for {file} (v{target_v})")
                continue

            compiled = compile_standard({
                "language": "Solidity",
                "sources": {file: {"content": source}},
                "settings": {"outputSelection": {"*": {"": ["ast", "legacyAST"]}}}
            })
            
            # Check for errors in output
            if "errors" in compiled:
                errors = [e for e in compiled["errors"] if e["severity"] == "error"]
                if errors:
                    error_msgs = "\n".join([e.get("message", "Unknown error") for e in errors])
                    logger.error(f"[{i+1}/{total}] FAILED: Compilation errors in {file}:\n{error_msgs}")
                    continue

            # In older versions, it might be in 'legacyAST'
            source_data = compiled["sources"].get(file, {})
            ast = source_data.get("ast") or source_data.get("legacyAST")

            if not ast:
                logger.error(f"[{i+1}/{total}] FAILED: No AST found for {file}")
                continue

            with open(outpath, "w") as out:
                json.dump(ast, out)

            print(f"[OK] {file} (v{target_v})")

        except Exception as e:
            logger.error(f"[{i+1}/{total}] FAILED: {file} -> {e}")

if __name__ == "__main__":
    main()
