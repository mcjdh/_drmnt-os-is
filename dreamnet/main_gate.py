#!/usr/bin/env python3
"""
DreamNet Main Gate - Interactive orchestration system for the DreamNet prototype

This main gate provides:
- Interactive menu system without soft locks
- Unified access to all DreamNet functionality
- Performance optimization through caching
- Batch processing capabilities
- Error handling and graceful exits
"""

import json
import subprocess
import sys
import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import hashlib


class PerformanceCache:
    """Performance optimization through intelligent caching"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'configurations_cached': 0
        }
    
    def _get_cache_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            # Sort dictionary for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def get_config(self, config_path: Path) -> Optional[Dict]:
        """Get cached configuration or load and cache it"""
        cache_key = self._get_cache_key(str(config_path))
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            self.cache_stats['hits'] += 1
            return self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.memory_cache[cache_key] = config
                self.cache_stats['hits'] += 1
                return config
            except Exception:
                pass  # Fall through to reload
        
        # Load and cache configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Cache in memory and file
            self.memory_cache[cache_key] = config
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.cache_stats['misses'] += 1
            self.cache_stats['configurations_cached'] += 1
            return config
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return None
    
    def invalidate_cache(self, config_path: Path = None):
        """Invalidate cache for specific config or all"""
        if config_path:
            cache_key = self._get_cache_key(str(config_path))
            self.memory_cache.pop(cache_key, None)
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all cache
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
    
    def get_stats(self) -> Dict:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests
        }


class MainGate:
    """Main orchestration system for DreamNet"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.cache_dir = self.script_dir / ".cache"
        self.performance_cache = PerformanceCache(self.cache_dir)
        
        self.config_cache = {}
        self.session_stats = {
            'dreams_generated': 0,
            'themes_explored': set(),
            'session_start': datetime.now(),
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.running = True
        
        # Available brain configurations
        self.brain_configs = self._discover_brain_configs()
        
        # Performance optimization settings
        self.batch_size = 5  # Process in batches to prevent overwhelming
        self.timeout_settings = {
            'dream_generation': 120,
            'ollama_call': 60,
            'user_input': 30
        }
        
    def _discover_brain_configs(self) -> Dict[str, Path]:
        """Discover all available brain configuration files"""
        brain_files = {}
        for file_path in self.script_dir.glob("brain*.json"):
            name = file_path.stem
            brain_files[name] = file_path
        return brain_files
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display the main header"""
        print("=" * 70)
        print("🌙 DREAMNET MAIN GATE - Mystical Symbol Generation System 🌙")
        print("=" * 70)
        print(f"Session Time: {(datetime.now() - self.session_stats['session_start']).seconds}s")
        print(f"Dreams Generated: {self.session_stats['dreams_generated']}")
        print(f"Themes Explored: {len(self.session_stats['themes_explored'])}")
        print("=" * 70)
    
    def display_main_menu(self):
        """Display the main menu options"""
        print("\n🎛️  MAIN MENU:")
        print("1. 🔮 Generate Single Dream (Original Engine)")
        print("2. ⚡ Generate Single Dream (V2 Engine)")
        print("3. 🌊 Basic Batch Generation")
        print("4. 🚀 Optimized Batch Generation")
        print("5. 🧠 Brain Configuration Manager")
        print("6. 🎨 Theme Explorer")
        print("7. 📊 Session Statistics")
        print("8. 🔧 System Configuration")
        print("9. 📖 Help & Documentation")
        print("0. 🚪 Exit DreamNet")
        print("\n" + "─" * 50)
    
    def get_user_input(self, prompt: str, valid_options: List[str] = None, timeout: int = 30) -> Optional[str]:
        """Get user input with validation and timeout protection"""
        try:
            print(f"{prompt}")
            if valid_options:
                print(f"Valid options: {', '.join(valid_options)}")
            
            # Simple input without timeout for now to avoid complexity
            user_input = input("► ").strip()
            
            if valid_options and user_input not in valid_options:
                print(f"❌ Invalid option. Please choose from: {', '.join(valid_options)}")
                return None
            
            return user_input
            
        except KeyboardInterrupt:
            print("\n\n🌟 Graceful exit requested. Returning to main menu...")
            return None
        except EOFError:
            print("\n\n🌟 End of input detected. Returning to main menu...")
            return None
    
    def generate_dream(self, engine: str = "original") -> bool:
        """Generate a single dream using specified engine"""
        try:
            dream_script = "dream.py" if engine == "original" else "dream_v2.py"
            script_path = self.script_dir / dream_script
            
            print(f"\n🔮 Invoking {engine} dream engine...")
            print("─" * 30)
            
            # Run the dream script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=False,  # Show real-time output
                cwd=str(self.script_dir),
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                self.session_stats['dreams_generated'] += 1
                print("─" * 30)
                print("✅ Dream generation completed successfully!")
                return True
            else:
                print("❌ Dream generation failed!")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Dream generation timed out!")
            return False
        except Exception as e:
            print(f"❌ Error during dream generation: {e}")
            return False
    
    def batch_dream_generation(self):
        """Basic batch dream generation with multiple configurations"""
        print("\n🌊 BASIC BATCH GENERATION")
        print("=" * 40)
        
        if not self.brain_configs:
            print("❌ No brain configurations found!")
            input("Press Enter to continue...")
            return
        
        print("Available brain configurations:")
        config_list = list(self.brain_configs.keys())
        for i, config in enumerate(config_list, 1):
            print(f"{i}. {config}")
        print(f"{len(config_list) + 1}. All configurations")
        
        choice = self.get_user_input(
            "Select configuration(s) for batch generation:",
            [str(i) for i in range(1, len(config_list) + 2)]
        )
        
        if not choice:
            return
        
        # Backup current brain.json
        original_brain = self.script_dir / "brain.json"
        backup_brain = self.script_dir / "brain_backup.json"
        
        if original_brain.exists():
            shutil.copy(original_brain, backup_brain)
        
        try:
            if int(choice) == len(config_list) + 1:
                # Run all configurations
                configs_to_run = config_list
            else:
                # Run selected configuration
                configs_to_run = [config_list[int(choice) - 1]]
            
            engine_choice = self.get_user_input(
                "Select engine (1=Original, 2=V2):",
                ["1", "2"]
            )
            
            if not engine_choice:
                return
            
            engine = "original" if engine_choice == "1" else "v2"
            
            print(f"\n🚀 Starting basic batch generation with {len(configs_to_run)} configurations...")
            
            for config_name in configs_to_run:
                print(f"\n🔄 Processing: {config_name}")
                
                # Copy brain config (skip if it's the same file)
                config_path = self.brain_configs[config_name]
                if config_path != original_brain:
                    shutil.copy(config_path, original_brain)
                
                # Generate dream
                success = self.generate_dream(engine)
                
                if success:
                    print(f"✅ Completed: {config_name}")
                else:
                    print(f"❌ Failed: {config_name}")
                
                time.sleep(1)  # Brief pause between generations
            
            print(f"\n🌟 Basic batch generation complete!")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
        finally:
            # Restore original brain.json
            if backup_brain.exists():
                if backup_brain != original_brain:  # Safety check
                    shutil.move(backup_brain, original_brain)
                else:
                    backup_brain.unlink()  # Remove if same file
            
        input("Press Enter to continue...")
    
    def optimized_batch_generation(self):
        """Optimized batch dream generation with performance monitoring"""
        print("\n🚀 OPTIMIZED BATCH GENERATION")
        print("=" * 40)
        
        if not self.brain_configs:
            print("❌ No brain configurations found!")
            input("Press Enter to continue...")
            return
        
        print("Available brain configurations:")
        config_list = list(self.brain_configs.keys())
        for i, config in enumerate(config_list, 1):
            print(f"{i}. {config}")
        print(f"{len(config_list) + 1}. All configurations")
        print(f"{len(config_list) + 2}. Custom batch size")
        
        choice = self.get_user_input(
            "Select configuration(s) for batch generation:",
            [str(i) for i in range(1, len(config_list) + 3)]
        )
        
        if not choice:
            return
        
        # Determine configurations to run
        if int(choice) == len(config_list) + 1:
            configs_to_run = config_list
        elif int(choice) == len(config_list) + 2:
            # Custom batch processing
            batch_size = self.get_user_input("Enter batch size (1-10):")
            try:
                batch_size = max(1, min(10, int(batch_size)))
                configs_to_run = config_list[:batch_size]
                print(f"Processing first {batch_size} configurations...")
            except (ValueError, TypeError):
                print("❌ Invalid batch size, using default.")
                configs_to_run = config_list[:self.batch_size]
        else:
            configs_to_run = [config_list[int(choice) - 1]]
        
        # Select engine
        engine_choice = self.get_user_input(
            "Select engine (1=Original, 2=V2, 3=Both):",
            ["1", "2", "3"]
        )
        
        if not engine_choice:
            return
        
        engines = []
        if engine_choice == "1":
            engines = ["original"]
        elif engine_choice == "2":
            engines = ["v2"]
        else:
            engines = ["original", "v2"]
        
        # Performance monitoring
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        # Backup current brain.json
        original_brain = self.script_dir / "brain.json"
        backup_brain = self.script_dir / "brain_backup.json"
        
        if original_brain.exists():
            shutil.copy(original_brain, backup_brain)
        
        try:
            total_operations = len(configs_to_run) * len(engines)
            print(f"\n🚀 Starting optimized batch generation...")
            print(f"📊 Configurations: {len(configs_to_run)}")
            print(f"🔧 Engines: {len(engines)}")
            print(f"⚙️  Total Operations: {total_operations}")
            print("─" * 50)
            
            operation_count = 0
            
            for config_name in configs_to_run:
                print(f"\n📁 Configuration: {config_name}")
                
                # Load config with caching
                config_path = self.brain_configs[config_name]
                config_data = self.performance_cache.get_config(config_path)
                
                if not config_data:
                    print(f"❌ Failed to load configuration: {config_name}")
                    error_count += 1
                    continue
                
                # Copy brain config (skip if it's the same file)
                if config_path != original_brain:
                    try:
                        shutil.copy(config_path, original_brain)
                    except Exception as e:
                        print(f"❌ Error copying config: {e}")
                        error_count += 1
                        continue
                
                # Run with each engine
                for engine in engines:
                    operation_count += 1
                    print(f"🔄 [{operation_count}/{total_operations}] {config_name} -> {engine}")
                    
                    try:
                        success = self.generate_dream(engine)
                        
                        if success:
                            success_count += 1
                            print(f"✅ Completed: {config_name} ({engine})")
                        else:
                            error_count += 1
                            print(f"❌ Failed: {config_name} ({engine})")
                        
                        # Brief pause to prevent overwhelming
                        if operation_count < total_operations:
                            time.sleep(0.5)
                            
                    except Exception as e:
                        error_count += 1
                        print(f"❌ Error in {config_name} ({engine}): {e}")
            
            # Performance summary
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🌟 BATCH GENERATION COMPLETE")
            print("═" * 40)
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"✅ Successful: {success_count}")
            print(f"❌ Failed: {error_count}")
            print(f"📈 Success Rate: {(success_count / total_operations * 100):.1f}%")
            
            # Update session stats
            self.session_stats['dreams_generated'] += success_count
            
            # Cache performance
            cache_stats = self.performance_cache.get_stats()
            print(f"🎯 Cache Hit Rate: {cache_stats['hit_rate']}")
            
        except Exception as e:
            print(f"❌ Batch generation error: {e}")
        finally:
            # Restore original brain.json
            if backup_brain.exists():
                if backup_brain != original_brain:  # Safety check
                    shutil.move(backup_brain, original_brain)
                else:
                    backup_brain.unlink()  # Remove if same file
        
        input("\nPress Enter to continue...")
    
    def brain_configuration_manager(self):
        """Manage brain configurations"""
        while True:
            print("\n🧠 BRAIN CONFIGURATION MANAGER")
            print("=" * 40)
            
            if not self.brain_configs:
                print("❌ No brain configurations found!")
            else:
                print("Available configurations:")
                for i, (name, path) in enumerate(self.brain_configs.items(), 1):
                    print(f"{i}. {name} ({path.name})")
            
            print("\nOptions:")
            print("1. Create new brain configuration")
            print("2. Edit existing configuration")
            print("3. Set active configuration")
            print("4. Delete configuration")
            print("5. Return to main menu")
            
            choice = self.get_user_input(
                "Select option:",
                ["1", "2", "3", "4", "5"]
            )
            
            if not choice:
                continue
            
            if choice == "1":
                self._create_brain_config()
            elif choice == "2":
                self._edit_brain_config()
            elif choice == "3":
                self._set_active_config()
            elif choice == "4":
                self._delete_brain_config()
            elif choice == "5":
                break
    
    def _create_brain_config(self):
        """Create a new brain configuration"""
        print("\n📝 CREATE NEW BRAIN CONFIGURATION")
        print("─" * 35)
        
        name = input("Configuration name: ").strip()
        if not name:
            print("❌ Name cannot be empty!")
            return
        
        # Sanitize filename
        filename = f"brain_{name.lower().replace(' ', '_')}.json"
        config_path = self.script_dir / filename
        
        if config_path.exists():
            print(f"❌ Configuration '{filename}' already exists!")
            return
        
        print("\nEnter the dream parameters:")
        intent = input("Intent: ").strip()
        style = input("Style: ").strip()
        
        if not intent or not style:
            print("❌ Both intent and style are required!")
            return
        
        config_data = {
            "intent": intent,
            "style": style
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            self.brain_configs[name] = config_path
            print(f"✅ Configuration saved as {filename}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def _edit_brain_config(self):
        """Edit an existing brain configuration"""
        if not self.brain_configs:
            print("❌ No configurations to edit!")
            return
        
        print("\n✏️  EDIT BRAIN CONFIGURATION")
        print("─" * 30)
        
        config_list = list(self.brain_configs.items())
        for i, (name, path) in enumerate(config_list, 1):
            print(f"{i}. {name}")
        
        choice = self.get_user_input(
            "Select configuration to edit:",
            [str(i) for i in range(1, len(config_list) + 1)]
        )
        
        if not choice:
            return
        
        try:
            name, config_path = config_list[int(choice) - 1]
            
            # Load current configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            print(f"\nEditing: {name}")
            print(f"Current intent: {config_data.get('intent', '')}")
            print(f"Current style: {config_data.get('style', '')}")
            
            new_intent = input("New intent (or press Enter to keep current): ").strip()
            new_style = input("New style (or press Enter to keep current): ").strip()
            
            if new_intent:
                config_data['intent'] = new_intent
            if new_style:
                config_data['style'] = new_style
            
            # Save updated configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            print("✅ Configuration updated!")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
        except Exception as e:
            print(f"❌ Error editing configuration: {e}")
    
    def _set_active_config(self):
        """Set the active brain configuration"""
        if not self.brain_configs:
            print("❌ No configurations available!")
            return
        
        print("\n🎯 SET ACTIVE CONFIGURATION")
        print("─" * 30)
        
        config_list = list(self.brain_configs.items())
        for i, (name, path) in enumerate(config_list, 1):
            print(f"{i}. {name}")
        
        choice = self.get_user_input(
            "Select configuration to activate:",
            [str(i) for i in range(1, len(config_list) + 1)]
        )
        
        if not choice:
            return
        
        try:
            name, config_path = config_list[int(choice) - 1]
            brain_file = self.script_dir / "brain.json"
            
            # Copy selected config to brain.json
            shutil.copy(config_path, brain_file)
            print(f"✅ Activated configuration: {name}")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
        except Exception as e:
            print(f"❌ Error activating configuration: {e}")
    
    def _delete_brain_config(self):
        """Delete a brain configuration"""
        if not self.brain_configs:
            print("❌ No configurations to delete!")
            return
        
        print("\n🗑️  DELETE BRAIN CONFIGURATION")
        print("─" * 30)
        
        config_list = list(self.brain_configs.items())
        for i, (name, path) in enumerate(config_list, 1):
            print(f"{i}. {name}")
        
        choice = self.get_user_input(
            "Select configuration to delete:",
            [str(i) for i in range(1, len(config_list) + 1)]
        )
        
        if not choice:
            return
        
        try:
            name, config_path = config_list[int(choice) - 1]
            
            confirm = self.get_user_input(
                f"Are you sure you want to delete '{name}'? (y/n):",
                ["y", "Y", "n", "N"]
            )
            
            if confirm and confirm.lower() == 'y':
                config_path.unlink()
                del self.brain_configs[name]
                print(f"✅ Deleted configuration: {name}")
            else:
                print("❌ Deletion cancelled.")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
        except Exception as e:
            print(f"❌ Error deleting configuration: {e}")
    
    def theme_explorer(self):
        """Explore available themes and their characteristics"""
        print("\n🎨 THEME EXPLORER")
        print("=" * 30)
        
        # Try to load config.json for theme information
        config_path = self.script_dir / "config.json"
        
        if not config_path.exists():
            print("❌ config.json not found! Theme information unavailable.")
            input("Press Enter to continue...")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            themes = config.get('themes', {})
            
            if not themes:
                print("❌ No themes found in configuration!")
                input("Press Enter to continue...")
                return
            
            print("Available themes:")
            print("─" * 20)
            
            for theme_name, theme_data in themes.items():
                print(f"\n🎭 {theme_name.upper()}")
                print(f"   Keywords: {', '.join(theme_data.get('keywords', []))}")
                print(f"   Symbols: {', '.join(theme_data.get('symbols', []))}")
                print(f"   Colors: {', '.join(theme_data.get('colors', []))}")
                
                # Track explored themes
                self.session_stats['themes_explored'].add(theme_name)
            
            print(f"\n🌟 Total themes available: {len(themes)}")
            
        except Exception as e:
            print(f"❌ Error loading theme information: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_session_stats(self):
        """Display current session statistics"""
        print("\n📊 SESSION STATISTICS")
        print("=" * 30)
        
        duration = datetime.now() - self.session_stats['session_start']
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"Session Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"Dreams Generated: {self.session_stats['dreams_generated']}")
        print(f"Themes Explored: {len(self.session_stats['themes_explored'])}")
        
        if self.session_stats['themes_explored']:
            print(f"Explored Themes: {', '.join(self.session_stats['themes_explored'])}")
        
        # Check for generated files
        echo_files = len(list(self.script_dir.glob("echoes/*.md")))
        log_files = len(list(self.script_dir.glob("logs/*.log")))
        
        print(f"Echo Files Created: {echo_files}")
        print(f"Log Files Created: {log_files}")
        
        # Performance cache statistics
        print("\n🎯 PERFORMANCE STATISTICS:")
        print("─" * 25)
        cache_stats = self.performance_cache.get_stats()
        print(f"Cache Hit Rate: {cache_stats['hit_rate']}")
        print(f"Cache Hits: {cache_stats['hits']}")
        print(f"Cache Misses: {cache_stats['misses']}")
        print(f"Configurations Cached: {cache_stats['configurations_cached']}")
        
        # Brain configurations discovered
        print(f"\n🧠 Brain Configurations: {len(self.brain_configs)}")
        for name in self.brain_configs.keys():
            print(f"   • {name}")
        
        input("\nPress Enter to continue...")
    
    def system_configuration(self):
        """Display and modify system configuration"""
        print("\n🔧 SYSTEM CONFIGURATION")
        print("=" * 30)
        
        print("1. View current configuration")
        print("2. Check system dependencies")
        print("3. Performance cache management")
        print("4. Clear session data")
        print("5. System optimization settings")
        print("6. Return to main menu")
        
        choice = self.get_user_input(
            "Select option:",
            ["1", "2", "3", "4", "5", "6"]
        )
        
        if not choice:
            return
        
        if choice == "1":
            self._view_configuration()
        elif choice == "2":
            self._check_dependencies()
        elif choice == "3":
            self._cache_management()
        elif choice == "4":
            self._clear_session_data()
        elif choice == "5":
            self._optimization_settings()
        elif choice == "6":
            return
    
    def _view_configuration(self):
        """View current system configuration"""
        config_path = self.script_dir / "config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                print("\n📋 Current Configuration:")
                print("─" * 25)
                print(json.dumps(config, indent=2))
                
            except Exception as e:
                print(f"❌ Error reading configuration: {e}")
        else:
            print("❌ config.json not found!")
        
        input("\nPress Enter to continue...")
    
    def _check_dependencies(self):
        """Check system dependencies"""
        print("\n🔍 DEPENDENCY CHECK")
        print("─" * 20)
        
        # Check Python version
        python_version = sys.version.split()[0]
        print(f"Python Version: {python_version} ✅")
        
        # Check for Ollama
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"Ollama: Available ✅")
            else:
                print(f"Ollama: Not responding ❌")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"Ollama: Not installed ❌")
        
        # Check required files
        required_files = ["dream.py", "dream_v2.py", "config.json"]
        for file_name in required_files:
            file_path = self.script_dir / file_name
            status = "✅" if file_path.exists() else "❌"
            print(f"{file_name}: {status}")
        
        input("\nPress Enter to continue...")
    
    def _clear_session_data(self):
        """Clear session data and temporary files"""
        confirm = self.get_user_input(
            "Clear all logs and echo files? (y/n):",
            ["y", "Y", "n", "N"]
        )
        
        if confirm and confirm.lower() == 'y':
            try:
                # Clear logs
                logs_dir = self.script_dir / "logs"
                if logs_dir.exists():
                    for log_file in logs_dir.glob("*.log"):
                        log_file.unlink()
                
                # Clear echoes
                echoes_dir = self.script_dir / "echoes"
                if echoes_dir.exists():
                    for echo_file in echoes_dir.glob("*.md"):
                        echo_file.unlink()
                
                # Reset session stats
                self.session_stats['dreams_generated'] = 0
                self.session_stats['themes_explored'].clear()
                
                print("✅ Session data cleared!")
                
            except Exception as e:
                print(f"❌ Error clearing data: {e}")
        else:
            print("❌ Operation cancelled.")
        
        input("Press Enter to continue...")
    
    def display_help(self):
        """Display help and documentation"""
        print("\n📖 DREAMNET HELP & DOCUMENTATION")
        print("=" * 40)
        
        help_text = """
🌙 DREAMNET OVERVIEW:
DreamNet is a mystical symbol generation system that transforms
intentions into symbolic wisdom using AI and algorithmic processes.

🎛️  MAIN FEATURES:
• Dream Generation: Create symbolic content from intentions
• Dual Engines: Original (hardcoded) and V2 (configuration-driven)
• Batch Processing: Generate multiple dreams efficiently
• Theme System: Explore different symbolic themes
• Configuration Management: Create and manage dream parameters

🔮 HOW TO USE:
1. Set up your brain configuration (intent + style)
2. Choose an engine (Original or V2)
3. Generate dreams and explore the symbolic output
4. Review echoes and logs for patterns and insights

⚠️  REQUIREMENTS:
• Python 3.7+
• Ollama (optional, fallback system available)
• JSON configuration files

🆘 TROUBLESHOOTING:
• Use Ctrl+C to exit any stuck process
• All menus have clear exit options
• Check dependencies in System Configuration
• Session data can be cleared if needed

📁 FILE STRUCTURE:
• brain*.json - Dream configurations
• config.json - System configuration
• echoes/ - Thematic collections
• logs/ - Session histories
• output.json - Latest result
        """
        
        print(help_text)
        input("\nPress Enter to continue...")
    
    def _cache_management(self):
        """Manage performance cache"""
        print("\n🎯 CACHE MANAGEMENT")
        print("─" * 20)
        
        cache_stats = self.performance_cache.get_stats()
        print(f"Cache Status:")
        print(f"• Hit Rate: {cache_stats['hit_rate']}")
        print(f"• Total Hits: {cache_stats['hits']}")
        print(f"• Total Misses: {cache_stats['misses']}")
        print(f"• Configurations Cached: {cache_stats['configurations_cached']}")
        
        cache_size = len(list(self.cache_dir.glob("*.json"))) if self.cache_dir.exists() else 0
        print(f"• Cache Files: {cache_size}")
        
        print("\nOptions:")
        print("1. Clear cache")
        print("2. Rebuild cache")
        print("3. Return")
        
        choice = self.get_user_input("Select option:", ["1", "2", "3"])
        
        if choice == "1":
            confirm = self.get_user_input("Clear all cache? (y/n):", ["y", "Y", "n", "N"])
            if confirm and confirm.lower() == 'y':
                self.performance_cache.invalidate_cache()
                print("✅ Cache cleared!")
            else:
                print("❌ Operation cancelled.")
        elif choice == "2":
            print("🔄 Rebuilding cache...")
            self.performance_cache.invalidate_cache()
            # Reload all configurations to rebuild cache
            for config_path in self.brain_configs.values():
                self.performance_cache.get_config(config_path)
            print("✅ Cache rebuilt!")
        
        input("\nPress Enter to continue...")
    
    def _optimization_settings(self):
        """Configure system optimization settings"""
        print("\n⚙️  OPTIMIZATION SETTINGS")
        print("─" * 25)
        
        print(f"Current Settings:")
        print(f"• Batch Size: {self.batch_size}")
        print(f"• Dream Generation Timeout: {self.timeout_settings['dream_generation']}s")
        print(f"• Ollama Call Timeout: {self.timeout_settings['ollama_call']}s")
        print(f"• User Input Timeout: {self.timeout_settings['user_input']}s")
        
        print("\nOptions:")
        print("1. Adjust batch size")
        print("2. Adjust timeouts")
        print("3. Reset to defaults")
        print("4. Return")
        
        choice = self.get_user_input("Select option:", ["1", "2", "3", "4"])
        
        if choice == "1":
            new_size = self.get_user_input("Enter new batch size (1-20):")
            try:
                new_size = max(1, min(20, int(new_size)))
                self.batch_size = new_size
                print(f"✅ Batch size set to {new_size}")
            except (ValueError, TypeError):
                print("❌ Invalid batch size!")
        
        elif choice == "2":
            print("Timeout Settings:")
            print("1. Dream Generation (current: {}s)".format(self.timeout_settings['dream_generation']))
            print("2. Ollama Call (current: {}s)".format(self.timeout_settings['ollama_call']))
            print("3. User Input (current: {}s)".format(self.timeout_settings['user_input']))
            
            timeout_choice = self.get_user_input("Select timeout to adjust:", ["1", "2", "3"])
            if timeout_choice:
                new_timeout = self.get_user_input("Enter new timeout (10-300 seconds):")
                try:
                    new_timeout = max(10, min(300, int(new_timeout)))
                    if timeout_choice == "1":
                        self.timeout_settings['dream_generation'] = new_timeout
                    elif timeout_choice == "2":
                        self.timeout_settings['ollama_call'] = new_timeout
                    elif timeout_choice == "3":
                        self.timeout_settings['user_input'] = new_timeout
                    print(f"✅ Timeout updated to {new_timeout}s")
                except (ValueError, TypeError):
                    print("❌ Invalid timeout value!")
        
        elif choice == "3":
            self.batch_size = 5
            self.timeout_settings = {
                'dream_generation': 120,
                'ollama_call': 60,
                'user_input': 30
            }
            print("✅ Settings reset to defaults!")
        
        input("\nPress Enter to continue...")
    
    def handle_exit(self):
        """Handle graceful system exit"""
        print("\n🌟 DREAMNET SHUTDOWN SEQUENCE")
        print("=" * 35)
        
        duration = datetime.now() - self.session_stats['session_start']
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"Session Summary:")
        print(f"• Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"• Dreams Generated: {self.session_stats['dreams_generated']}")
        print(f"• Themes Explored: {len(self.session_stats['themes_explored'])}")
        
        print("\n🙏 Thank you for exploring the symbolic realms.")
        print("🌙 Until the next awakening...")
        
        self.running = False
    
    def run(self):
        """Main application loop"""
        try:
            while self.running:
                self.clear_screen()
                self.display_header()
                self.display_main_menu()
                
                choice = self.get_user_input(
                    "Select option:",
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
                )
                
                if not choice:
                    continue
                
                if choice == "1":
                    self.generate_dream("original")
                    input("\nPress Enter to continue...")
                elif choice == "2":
                    self.generate_dream("v2")
                    input("\nPress Enter to continue...")
                elif choice == "3":
                    self.batch_dream_generation()
                elif choice == "4":
                    self.optimized_batch_generation()
                elif choice == "5":
                    self.brain_configuration_manager()
                elif choice == "6":
                    self.theme_explorer()
                elif choice == "7":
                    self.display_session_stats()
                elif choice == "8":
                    self.system_configuration()
                elif choice == "9":
                    self.display_help()
                elif choice == "0":
                    self.handle_exit()
                
        except KeyboardInterrupt:
            print("\n\n🌟 Graceful exit requested...")
            self.handle_exit()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("🔄 Returning to main menu...")
            input("Press Enter to continue...")


def main():
    """Main entry point"""
    gate = MainGate()
    gate.run()


if __name__ == "__main__":
    main()