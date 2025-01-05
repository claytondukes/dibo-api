#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime

def load_json_file(file_path: str) -> Dict:
    """Load JSON file if it exists, otherwise return empty dict"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return {}

def extract_numeric_value(text: str) -> Optional[Tuple[float, str]]:
    """Extract numeric value and unit from text"""
    if not text:
        return None
    
    # Common patterns for numeric values
    patterns = [
        (r'(\d+(?:\.\d+)?)%', 'percentage'),  # 15.5%
        (r'(\d+(?:\.\d+)?) seconds', 'seconds'),  # 3.5 seconds
        (r'(\d+(?:\.\d+)?) damage', 'damage'),  # 150 damage
        (r'(\d+(?:\.\d+)?)', 'number')  # fallback for plain numbers
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1)), unit
    return None

def parse_condition(text: str) -> List[Dict[str, Any]]:
    """Parse effect conditions from text"""
    if not text:
        return []
    
    conditions = []
    
    # Trigger conditions
    trigger_patterns = {
        "on_hit": [
            r"when (?:you )?(?:are )?(?:get )?(?:getting )?hit",
            r"upon being hit",
            r"after taking damage",
            r"when (?:you )?take damage"
        ],
        "on_attack": [
            r"when (?:you )?attack",
            r"on hit",
            r"hitting enemies",
            r"your (?:attacks|primary attacks)"
        ],
        "on_kill": [
            r"when (?:you )?(?:defeat|kill)",
            r"after (?:defeating|killing)",
            r"on kill"
        ],
        "on_skill": [
            r"when (?:you )?(?:use|cast)",
            r"after using",
            r"on skill use",
            r"using a (?:skill|dash skill)"
        ]
    }
    
    # State conditions
    state_patterns = {
        "health_threshold": [
            r"(?:while |when |if )(?:you are )?at (?:full|low) (?:life|health)",
            r"above (\d+(?:\.\d+)?)% (?:life|health)",
            r"below (\d+(?:\.\d+)?)% (?:life|health)",
            r"while at (?:full|low) Life"
        ],
        "target_count": [
            r"(\d+) or more enemies",
            r"at least (\d+) enemies",
            r"(\d+) nearby enemies",
            r"all nearby enemies"
        ],
        "position": [
            r"(?:while |when )?behind",
            r"(?:while |when )?in front",
            r"from behind",
            r"(?:within|at) (\d+(?:\.\d+)?) yards"
        ],
        "stacks": [
            r"stacking up to (\d+(?:\.\d+)?) times",
            r"while at full stacks",
            r"at (\d+(?:\.\d+)?) stacks"
        ]
    }
    
    # Cooldown conditions
    cooldown_patterns = [
        r"Cannot (?:occur|trigger|affect|be affected) (?:more often than )?(?:once )?every (\d+(?:\.\d+)?) seconds",
        r"Cannot (?:occur|trigger|affect|be affected) (?:more often than )?(?:once )?every (\d+(?:\.\d+)?)s",
        r"cooldown(?: of)? (\d+(?:\.\d+)?) seconds",
        r"cooldown(?: of)? (\d+(?:\.\d+)?)s"
    ]
    
    # Target restrictions
    target_patterns = [
        r"(?:each|the same) (?:enemy|target) cannot .*? (?:more often than )?(?:once )?every (\d+(?:\.\d+)?) seconds",
        r"(?:each|the same) (?:enemy|target) cannot .*? (?:more often than )?(?:once )?every (\d+(?:\.\d+)?)s"
    ]
    
    # Check trigger conditions
    for trigger_type, patterns in trigger_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_text = match.group(0)
                conditions.append({
                    "type": "trigger",
                    "trigger": trigger_type,
                    "text": matched_text
                })
    
    # Check state conditions
    for state_type, patterns in state_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_text = match.group(0)
                condition = {
                    "type": "state",
                    "state": state_type,
                    "text": matched_text
                }
                # Add threshold value if present
                if match.groups():
                    condition["threshold"] = float(match.group(1))
                conditions.append(condition)
    
    # Check cooldown conditions
    for pattern in cooldown_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_text = match.group(0)
            conditions.append({
                "type": "cooldown",
                "cooldown": float(match.group(1)),
                "text": matched_text
            })
    
    # Check target restrictions
    for pattern in target_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_text = match.group(0)
            conditions.append({
                "type": "target_restriction",
                "cooldown": float(match.group(1)),
                "text": matched_text
            })
    
    return conditions

def extract_stat_value(text: str, stat_type: str) -> List[Dict]:
    """Extract stat values from effect text with improved numeric parsing"""
    values = []
    
    if not text:
        return values
    
    # Common patterns with value ranges
    patterns = {
        "critical_hit_chance": r"(?:Critical Hit Chance|critical hit chance|crit chance)(?:[^%\d]+)(\d+(?:\.\d+)?%)",
        "critical_hit_damage": r"(?:Critical Hit Damage|critical hit damage|crit damage)(?:[^%\d]+)(\d+(?:\.\d+)?%)",
        "damage_increase": [
            # Fixed damage increase
            r"(?:damage|Damage)(?: dealt| you deal| taken)?(?:[^%\d]+)(\d+(?:\.\d+)?%)",
            # Range based on condition
            r"(?:damage|Damage)(?: dealt| you deal| taken)?(?:[^%\d]+)up to (\d+(?:\.\d+)?%).*minimum (?:bonus is )?(\d+(?:\.\d+)?%)"
        ],
        "attack_speed": r"(?:Attack Speed|attack speed)(?:[^%\d]+)(\d+(?:\.\d+)?%)",
        "movement_speed": r"(?:Movement Speed|movement speed)(?:[^%\d]+)(\d+(?:\.\d+)?%)",
        "life": r"(?:maximum Life|Life|life)(?:[^%\d]+)(\d+(?:\.\d+)?%)"
    }
    
    if stat_type in patterns:
        pattern_list = patterns[stat_type] if isinstance(patterns[stat_type], list) else [patterns[stat_type]]
        for pattern in pattern_list:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conditions = parse_condition(text)
                value_data = {
                    "conditions": conditions
                }
                
                # Handle value ranges
                if len(match.groups()) > 1:  # Pattern with min/max values
                    max_val = extract_numeric_value(match.group(1))
                    min_val = extract_numeric_value(match.group(2))
                    if max_val and min_val:
                        value_data.update({
                            "max_value": max_val[0],
                            "min_value": min_val[0],
                            "unit": max_val[1],
                            "scaling": True
                        })
                else:  # Single fixed value
                    numeric_val = extract_numeric_value(match.group(1))
                    if numeric_val:
                        value_data.update({
                            "value": numeric_val[0],
                            "unit": numeric_val[1],
                            "scaling": False
                        })
                
                values.append(value_data)
    
    return values

def create_stat_indexes(gems_data: Dict, essences_data: Dict) -> Dict:
    """Create indexes based on stat boosts with value progression.
    
    Analyzes gems and essences for their stat boost effects, including:
    - Critical hit chance/damage
    - Damage increases (both flat and percentage)
    - Attack speed modifications
    - Movement speed changes
    - Life and survival stats
    
    Returns:
        Dict containing categorized stat boosts with their sources and values
    """
    stats = {
        "critical_hit_chance": {"gems": [], "essences": []},
        "critical_hit_damage": {"gems": [], "essences": []},
        "damage_increase": {"gems": [], "essences": []},
        "attack_speed": {"gems": [], "essences": []},
        "movement_speed": {"gems": [], "essences": []},
        "life": {"gems": [], "essences": []}
    }
    
    # Index gems
    for gem in gems_data.get("gems", []):
        name = gem["Name"]
        for stat_type in stats:
            # Check base effect
            base_values = extract_stat_value(gem["Base Effect"], stat_type)
            # Check rank 10 effect if available
            rank_10_values = []
            if gem["Rank 10 Effect"]:
                rank_10_values = extract_stat_value(gem["Rank 10 Effect"], stat_type)
            
            if base_values or rank_10_values:
                gem_entry = {
                    "name": name,
                    "stars": gem["Stars"],
                    "base_values": base_values,
                    "rank_10_values": rank_10_values,
                    "conditions": parse_condition(gem["Base Effect"])
                }
                if gem["Rank 10 Effect"]:
                    gem_entry["rank_10_conditions"] = parse_condition(gem["Rank 10 Effect"])
                stats[stat_type]["gems"].append(gem_entry)
    
    # Index essences
    for essence in essences_data.get("essences", []):
        name = essence["Essence Name"]
        effect = essence["Short Effect"]
        for stat_type in stats:
            values = extract_stat_value(effect, stat_type)
            if values:
                essence_entry = {
                    "name": name,
                    "slot": essence["Gear Slot"],
                    "values": values,
                    "conditions": parse_condition(effect)
                }
                stats[stat_type]["essences"].append(essence_entry)
    
    return stats

def create_effect_synergies(gems_data: Dict, essences_data: Dict) -> Dict:
    """Create indexes based on effect synergies with conditions"""
    synergies = {
        "critical_hit": {
            "gems": set(),
            "essences": set(),
            "skills": set(),
            "conditions": defaultdict(list)  # Track conditions by item
        },
        "movement_speed": {
            "gems": set(),
            "essences": set(),
            "skills": set(),
            "conditions": defaultdict(list)
        },
        "damage_boost": {
            "gems": set(),
            "essences": set(),
            "skills": set(),
            "conditions": defaultdict(list)
        },
        "control": {
            "gems": set(),
            "essences": set(),
            "skills": set(),
            "conditions": defaultdict(list)
        },
        "survival": {
            "gems": set(),
            "essences": set(),
            "skills": set(),
            "conditions": defaultdict(list)
        }
    }
    
    # Keywords for each synergy type
    keywords = {
        "critical_hit": ["critical", "crit"],
        "movement_speed": ["movement speed", "move speed"],
        "damage_boost": ["damage", "attack"],
        "control": ["stun", "slow", "freeze", "immobilize"],
        "survival": ["life", "healing", "shield", "absorb"]
    }
    
    # Index gems
    for gem in gems_data.get("gems", []):
        name = gem["Name"]
        effect_text = f"{gem['Base Effect'] or ''} {gem['Rank 10 Effect'] or ''}"
        conditions = parse_condition(effect_text)
        
        for synergy_type, words in keywords.items():
            if any(word in effect_text.lower() for word in words):
                synergies[synergy_type]["gems"].add(name)
                if conditions:
                    synergies[synergy_type]["conditions"][name].extend(conditions)
    
    # Index essences
    for essence in essences_data.get("essences", []):
        name = essence["Essence Name"]
        effect = essence["Short Effect"] or ""
        skill = essence["Modifies Skill"]
        essence_conditions = parse_condition(effect)
        
        for synergy_type, words in keywords.items():
            if any(word in effect.lower() for word in words):
                synergies[synergy_type]["essences"].add(name)
                synergies[synergy_type]["skills"].add(skill)
                if essence_conditions:
                    synergies[synergy_type]["conditions"][name].extend(essence_conditions)
    
    # Convert sets to sorted lists and defaultdict to dict
    for synergy_type in synergies:
        for category in ["gems", "essences", "skills"]:
            synergies[synergy_type][category] = sorted(synergies[synergy_type][category])
        synergies[synergy_type]["conditions"] = dict(synergies[synergy_type]["conditions"])
    
    return synergies

def create_build_templates() -> Dict:
    """Create build templates index organized by content type and purpose"""
    return {
        "pvp": {
            "burst_damage": {
                "name": "Burst Assassin",
                "primary_skills": ["Hammer of the Ancients", "Whirlwind"],
                "gem_setup": {
                    "required": {
                        "damage": ["Blood-Soaked Jade", "Chip of Stoned Flesh", "Power and Command"],
                        "defense": ["Blessing of the Worthy"]
                    },
                    "options": {
                        "budget": {
                            "damage": ["Berserker's Eye", "Pain of Subjugation", "Ca'arsen's Invigoration"],
                            "defense": ["The Black Rose"]
                        },
                        "premium": {
                            "damage": ["Bottled Hope", "Howler's Call"],
                            "defense": ["Phoenix Ashes"]
                        }
                    },
                    "notes": [
                        "BSJ can use Seeping Bile as aux for more DoT pressure",
                        "Phoenix Ashes works well as aux in Blessing slot for more survival"
                    ]
                },
                "recommended_essences": {
                    "primary": ["Davin's Legacy", "Rage of the Ancients"],
                    "alternatives": ["The Gathering", "Death Awaits"]
                },
                "playstyle_notes": [
                    "Focus on burst damage windows with HotA",
                    "Use Whirlwind for mobility and chip damage",
                    "Coordinate CC with team for maximum burst"
                ]
            },
            "control": {
                "name": "CC Controller",
                "primary_skills": ["Ground Stomp", "Sprint"],
                "gem_setup": {
                    "required": {
                        "control": ["Chip of Stoned Flesh", "Pain of Subjugation"],
                        "defense": ["Phoenix Ashes", "Blessing of the Worthy"]
                    },
                    "options": {
                        "budget": {
                            "control": ["The Black Rose", "Bloody Reach"],
                            "defense": ["Berserker's Eye"]
                        },
                        "premium": {
                            "control": ["Seeping Bile"],
                            "defense": ["Blood-Soaked Jade"]
                        }
                    },
                    "notes": [
                        "Use Chip of Stoned Flesh as aux for more CC",
                        "Phoenix Ashes works well as aux in Blessing slot for more survival"
                    ]
                },
                "recommended_essences": {
                    "primary": ["Broken Soul", "The Gathering"],
                    "alternatives": ["Pot Metal", "Spiritbreaker"]
                },
                "playstyle_notes": [
                    "Focus on setting up team fights with CC",
                    "Use mobility to stay safe while cooldowns refresh",
                    "Coordinate CC chains with team"
                ]
            }
        },
        "pve": {
            "speed_farm": {
                "name": "Speed Farmer",
                "primary_skills": ["Whirlwind", "Sprint"],
                "gem_setup": {
                    "required": {
                        "damage": ["Blood-Soaked Jade", "Seeping Bile"],
                        "utility": ["Bottled Hope"]
                    },
                    "options": {
                        "budget": {
                            "damage": ["Berserker's Eye", "Ca'arsen's Invigoration", "Power and Command"],
                            "utility": ["Everlasting Torment"]
                        },
                        "premium": {
                            "damage": ["Howler's Call"],
                            "utility": ["Phoenix Ashes"]
                        }
                    },
                    "notes": [
                        "Use Seeping Bile as aux for more DoT pressure",
                        "Phoenix Ashes works well as aux in Blessing slot for more survival"
                    ]
                },
                "recommended_essences": {
                    "primary": ["Ferocious Gale", "Hell's Legacy"],
                    "alternatives": ["Eager Maelstrom", "Routfinder"]
                },
                "playstyle_notes": [
                    "Maintain maximum movement speed",
                    "Group mobs efficiently",
                    "Skip elites unless they're directly in path"
                ]
            },
            "challenge_rift": {
                "name": "Rift Pusher",
                "primary_skills": ["Hammer of the Ancients", "Undying Rage"],
                "gem_setup": {
                    "required": {
                        "damage": ["Blood-Soaked Jade", "Chip of Stoned Flesh", "Power and Command"],
                        "defense": ["Phoenix Ashes"]
                    },
                    "options": {
                        "budget": {
                            "damage": ["Berserker's Eye", "Pain of Subjugation", "Lightning Core"],
                            "defense": ["The Black Rose"]
                        },
                        "premium": {
                            "damage": ["Bottled Hope", "Howler's Call"],
                            "defense": ["Blessing of the Worthy"]
                        }
                    },
                    "notes": [
                        "Use Chip of Stoned Flesh as aux for more CC",
                        "Phoenix Ashes works well as aux in Blessing slot for more survival"
                    ]
                },
                "recommended_essences": {
                    "primary": ["Davin's Legacy", "The Last Wail"],
                    "alternatives": ["Bonegyre", "The Remembered"]
                },
                "playstyle_notes": [
                    "Focus on elite packs for progress",
                    "Balance survival with damage output",
                    "Use terrain to group mobs"
                ]
            }
        }
    }

def create_gem_indexes(gems_data: Dict) -> Dict:
    """Create gem indexes with proper structure"""
    indexes = {}
    
    for gem in gems_data.get("gems", []):
        name = gem["Name"]
        indexes[name] = {
            "stars": int(gem["Stars"]),
            "base_effect": gem["Base Effect"],
            "rank_10_effect": gem["Rank 10 Effect"],
            "owned_rank": int(gem["Owned Rank"]) if gem.get("Owned Rank") else None,
            "quality": gem.get("Quality (if 5 star)")
        }
    
    return indexes

def create_essence_indexes(essences_data: Dict) -> Dict:
    indexed = {
        "by_name": {},
        "by_slot": {},
        "by_skill": {}
    }
    
    # Index each essence
    for essence in essences_data.get("essencelist", []):
        name = essence["Essence Name"]
        slot = essence["Gear Slot"]
        skill = essence["Modifies Skill"]
        
        # By name index
        indexed["by_name"][name] = essence
        
        # By slot index
        if slot not in indexed["by_slot"]:
            indexed["by_slot"][slot] = []
        indexed["by_slot"][slot].append(essence)
        
        # By skill index
        if skill not in indexed["by_skill"]:
            indexed["by_skill"][skill] = []
        indexed["by_skill"][skill].append(essence)
    
    return indexed

def create_cross_references(gems_data: Dict, essences_data: Dict) -> Dict[str, Any]:
    """Create cross-references between gems and essences"""
    cross_refs = {
        "gems_by_skill": defaultdict(list),
        "essences_by_skill": defaultdict(list),
        "synergies": defaultdict(list)
    }
    
    # Index essences by skill
    for essence in essences_data.get("essences", []):
        if "Skill" in essence and essence["Skill"]:
            skill = essence["Skill"].lower()
            cross_refs["essences_by_skill"][skill].append(essence)
    
    # Index gems by affected skills and find synergies
    for gem in gems_data.get("gems", []):
        if "Base Effect" in gem:
            effect = gem["Base Effect"].lower()
            skills_affected = extract_affected_skills(effect)
            
            for skill in skills_affected:
                cross_refs["gems_by_skill"][skill].append(gem)
                
                # Check for synergies with essences
                if skill in cross_refs["essences_by_skill"]:
                    for essence in cross_refs["essences_by_skill"][skill]:
                        synergy = {
                            "gem": gem["Name"],
                            "essence": essence["Name"],
                            "skill": skill,
                            "description": f"Both affect {skill}"
                        }
                        cross_refs["synergies"][skill].append(synergy)
    
    return cross_refs

def load_gem_ranks(file_path: str) -> Dict[str, Dict]:
    """Load and parse gem rank progression data from JSON"""
    json_file = Path(file_path)
    rank_data = {}
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        for gem in raw_data.get("gemranks", []):
            name = gem.get("Name", "")
            if not name:
                continue
                
            rank_data[name] = {
                "stars": int(gem.get("Star", 1)),
                "ranks": {},
                "magic_find": gem.get("Magic Find", "0").rstrip("%"),
                "max_effect": gem.get("Max", "")
            }
            
            # Process each rank
            for i in range(1, 11):
                rank_key = f"Rank {i}"
                if rank_key in gem and gem[rank_key]:
                    rank_data[name]["ranks"][str(i)] = gem[rank_key]
    
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: File not found or invalid JSON: {file_path}")
        print(f"Error: {str(e)}")
    
    return rank_data

def extract_rank_progression(text: str, rank: int, stars: int) -> Dict[str, Any]:
    """Extract rank-specific progression data from effect text"""
    progression = {
        "effects": [],
        "stats": defaultdict(list)
    }
    
    if not text:
        return progression
    
    # Extract all numeric values with their context
    value_patterns = [
        (r'(\d+(?:\.\d+)?)%.*damage', 'damage_increase'),
        (r'(\d+(?:\.\d+)?)%.*Critical Hit', 'critical_hit_chance'),
        (r'(\d+(?:\.\d+)?)%.*Life', 'life'),
        (r'(\d+(?:\.\d+)?)%.*Attack Speed', 'attack_speed'),
        (r'(\d+(?:\.\d+)?)%.*Movement Speed', 'movement_speed'),
        (r'(\d+(?:\.\d+)?)%.*healing', 'healing'),
        (r'(\d+(?:\.\d+)?)%.*duration', 'duration'),
        (r'(\d+(?:\.\d+)?)%.*cooldown', 'cooldown_reduction'),
        (r'(\d+(?:\.\d+)?)%.*chance', 'proc_chance')
    ]
    
    for pattern, stat_type in value_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            value = float(match.group(1))
            conditions = parse_condition(text)
            stat_entry = {
                "value": value,
                "conditions": conditions,
                "context": text[max(0, match.start()-20):min(len(text), match.end()+20)]
            }
            progression["stats"][stat_type].append(stat_entry)
    
    # Extract special effects (non-numeric bonuses)
    effect_patterns = [
        (r"(?:chance|probability) to .*?(?:\.|\n|$)", "proc_effect"),
        (r"(?:grants|gives|provides|gain) .*?(?:\.|\n|$)", "buff_effect"),
        (r"(?:summon|create|spawn|conjure) .*?(?:\.|\n|$)", "summon_effect"),
        (r"(?:shield|absorb|protect|reduce) .*?(?:\.|\n|$)", "defensive_effect"),
        (r"(?:explode|blast|burst|unleash) .*?(?:\.|\n|$)", "damage_effect"),
        (r"(?:stun|immobilize|freeze|chill|slow|blind) .*?(?:\.|\n|$)", "control_effect"),
        (r"(?:heal|restore|regenerate) .*?(?:\.|\n|$)", "healing_effect"),
        (r"increases? .*?(?:\.|\n|$)", "stat_effect")
    ]
    
    for pattern, effect_type in effect_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            effect_text = match.group(0).strip()
            if effect_text.endswith('.'):
                effect_text = effect_text[:-1]
            conditions = parse_condition(effect_text)
            
            # Don't add duplicate effects
            effect = {
                "type": effect_type,
                "text": effect_text,
                "conditions": conditions
            }
            if effect not in progression["effects"]:
                progression["effects"].append(effect)
    
    # If no effects were found but text exists, add it as a generic effect
    if not progression["effects"] and text:
        progression["effects"].append({
            "type": "generic_effect",
            "text": text.strip().rstrip('.'),
            "conditions": parse_condition(text)
        })
    
    return progression

def create_gem_progression_index(gems_data: Dict, rank_data: Dict) -> Dict[str, Any]:
    """Create detailed progression index for gems including rank data"""
    progression_index = {}
    
    # First process all rank data
    for gem_name, ranks in rank_data.items():
        if gem_name not in progression_index:
            progression_index[gem_name] = {
                "stars": str(ranks.get("stars", 1)),
                "ranks": {},
                "max_rank": 0,
                "magic_find": str(ranks.get("magic_find", "0")),
                "max_effect": ranks.get("max_effect", "")
            }
        
        # Process each rank's description
        for rank_num, description in ranks.get("ranks", {}).items():
            try:
                rank = int(rank_num)
            except (ValueError, TypeError):
                continue
                
            stars = ranks.get("stars", 1)
            
            # Update max rank if this is higher
            progression_index[gem_name]["max_rank"] = max(
                progression_index[gem_name]["max_rank"], 
                rank
            )
            
            # Extract rank progression data
            progression = extract_rank_progression(description, rank, stars)
            progression_index[gem_name]["ranks"][str(rank)] = progression
    
    # Then supplement with base gem data
    for gem in gems_data.get("gems", []):
        gem_name = gem.get("Name", "")
        if not gem_name:
            continue
            
        if gem_name not in progression_index:
            # Create new entry if gem wasn't in rank data
            stars = int(gem.get("Stars", 1))
            progression_index[gem_name] = {
                "stars": str(stars),
                "ranks": {},
                "max_rank": 10,  # Default max rank
                "magic_find": "0",  # Default magic find
                "max_effect": gem.get("Rank 10 Effect", "")
            }
        
        # Add base effect if rank 1 is missing or has no effects
        base_effect = gem.get("Base Effect", "")
        if base_effect:
            rank1 = progression_index[gem_name]["ranks"].get("1", {})
            if not rank1 or not rank1.get("effects"):
                stars = int(progression_index[gem_name]["stars"])
                progression = extract_rank_progression(base_effect, 1, stars)
                progression_index[gem_name]["ranks"]["1"] = progression
        
        # Add rank 10 effect if it exists and rank 10 is missing effects
        rank10_effect = gem.get("Rank 10 Effect", "")
        if rank10_effect:
            rank10 = progression_index[gem_name]["ranks"].get("10", {})
            if not rank10 or not rank10.get("effects"):
                stars = int(progression_index[gem_name]["stars"])
                progression = extract_rank_progression(rank10_effect, 10, stars)
                progression_index[gem_name]["ranks"]["10"] = progression
    
    return progression_index

def extract_affected_skills(text: str) -> Set[str]:
    """Extract affected skills from text"""
    skills = set()
    
    # Common skill keywords
    skill_keywords = {
        'primary attack', 'channeled', 'dash', 'ultimate',
        'summon', 'shield', 'buff', 'movement', 'attack'
    }
    
    text = text.lower()
    for keyword in skill_keywords:
        if keyword in text:
            skills.add(keyword)
    
    return skills

def create_player_resources(gems_data: Dict) -> Dict:
    """Create player resources section including all owned gem copies"""
    resources = {
        "owned_gems": {
            "5_star": [],
            "2_star": [],
            "1_star": []
        }
    }
    
    # Map stars to category
    star_category = {
        "5": "5_star",
        "2": "2_star",
        "1": "1_star"
    }
    
    for gem in gems_data.get("gems", []):
        if "Owned Rank" in gem:
            category = star_category.get(gem["Stars"])
            if category:
                resources["owned_gems"][category].append({
                    "name": gem["Name"],
                    "rank": int(gem["Owned Rank"]),
                    "quality": gem.get("Quality (if 5 star)")
                })
    
    return resources

def create_build_history() -> Dict:
    """Create initial build history structure"""
    return {
        "categories": {
            "farm": {"versions": []},
            "pvp": {"versions": []},
            "boss": {"versions": []},
            "challenge_rift": {"versions": []}
        }
    }

def create_metadata() -> Dict:
    """Create metadata section"""
    from datetime import datetime
    return {
        "last_updated": datetime.now().isoformat(),
        "version": "1.0",
        "data_structure_version": "1.0"
    }

def create_system_constraints() -> Dict:
    """Create system constraints for equipment validation"""
    return {
        "gem_slots": {
            "total_required": 8,
            "primary": {
                "required": 8,
                "unique": True,
                "star_ratings": [1, 2, 5]
            },
            "auxiliary": {
                "required": 0,
                "must_match_primary_stars": True,
                "unique": True
            }
        },
        "essence_slots": {
            "total_required": 8,
            "slots": {
                "Head": 1,
                "Shoulder": 1,
                "Chest": 1,
                "Legs": 1,
                "Primary weapon": 1,
                "Secondary weapon": 1,
                "Off-hand weapon": 1,
                "Off-hand secondary weapon": 1
            }
        },
        "set_slots": {
            "total_required": 8,
            "slots": {
                "Ring": 2,
                "Neck": 1,
                "Hands": 1,
                "Waist": 1,
                "Feet": 1,
                "Bracer": 2
            },
            "valid_combinations": [
                [6, 2],  # 6+2 pieces
                [4, 4],  # 4+4 pieces
                [4, 2, 2],  # 4+2+2 pieces
                [2, 2, 2, 2]  # 2+2+2+2 pieces
            ]
        },
        "skill_slots": {
            "total_required": 4,
            "slots": ["skill1", "skill2", "skill3", "skill4"],
            "available_skills": [
                "Hammer of the Ancients",
                "Cleave",
                "Whirlwind",
                "Sprint",
                "Wrath of the Berserker",
                "Undying Rage",
                "Ground Stomp",
                "Leap",
                "Furious Charge",
                "Chained Spear",
                "Demoralize",
                "Grab",
                "Sunder"
            ]
        },
        "weapon_slots": {
            "total_required": 1,
            "available_weapons": [
                "Frenzy",
                "Lacerate"
            ]
        }
    }

def validate_build(build: Dict) -> Tuple[bool, str]:
    """Validate a build against system constraints"""
    # Validate gems
    if len(build.get("gems", [])) != 8:
        return False, f"Build must have exactly 8 gems (has {len(build.get('gems', []))})"
    
    gem_names = [g["name"] for g in build.get("gems", [])]
    if len(gem_names) != len(set(gem_names)):
        return False, "Build contains duplicate gems"
    
    for gem in build.get("gems", []):
        if "auxiliary" in gem:
            primary_stars = next((g["stars"] for g in build["gems"] if g["name"] == gem["name"]), None)
            aux_stars = next((g["stars"] for g in build["gems"] if g["name"] == gem["auxiliary"]), None)
            if primary_stars != aux_stars:
                return False, f"Auxiliary gem {gem['auxiliary']} star rating does not match primary gem {gem['name']}"
    
    # Validate essences
    essences = build.get("essences", {})
    required_slots = ["Head", "Shoulder", "Chest", "Legs", "Primary weapon", 
                     "Secondary weapon", "Off-hand weapon", "Off-hand secondary weapon"]
    
    missing_slots = [slot for slot in required_slots if slot not in essences]
    if missing_slots:
        return False, f"Missing essences for slots: {', '.join(missing_slots)}"
    
    # Validate set items
    sets = build.get("sets", {})
    if not sets:
        return False, "Build must include set items"
    
    # Count set pieces
    set_counts = {}
    for piece in sets.values():
        set_name = piece["set"]
        set_counts[set_name] = set_counts.get(set_name, 0) + 1
    
    # Check if combination is valid
    counts = sorted(set_counts.values(), reverse=True)
    valid_combinations = [[6, 2], [4, 4], [4, 2, 2], [2, 2, 2, 2]]
    if counts not in valid_combinations:
        return False, f"Invalid set combination: {counts}. Must be one of: 6+2, 4+4, 4+2+2, or 2+2+2+2"
    
    return True, "Build is valid"

def add_build_to_history(category: str, build: Dict) -> Tuple[bool, str]:
    """Add a build to history after validation"""
    is_valid, message = validate_build(build)
    if not is_valid:
        return False, message
    
    # Get next version number
    versions = indexed_data["build_history"]["categories"][category]["versions"]
    next_version = len(versions) + 1
    
    # Add validated build
    build["version"] = next_version
    build["date_tested"] = datetime.now().isoformat()
    versions.append(build)
    
    return True, f"Added {category} build v{next_version}"

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)

def write_json_file(data: Dict, file_path: Path) -> None:
    """Write data to JSON file with proper formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_indexed_structure():
    """Create the new indexed directory structure"""
    base_dir = Path(__file__).parent.parent / "data/indexed"
    
    # Create required directories
    directories = [
        base_dir / "gems",
        base_dir / "essences",
        base_dir / "builds" / "categories",
        base_dir / "player",
        base_dir / "skills"
    ]
    for directory in directories:
        ensure_directory(directory)

