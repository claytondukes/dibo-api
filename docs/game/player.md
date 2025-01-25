# Diablo Immortal Player Data Guide

This guide explains how to store your Diablo Immortal character data in a GitHub
Gist. The API can use this data to provide personalized recommendations and
analysis, but all files are completely optional. The API will work with or
without your personal data.

## Using the API

The API works in two modes:

1. **Generic Mode** (No personal data)
   - Suggests optimal builds considering all possible:
     - Legendary essences
     - Legendary gems
     - Set items
     - Skill combinations
   - Recommendations based on general meta and synergies

2. **Personalized Mode** (With your gist data)
   - Tailors suggestions to your:
     - Available gems
     - Collected set items
     - Preferred playstyles (from your saved builds)
     - Character level and progress

## Setting Up Your Data (Optional)

If you want personalized recommendations:

1. Create a new [GitHub Gist](https://gist.github.com)

2. Create any of these files in your gist:
   - `profile.json`: Your character information
   - `builds.json`: Your saved builds
   - `gems.json`: Your legendary gem inventory
   - `sets.json`: Your set item inventory

3. Copy the examples below and replace the values with your actual character data

4. When you log into the API, it will query your gist directly to access your
   character information

## Optional Data Files

You can create any of these JSON files in your gist. Each file helps the API
provide more personalized recommendations:

### 1. profile.json

Completly optional and not even used yet in the api. Just here for possible future use.

```json
{
  "version": "1.0.0",
  "battle_net_id": "example#1234",
  "character_class": "barbarian",
  "paragon": 675,
  "server": "us"
}
```

Fields:

- `battle_net_id`: Your Battle.net ID with discriminator
- `character_class`: Your character's class (barbarian, etc.)
- `paragon`: Your current paragon level
- `server`: Your game server (us, eu, etc.)

### 2. builds.json

Your saved character builds. Each time you save a build, the API will update your gist.

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2025-01-25T11:17:44-05:00"
  },
  "builds": {
    "pvp": {
      "BG Stomp LR": {
        "gear": {
          "primary_weapon": {
            "essence": "Krubask's Fury",
            "gem": {
              "name": "Blood-Soaked Jade",
              "rank": 10,
              "quality": 5
            }
          },
          "secondary_weapon": {
            "essence": "Shackled Fate",
            "gem": {
              "name": "Frozen Heart",
              "rank": 10,
              "quality": 5
            }
          },
          "offhand": {
            "essence": "Loathsome Lamina",
            "gem": {
              "name": "Seeping Bile",
              "rank": 8,
              "quality": 5
            }
          },
          "offhand_secondary": {
            "essence": "Pit Lord's Aspect",
            "gem": {
              "name": "Starfire Shard",
              "rank": 7,
              "quality": 5
            }
          },
          "head": {
            "essence": "Rending Bite",
            "gem": {
              "name": "Pain Clasp",
              "rank": 10,
              "quality": 2
            }
          },
          "shoulders": {
            "essence": "Roar of Persuasion",
            "gem": {
              "name": "Mother's Lament",
              "rank": 10,
              "quality": 2
            }
          },
          "chest": {
            "essence": "Ardent Fervor",
            "gem": {
              "name": "Bottled Hope",
              "rank": 8,
              "quality": 5
            }
          },
          "legs": {
            "essence": "Thunder Strike",
            "gem": {
              "name": "Roiling Consequence",
              "rank": 5,
              "quality": 5
            }
          }
        },
        "sets": {
          "neck": {
            "item": "Awakener's Call"
          },
          "waist": {
            "item": "Mountebank's Bravado"
          },
          "hands": {
            "item": "Mountebank's Shirking"
          },
          "feet": {
            "item": "Beacon's Urge"
          },
          "ring_1": {
            "item": "Mountebank's Misdirection"
          },
          "ring_2": {
            "item": "Mountebank's Marvel"
          },
          "bracer_1": {
            "item": "Dreamer's Urge"
          },
          "bracer_2": {
            "item": "Failure's Urge"
          }
        }
      }
    },
    "raid": {
      "sample name": {}
    }
  }
}
```

### 3. gems.json

Your legendary gem collection. If provided, the API will prioritize builds that
use gems you already own. Without this file, the API will consider all possible
gem combinations. Duplicate gems are allowed.

```json
{
  "version": "1.0",
  "last_updated": "2025-01-05T11:51:33-05:00",
  "gems": {
    "Berserker's Eye": [{
      "owned_rank": 10,
      "owned_quality": 1
    }],
    "Blessed Pebble": [{
      "owned_rank": 10,
      "owned_quality": 1
    }],
    "Blessing of the Worthy": [{
      "owned_rank": 10,
      "owned_quality": 5
    }, {
      "owned_rank": 4,
      "owned_quality": 2
    }, {
      "owned_rank": 3,
      "owned_quality": 2
    }]
  }
}
```

### 4. sets.json

Your set item inventory. If provided, the API can suggest builds that maximize
your existing set bonuses.

>TODO: implement magic affixes and gem slots
>TODO: consider attributes when generating builds, e.g.: high fortitude, high willpower, etc.

```json
{
  "version": "1.0",
  "last_updated": "2025-01-05T11:34:02-05:00",
  "sets": {
    "Grace of the Flagellant": [
      {
        "attributes": {
          "strength": 642,
          "fortitude": 641,
          "willpower": 641
        }
      }
    ],
    "Vithu's Urges": [
      {
        "attributes": {
          "strength": 620,
          "fortitude": 625,
          "willpower": 622
        }
      }
    ]
  }
}
