
# Volumio Node Server (c) 2021 Robert Paauwe

This is a node server to interface a [Volumio](http://www.volumio.org) Music player with
[Universal Devices ISY994] (https://www.universal-devices.com/residential/ISY) series of
controllers. It is written to run under the
[Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with
[Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)

Volumio is music server software designed to run on lightweight hardware like a Raspberry Pi.
It can play music from multiple sources including a local hard drive, a NAS, music servers,
Internet radio stations, Pandora, Spotify, etc.

This node server allows an ISY to have basic control over the music player. It queries the
Volumio device for the configured sources so that the ISY can choose which source to play.
Play, Pause, Next, Previous playback controls are supported. The ability to adjust the volume
level, turn repeat and shuffle on/off is also available.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please.
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web to a free slot.
4. From the Dashboard, select the Volumio node server and go to the configuration tab.
5. Configure the IP address of the Volumio player.

### Node Settings
The settings for this node are:

#### Short Poll
   * Not used
#### Long Poll
   * Not used

#### Volumio IP Address
   * The IP address (or name) of the Volumio player.  Note that this can't do Bonjour type name resolution so names like 'volumio.local' won't work.


## Requirements

1. Polyglot V2 running on a supported platform.
2. ISY994 series controller running firmware version 5.3 or later
3. Volumio music player

# Upgrading

If an update to the node server becomes availabe, it will show up in the Nodeserver store with an "Update" button next to 
the Volumio listing.  Click the "Update" button and the latest version of the Volumio node server will be installed.

# Release Notes

- 1.0.0 02/15/2021
   - Initial version published to github