def create_skill_indexes(skills_data: Dict) -> Dict:
    """Create indexes for skills with their base attributes and types"""
    skill_indexes = {
        "registry": {},
        "by_type": defaultdict(list),
        "by_cooldown": {
            "no_cooldown": [],
            "short": [],  # 0-10s
            "medium": [], # 11-20s
            "long": []    # >20s
        }
    }

    # Define valid skill types
    valid_types = {"damage", "buff", "control", "dash", "channel"}

    for skill in skills_data.get("skills", []):
        # Convert skill name to title case
        name = skill["name"].title()

        # Validate skill type
        base_type = skill["base_type"].lower()
        if base_type not in valid_types:
            continue

        # Create main registry entry
        skill_indexes["registry"][name] = {
            "base_type": base_type,
            "second_base_type": skill["second_base_type"].lower() if skill["second_base_type"] else None,
            "base_cooldown": skill["base_cooldown"],
            "description": skill["description"]
        }

        # Index by type
        skill_indexes["by_type"][base_type].append(name)

        # Index by cooldown - ensure cooldown is an integer
        try:
            cooldown = int(skill["base_cooldown"])
        except (ValueError, TypeError):
            cooldown = 0  # Default to no cooldown if invalid

        if cooldown == 0:
            skill_indexes["by_cooldown"]["no_cooldown"].append(name)
        elif cooldown <= 10:
            skill_indexes["by_cooldown"]["short"].append(name)
        elif cooldown <= 20:
            skill_indexes["by_cooldown"]["medium"].append(name)
        else:
            skill_indexes["by_cooldown"]["long"].append(name)

    return skill_indexes

