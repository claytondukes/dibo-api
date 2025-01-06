# Diablo Immortal Player Inventory System

This directory contains the JSON schema for tracking your Diablo Immortal inventory, builds, and equipped items. These files are designed to be stored in your GitHub Gists for easy access and updating.

## Files

### `profile.json`
Contains your player information and currently equipped items:
- Player details (battle.net ID, class, paragon level)
- Primary gear:
  - Head, Shoulders, Chest, Legs
  - Main Hand and Off-Hand (both weapon sets)
  - Legendary essences
  - Legendary gem slots
- Set items:
  - Neck, Waist, Hands, Feet
  - Rings (2 slots)
  - Bracers (2 slots)
  - Normal gem sockets

### `gems.json`
Tracks all legendary gems you own:
- Organized by gem name
- Each gem can have multiple copies at different:
  - Ranks (1-10)
  - Quality levels (2-5/5 for 5★ gems)
  - Auxiliary (Aux) status

### `sets.json`
Lists all set items in your inventory:
- Organized by set name
- Each item includes:
  - Slot type
  - Attributes (strength, fortitude, willpower)
  - Socket count (2-3 per item)
  - Combat rating

### `builds.json`
Stores your saved builds:
- Each build has a name and complete equipment loadout
- References items from your inventory
- Tracks both gear and set items

## Setting Up Your Inventory

1. Create a new GitHub Gist at https://gist.github.com/
2. Create four files with the exact names: `profile.json`, `gems.json`, `sets.json`, and `builds.json`
3. Copy the contents of each file from this directory into your corresponding gist files
4. Update the contents to match your actual inventory:
   - Set your player info in `profile.json`
   - List your legendary gems in `gems.json`
   - Add your set items to `sets.json`
   - Create your builds in `builds.json`

## File Format Guidelines

1. Each file must be valid JSON
2. Keep the version and last_updated fields current
3. Follow the exact structure shown in the example files
4. For equipped items:
   - Legendary gems go in essence slots
   - Normal gems (ruby, sapphire, etc.) go in set item sockets
5. Set items always have 2-3 sockets when equipped

## Example Usage

```json
// profile.json - Example of equipped items
{
  "equipped": {
    "gear": {
      "chest": {
        "essence": null,
        "gem": {
          "name": "Blessing of the Worthy",
          "rank": 10,
          "quality": 5
        }
      }
    },
    "sets": {
      "neck": {
        "item": "Awakener's Urge",
        "sockets": 2
      }
    }
  }
}
```

## Updating Your Inventory

1. Edit the appropriate gist file when you:
   - Get new items
   - Upgrade gems
   - Change equipped items
   - Create new builds
2. Always update the `last_updated` timestamp
3. Increment the `version` if you make structural changes

## Need Help?

If you need help setting up or maintaining your inventory files, feel free to:
1. Check the example files in this directory
2. Open an issue in the main repository
3. Ask for help in our Discord community
