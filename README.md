## Icy Voice Assintant

**Your own local assistant, working entirely on your computer!**

### TODO
- add proxy interface for voice and command handlers
- change the intention classifier to dependency injection, as command proxy
- add recomendation for the web config page
- add downloading the vosk models (and choosing from the web repo)
- create the server for IcyMI (modules index)
- unify localization services among modules (need separated i18n system)
- move stop recording exception to the voice handler
- rearrange the appstate structure to make it less God object
- rearrange the stucture of folders and files to make more understandable
- add checks for incorrect prev.data file (to not fail program only because of that)
- add correct index web page for assistant
- handle the obsidian vault
- save web page theme
- add headless (no web / no window) mode