def create_skill_modifiers(skills_data: Dict, essences_data: Dict, sets_data: Dict, gems_data: Dict, enchantments_data: Dict) -> Dict:
    """Create comprehensive mapping of all possible skill modifications"""
    # Get valid skill names for validation
    valid_skills = {skill["name"].title() for skill in skills_data.get("skills", [])}

    modifiers = {
        "by_skill": defaultdict(lambda: defaultdict(list)),
        "by_type": defaultdict(lambda: defaultdict(list)),
        "by_source": defaultdict(lambda: defaultdict(list))
    }

    # Track essence modifications (direct skill changes)
    for essence in essences_data.get("essences", []):
        if "skill" in essence:
            skill_name = essence["skill"].title()
            # Only process if it's a valid skill name
            if skill_name in valid_skills:
                modifiers["by_skill"][skill_name]["essences"].append({
                    "name": essence["name"],
                    "slot": essence.get("slot", "Unknown"),
                    "effect": essence["effect"]
                })
                modifiers["by_source"]["essences"][skill_name].append(essence["name"])

    # Track set bonuses (skill type modifications)
    for set_item in sets_data.get("sets", []):
        if "effect" in set_item:
            effect = set_item["effect"]
            # Check for skill type modifications
            skill_types = {
                "primary": ["Primary Attack", "Primary Attacks"],
                "channeled": ["channeled", "continual"],
                "movement": ["Movement Speed"],
                "summon": ["summons", "summoned"],
                "aoe": ["AoE", "area"]
            }

            for skill_type, keywords in skill_types.items():
                if any(keyword.lower() in effect.lower() for keyword in keywords):
                    modifiers["by_type"][skill_type]["sets"].append({
                        "set": set_item["name"],
                        "pieces": set_item["pieces"],
                        "effect": effect
                    })
                    modifiers["by_source"]["sets"][skill_type].append(set_item["name"])

    # Track gem effects (skill modifications)
    for gem in gems_data.get("gems", []):
        effects = [gem.get("base_effect", ""), gem.get("rank_10_effect", "")]

        for effect in effects:
            if not effect:
                continue

            # Check for skill-related modifications
            skill_keywords = {
                "primary": ["Primary Attack", "Primary Attacks"],
                "critical": ["Critical Hit"],
                "movement": ["Movement Speed"],
                "attack_speed": ["Attack Speed"],
                "beneficial": ["beneficial effects"]
            }

            for effect_type, keywords in skill_keywords.items():
                if any(keyword.lower() in effect.lower() for keyword in keywords):
                    modifiers["by_type"][effect_type]["gems"].append({
                        "gem": gem["name"],
                        "stars": gem.get("stars", 1),
                        "effect": effect
                    })
                    modifiers["by_source"]["gems"][effect_type].append(gem["name"])

    # Track enchantment modifications
    for enchant in enchantments_data.get("enchantments", []):
        if "effect" in enchant:
            effect = enchant["effect"]
            # Check for skill-related modifications
            skill_keywords = {
                "primary": ["Primary Attack", "Primary Attacks"],
                "critical": ["Critical Hit"],
                "movement": ["Movement Speed"],
                "attack_speed": ["Attack Speed"],
                "beneficial": ["beneficial effects"]
            }

            for effect_type, keywords in skill_keywords.items():
                if any(keyword.lower() in effect.lower() for keyword in keywords):
                    modifiers["by_type"][effect_type]["enchantments"].append({
                        "name": enchant["name"],
                        "effect": effect
                    })
                    modifiers["by_source"]["enchantments"][effect_type].append(enchant["name"])

    return modifiers

