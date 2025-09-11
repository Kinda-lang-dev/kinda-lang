# kinda/grammar/constructs.py

import re

KindaPythonConstructs = {
    "kinda_int": {
        "type": "declaration",
        "pattern": re.compile(r"~kinda int (\w+)\s*[~=]+\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy integer declaration with personality-adjusted noise",
        "body": (
            "def kinda_int(val):\n"
            '    """Fuzzy integer with personality-adjusted fuzz and chaos tracking"""\n'
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] kinda int got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = random.randint(fuzz_min, fuzz_max)\n"
            "        result = int(val + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda int got kinda confused: {e}")\n'
            '        print(f"[tip] Just picking a random number instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.randint(0, 10)"
        ),
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r"~sorta print\s*\((.*)\)\s*(?:;|$)"),
        "description": "Print with personality-adjusted probability",
        "body": (
            "def sorta_print(*args):\n"
            '    """Sorta prints with personality-adjusted probability and chaos tracking"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if not args:\n"
            "            prob = chaos_probability('sorta_print')\n"
            "            if random.random() < prob:\n"
            "                print('[shrug] Nothing to print, I guess?')\n"
            "            update_chaos_state(failed=False)\n"
            "            return\n"
            "        \n"
            "        prob = chaos_probability('sorta_print')\n"
            "        if random.random() < prob:\n"
            "            print('[print]', *args)\n"
            "            update_chaos_state(failed=False)\n"
            "        else:\n"
            '            # Add some personality to the "shrug" responses\n'
            "            shrug_responses = [\n"
            "                '[shrug] Meh...',\n"
            "                '[shrug] Not feeling it right now',\n"
            "                '[shrug] Maybe later?',\n"
            "                '[shrug] *waves hand dismissively*',\n"
            "                '[shrug] Kinda busy'\n"
            "            ]\n"
            "            response = random.choice(shrug_responses)\n"
            "            print(response, *args)\n"
            "            update_chaos_state(failed=True)\n"
            "    except Exception as e:\n"
            "        print(f'[error] Sorta print kinda broke: {e}')\n"
            "        print('[fallback]', *args)\n"
            "        update_chaos_state(failed=True)"
        ),
    },
    "sometimes": {
        "type": "conditional",
        "pattern": re.compile(r"~sometimes\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with personality-adjusted probability",
        "body": (
            "def sometimes(condition=True):\n"
            '    """Sometimes evaluates a condition with personality-adjusted probability"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Sometimes got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('sometimes', condition)\n"
            "        result = random.random() < prob and bool(condition)\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Sometimes got confused: {e}")\n'
            '        print("[tip] Flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "maybe": {
        "type": "conditional",
        "pattern": re.compile(r"~maybe\s*\(([^)]*)\)\s*\{?"),
        "description": "Fuzzy conditional trigger with personality-adjusted probability",
        "body": (
            "def maybe(condition=True):\n"
            '    """Maybe evaluates a condition with personality-adjusted probability"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        if condition is None:\n"
            '            print("[?] Maybe got None as condition - treating as False")\n'
            "            update_chaos_state(failed=True)\n"
            "            return False\n"
            "        \n"
            "        prob = chaos_probability('maybe', condition)\n"
            "        result = random.random() < prob and bool(condition)\n"
            "        update_chaos_state(failed=not result)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Maybe couldn\'t decide: {e}")\n'
            '        print("[tip] Defaulting to random choice")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "fuzzy_reassign": {
        "type": "reassignment",
        "pattern": re.compile(r"(\w+)\s*~=\s*([^#;]+?)(?:\s*#.*)?(?:;|$)"),
        "description": "Fuzzy reassignment with personality-adjusted noise",
        "body": (
            "def fuzzy_assign(var_name, value):\n"
            '    """Fuzzy assignment with personality-adjusted fuzz and chaos tracking"""\n'
            "    from kinda.personality import chaos_fuzz_range, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Check if value is numeric\n"
            "        if not isinstance(value, (int, float)):\n"
            "            try:\n"
            "                value = float(value)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] fuzzy assignment got something weird: {repr(value)}")\n'
            '                print(f"[tip] Expected a number but got {type(value).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.randint(0, 10)\n"
            "        \n"
            "        fuzz_min, fuzz_max = chaos_fuzz_range('int')\n"
            "        fuzz = random.randint(fuzz_min, fuzz_max)\n"
            "        result = int(value + fuzz)\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Fuzzy assignment kinda failed: {e}")\n'
            '        print(f"[tip] Returning a random number because why not?")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.randint(0, 10)"
        ),
    },
    "kinda_binary": {
        "type": "declaration",
        "pattern": re.compile(
            r"~kinda\s+binary\s+(\w+)(?:\s*~\s*probabilities\s*\(([^)]+)\))?(?:;|$)"
        ),
        "description": "Three-state binary with personality-adjusted probabilities",
        "body": (
            "def kinda_binary(pos_prob=None, neg_prob=None, neutral_prob=None):\n"
            '    """Returns 1 (positive), -1 (negative), or 0 (neutral) with personality-adjusted probabilities."""\n'
            "    from kinda.personality import chaos_binary_probabilities, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted probabilities if not specified\n"
            "        if pos_prob is None or neg_prob is None or neutral_prob is None:\n"
            "            pos_prob, neg_prob, neutral_prob = chaos_binary_probabilities()\n"
            "        \n"
            "        # Validate probabilities\n"
            "        total_prob = pos_prob + neg_prob + neutral_prob\n"
            "        if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors\n"
            '            print(f"[?] Binary probabilities don\'t add up to 1.0 (got {total_prob:.3f})")\n'
            '            print(f"[tip] Normalizing: pos={pos_prob:.3f}, neg={neg_prob:.3f}, neutral={neutral_prob:.3f}")\n'
            "            # Normalize probabilities\n"
            "            pos_prob /= total_prob\n"
            "            neg_prob /= total_prob\n"
            "            neutral_prob /= total_prob\n"
            "        \n"
            "        rand = random.random()\n"
            "        if rand < pos_prob:\n"
            "            result = 1\n"
            "        elif rand < pos_prob + neg_prob:\n"
            "            result = -1\n"
            "        else:\n"
            "            result = 0\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Binary choice kinda broke: {e}")\n'
            '        print(f"[tip] Defaulting to random choice between -1, 0, 1")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([-1, 0, 1])"
        ),
    },
    "ish_value": {
        "type": "value",
        "pattern": re.compile(r"(\d+(?:\.\d+)?)~ish"),
        "description": "Fuzzy value with personality-adjusted variance",
        "body": (
            "def ish_value(val, variance=None):\n"
            '    """Create a fuzzy value with personality-adjusted variance"""\n'
            "    from kinda.personality import chaos_variance, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted variance if not specified\n"
            "        if variance is None:\n"
            "            variance = chaos_variance()\n"
            "        \n"
            "        # Convert to float for processing\n"
            "        if not isinstance(val, (int, float)):\n"
            "            try:\n"
            "                val = float(val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish value got something weird: {repr(val)}")\n'
            '                print(f"[tip] Expected a number but got {type(val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.uniform(-variance, variance)\n"
            "        \n"
            "        # Generate fuzzy variance\n"
            "        fuzz = random.uniform(-variance, variance)\n"
            "        result = val + fuzz\n"
            "        update_chaos_state(failed=False)\n"
            "        \n"
            "        # Return integer if input was integer, float otherwise\n"
            "        return int(result) if isinstance(val, int) else result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Ish value kinda confused: {e}")\n'
            '        print(f"[tip] Returning random value with variance +/-{variance}")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.uniform(-variance, variance)"
        ),
    },
    "ish_comparison": {
        "type": "comparison",
        "pattern": re.compile(r"(\w+)\s*~ish\s*([^#;\s]+)"),
        "description": "Fuzzy comparison with personality-adjusted tolerance",
        "body": (
            "def ish_comparison(left_val, right_val, tolerance=None):\n"
            '    """Check if values are approximately equal within personality-adjusted tolerance"""\n'
            "    from kinda.personality import chaos_tolerance, update_chaos_state\n"
            "    import random\n"
            "    try:\n"
            "        # Use personality-adjusted tolerance if not specified\n"
            "        if tolerance is None:\n"
            "            tolerance = chaos_tolerance()\n"
            "        \n"
            "        # Convert both values to numeric\n"
            "        if not isinstance(left_val, (int, float)):\n"
            "            try:\n"
            "                left_val = float(left_val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish comparison got weird left value: {repr(left_val)}")\n'
            '                print(f"[tip] Expected a number but got {type(left_val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        if not isinstance(right_val, (int, float)):\n"
            "            try:\n"
            "                right_val = float(right_val)\n"
            "            except (ValueError, TypeError):\n"
            '                print(f"[?] ish comparison got weird right value: {repr(right_val)}")\n'
            '                print(f"[tip] Expected a number but got {type(right_val).__name__}")\n'
            "                update_chaos_state(failed=True)\n"
            "                return random.choice([True, False])\n"
            "        \n"
            "        # Check if values are within tolerance\n"
            "        difference = abs(left_val - right_val)\n"
            "        result = difference <= tolerance\n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Ish comparison kinda broke: {e}")\n'
            '        print(f"[tip] Flipping a coin instead")\n'
            "        update_chaos_state(failed=True)\n"
            "        return random.choice([True, False])"
        ),
    },
    "welp": {
        "type": "fallback",
        "pattern": re.compile(r"(.+)\s*~welp\s*(.+)"),
        "description": "Graceful fallback with personality-aware error messages",
        "body": (
            "def welp_fallback(primary_expr, fallback_value):\n"
            '    """Execute primary expression with graceful fallback and chaos tracking"""\n'
            "    from kinda.personality import update_chaos_state, get_personality\n"
            "    try:\n"
            "        # If primary_expr is a callable, call it\n"
            "        if callable(primary_expr):\n"
            "            result = primary_expr()\n"
            "        else:\n"
            "            result = primary_expr\n"
            "        \n"
            "        # Return fallback if result is None or falsy (but not 0 or False explicitly)\n"
            "        if result is None:\n"
            "            # Get personality-appropriate error message style\n"
            "            personality = get_personality()\n"
            "            style = personality.get_error_message_style()\n"
            "            \n"
            "            if style == 'professional':\n"
            '                print(f"[welp] Expression returned None, using fallback: {repr(fallback_value)}")\n'
            "            elif style == 'friendly':\n"
            '                print(f"[welp] Got nothing there, trying fallback: {repr(fallback_value)}")\n'
            "            elif style == 'snarky':\n"
            '                print(f"[welp] Well that was useless, falling back to: {repr(fallback_value)}")\n'
            "            else:  # chaotic\n"
            '                print(f"[welp] *shrugs* That didn\'t work, whatever: {repr(fallback_value)}")\n'
            "            \n"
            "            update_chaos_state(failed=True)\n"
            "            return fallback_value\n"
            "        \n"
            "        update_chaos_state(failed=False)\n"
            "        return result\n"
            "    except Exception as e:\n"
            "        # Get personality-appropriate error message style\n"
            "        personality = get_personality()\n"
            "        style = personality.get_error_message_style()\n"
            "        \n"
            "        if style == 'professional':\n"
            '            print(f"[welp] Operation failed ({type(e).__name__}: {e}), using fallback: {repr(fallback_value)}")\n'
            "        elif style == 'friendly':\n"
            '            print(f"[welp] Oops, that didn\'t work ({e}), trying: {repr(fallback_value)}")\n'
            "        elif style == 'snarky':\n"
            '            print(f"[welp] Predictably failed with {type(e).__name__}, fine: {repr(fallback_value)}")\n'
            "        else:  # chaotic\n"
            '            print(f"[welp] BOOM! {e} 💥 Whatever, here\'s: {repr(fallback_value)}")\n'
            "        \n"
            "        update_chaos_state(failed=True)\n"
            "        return fallback_value"
        ),
    },
    "kinda_import": {
        "type": "import",
        "pattern": re.compile(
            r"~kinda import\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)(?:\s+as\s+([a-zA-Z_]\w*))?(?:\s*#.*)?(?:;|$)"
        ),
        "description": "Fuzzy import with personality-adjusted behavior and optional aliasing",
        "body": (
            "def kinda_import(module_name, alias=None, success_probability=None, fallback_strategy='graceful'):\n"
            '    """Fuzzy import with personality-adjusted success rates and chaos tracking"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, get_personality\n"
            "    import random\n"
            "    import sys\n"
            "    import importlib\n"
            "    try:\n"
            "        # Use personality-adjusted import success probability\n"
            "        if success_probability is None:\n"
            "            success_probability = chaos_probability('kinda_import')\n"
            "        \n"
            "        # Fuzzy import behavior - sometimes imports might 'kinda' work\n"
            "        if random.random() < success_probability:\n"
            "            try:\n"
            "                module = importlib.import_module(module_name)\n"
            "                update_chaos_state(failed=False)\n"
            "                return module\n"
            "            except ImportError as e:\n"
            "                # Even when trying to import, sometimes it might kinda work\n"
            "                personality = get_personality()\n"
            "                style = personality.get_error_message_style()\n"
            "                \n"
            "                if style == 'professional':\n"
            "                    print(f\"[kinda import] Module '{module_name}' not found: {e}\")\n"
            "                elif style == 'friendly':\n"
            "                    print(f\"[kinda import] Couldn't find '{module_name}', that's okay though!\")\n"
            "                elif style == 'snarky':\n"
            "                    print(f\"[kinda import] '{module_name}' doesn't exist, shocking.\")\n"
            "                else:  # chaotic\n"
            "                    print(f\"[kinda import] '{module_name}' went poof! 💨\")\n"
            "                \n"
            "                if fallback_strategy == 'graceful':\n"
            "                    # Create a mock module that kinda works\n"
            "                    class KindaMockModule:\n"
            "                        def __init__(self, name):\n"
            "                            self.__name__ = name\n"
            "                        def __getattr__(self, attr):\n"
            "                            def kinda_function(*args, **kwargs):\n"
            '                                print(f"[kinda] Called {attr} from mock {self.__name__}")\n'
            "                                return None\n"
            "                            return kinda_function\n"
            "                    \n"
            "                    mock_module = KindaMockModule(module_name)\n"
            "                    update_chaos_state(failed=True)\n"
            "                    return mock_module\n"
            "                else:\n"
            "                    update_chaos_state(failed=True)\n"
            "                    raise\n"
            "        else:\n"
            "            # Sometimes imports just don't happen\n"
            "            personality = get_personality()\n"
            "            style = personality.get_error_message_style()\n"
            "            \n"
            "            if style == 'professional':\n"
            "                print(f\"[kinda import] Skipping import of '{module_name}' (probabilistic behavior)\")\n"
            "            elif style == 'friendly':\n"
            "                print(f\"[kinda import] Not really feeling like importing '{module_name}' right now\")\n"
            "            elif style == 'snarky':\n"
            "                print(f\"[kinda import] Nah, '{module_name}' can wait\")\n"
            "            else:  # chaotic\n"
            "                print(f\"[kinda import] '{module_name}'? Maybe later! 🤷\")\n"
            "            \n"
            "            # Return a mock module for graceful fallback\n"
            "            class KindaMockModule:\n"
            "                def __init__(self, name):\n"
            "                    self.__name__ = name\n"
            "                def __getattr__(self, attr):\n"
            "                    def kinda_function(*args, **kwargs):\n"
            '                        print(f"[kinda] Called {attr} from mock {self.__name__}")\n'
            "                        return None\n"
            "                    return kinda_function\n"
            "            \n"
            "            mock_module = KindaMockModule(module_name)\n"
            "            update_chaos_state(failed=True)\n"
            "            return mock_module\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Kinda import got confused: {e}")\n'
            '        print(f"[tip] Creating a mock module instead")\n'
            "        \n"
            "        class KindaMockModule:\n"
            "            def __init__(self, name):\n"
            "                self.__name__ = name\n"
            "            def __getattr__(self, attr):\n"
            "                def kinda_function(*args, **kwargs):\n"
            '                    print(f"[kinda] Called {attr} from mock {self.__name__}")\n'
            "                    return None\n"
            "                return kinda_function\n"
            "        \n"
            "        mock_module = KindaMockModule(module_name)\n"
            "        update_chaos_state(failed=True)\n"
            "        return mock_module"
        ),
    },
    "maybe_import": {
        "type": "import",
        "pattern": re.compile(
            r"~maybe import\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)(?:\s+as\s+([a-zA-Z_]\w*))?(?:\s*~welp\s+(.+?))?(?:\s*#.*)?(?:;|$)"
        ),
        "description": "Conditional import with graceful fallback using ~welp syntax",
        "body": (
            "def maybe_import(module_name, alias=None, fallback_module=None):\n"
            '    """Maybe import with graceful fallback and chaos tracking"""\n'
            "    from kinda.personality import chaos_probability, update_chaos_state, get_personality\n"
            "    import random\n"
            "    import sys\n"
            "    import importlib\n"
            "    try:\n"
            "        # Use personality-adjusted maybe probability\n"
            "        maybe_probability = chaos_probability('maybe_import')\n"
            "        \n"
            "        if random.random() < maybe_probability:\n"
            "            try:\n"
            "                module = importlib.import_module(module_name)\n"
            "                update_chaos_state(failed=False)\n"
            "                return module\n"
            "            except ImportError as e:\n"
            "                # Import failed, try fallback\n"
            "                personality = get_personality()\n"
            "                style = personality.get_error_message_style()\n"
            "                \n"
            "                if style == 'professional':\n"
            "                    print(f\"[maybe import] Module '{module_name}' not available: {e}\")\n"
            "                elif style == 'friendly':\n"
            "                    print(f\"[maybe import] Can't find '{module_name}', trying fallback...\")\n"
            "                elif style == 'snarky':\n"
            "                    print(f\"[maybe import] '{module_name}' failed, obviously\")\n"
            "                else:  # chaotic\n"
            "                    print(f\"[maybe import] '{module_name}' went missing! 🕵️\")\n"
            "                \n"
            "                if fallback_module:\n"
            "                    try:\n"
            "                        fallback = importlib.import_module(fallback_module)\n"
            '                        print(f"[maybe import] Using fallback: {fallback_module}")\n'
            "                        update_chaos_state(failed=False)\n"
            "                        return fallback\n"
            "                    except ImportError:\n"
            "                        print(f\"[maybe import] Fallback '{fallback_module}' also failed\")\n"
            "                \n"
            "                # Create graceful mock if no fallback works\n"
            "                class MaybeMockModule:\n"
            "                    def __init__(self, name):\n"
            "                        self.__name__ = name\n"
            "                    def __getattr__(self, attr):\n"
            "                        def maybe_function(*args, **kwargs):\n"
            '                            print(f"[maybe] Called {attr} from mock {self.__name__}")\n'
            "                            return None\n"
            "                        return maybe_function\n"
            "                \n"
            "                mock_module = MaybeMockModule(module_name)\n"
            "                update_chaos_state(failed=True)\n"
            "                return mock_module\n"
            "        else:\n"
            "            # Maybe decided not to import\n"
            "            personality = get_personality()\n"
            "            style = personality.get_error_message_style()\n"
            "            \n"
            "            if style == 'professional':\n"
            "                print(f\"[maybe import] Skipping '{module_name}' import (probabilistic decision)\")\n"
            "            elif style == 'friendly':\n"
            "                print(f\"[maybe import] Maybe later for '{module_name}'?\")\n"
            "            elif style == 'snarky':\n"
            "                print(f\"[maybe import] '{module_name}'? Nah, not today\")\n"
            "            else:  # chaotic\n"
            "                print(f\"[maybe import] '{module_name}'? Maybe not! 🤷‍♀️\")\n"
            "            \n"
            "            # Use fallback if available\n"
            "            if fallback_module:\n"
            "                try:\n"
            "                    fallback = importlib.import_module(fallback_module)\n"
            '                    print(f"[maybe import] Using fallback: {fallback_module}")\n'
            "                    update_chaos_state(failed=False)\n"
            "                    return fallback\n"
            "                except ImportError:\n"
            "                    print(f\"[maybe import] Fallback '{fallback_module}' also failed\")\n"
            "            \n"
            "            # Create graceful mock\n"
            "            class MaybeMockModule:\n"
            "                def __init__(self, name):\n"
            "                    self.__name__ = name\n"
            "                def __getattr__(self, attr):\n"
            "                    def maybe_function(*args, **kwargs):\n"
            '                        print(f"[maybe] Called {attr} from mock {self.__name__}")\n'
            "                        return None\n"
            "                    return maybe_function\n"
            "            \n"
            "            mock_module = MaybeMockModule(module_name)\n"
            "            update_chaos_state(failed=True)\n"
            "            return mock_module\n"
            "    except Exception as e:\n"
            '        print(f"[shrug] Maybe import got confused: {e}")\n'
            '        print(f"[tip] Creating a mock module instead")\n'
            "        \n"
            "        class MaybeMockModule:\n"
            "            def __init__(self, name):\n"
            "                self.__name__ = name\n"
            "            def __getattr__(self, attr):\n"
            "                def maybe_function(*args, **kwargs):\n"
            '                    print(f"[maybe] Called {attr} from mock {self.__name__}")\n'
            "                    return None\n"
            "                return maybe_function\n"
            "        \n"
            "        mock_module = MaybeMockModule(module_name)\n"
            "        update_chaos_state(failed=True)\n"
            "        return mock_module"
        ),
    },
}