def create_skill_essence_mapping(skills_data: Dict, essences_data: Dict) -> Dict:
    """Create mapping between skills and their possible essence modifications"""
    mapping = defaultdict(list)
    
    for essence in essences_data.get("essencelist", []):
        if "Modifies Skill" in essence:
            skill_name = essence["Modifies Skill"].title()
            mapping[skill_name].append({
                "essence_name": essence["Essence Name"],
                "gear_slot": essence["Gear Slot"],
                "effect": essence["Short Effect"]
            })
    
    return dict(mapping)

def main():
    """Main function to create indexed data structure"""
    # Get project root directory (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    
    # Load raw data
    gems_data = load_json_file(project_root / "data/raw/Gems.json")
    essences_data = load_json_file(project_root / "data/raw/EssenceList.json")
    skills_data = load_json_file(project_root / "data/raw/Skills.json")
    sets_data = load_json_file(project_root / "data/raw/Sets.json")
    enchantments_data = load_json_file(project_root / "data/raw/Enchantments.json")
    curses_data = load_json_file(project_root / "data/raw/Curses.json")
    reforges_data = load_json_file(project_root / "data/raw/Reforges.json")
    
    # Load and process gem rank data
    rank_data = load_gem_ranks(project_root / "data/raw/GemRanks.json")
    
    # Create indexed directory structure
    create_indexed_structure()
    
    # Create indexes
    gem_indexes = create_gem_indexes(gems_data)
    essence_indexes = create_essence_indexes(essences_data)
    skill_indexes = create_skill_indexes(skills_data)
    stat_indexes = create_stat_indexes(gems_data, essences_data)
    synergy_indexes = create_effect_synergies(gems_data, essences_data)
    cross_references = create_cross_references(gems_data, essences_data)
    skill_modifiers = create_skill_modifiers(skills_data, essences_data, sets_data, gems_data, enchantments_data)
    skill_essence_map = create_skill_essence_mapping(skills_data, essences_data)
    gem_progression = create_gem_progression_index(gems_data, rank_data)
    player_resources = create_player_resources(gems_data)
    build_history = create_build_history()
    metadata = create_metadata()
    constraints = create_system_constraints()
    
    # Write indexed files
    base_dir = project_root / "data/indexed"
    
    write_json_file(gem_indexes, base_dir / "gems/registry.json")
    write_json_file(essence_indexes, base_dir / "essences/registry.json")
    write_json_file(skill_indexes, base_dir / "skills/registry.json")
    write_json_file(stat_indexes, base_dir / "gems/stat_boosts.json")
    write_json_file(synergy_indexes, base_dir / "gems/synergies.json")
    write_json_file(cross_references, base_dir / "cross_references.json")
    write_json_file(skill_modifiers, base_dir / "skills/modifiers.json")
    write_json_file(skill_essence_map, base_dir / "classes/barbarian/essences/skill_mapping.json")
    write_json_file(gem_progression, base_dir / "gems/progression.json")
    write_json_file(player_resources, base_dir / "player/resources.json")
    write_json_file(build_history, base_dir / "builds/history.json")
    write_json_file(metadata, base_dir / "metadata.json")
    write_json_file(constraints, base_dir / "constraints.json")

    print("Successfully created all indexed files")

if __name__ == '__main__':
    main()
