![Static Badge](https://img.shields.io/badge/build-repo-blue?logo=github&link=https%3A%2F%2Fgithub.com%2FOzzi448%2FBOTN-Backup-Restore%2Freleases%2Ftag%2Fv1.0.2-alpha.3) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Ozzi448/BOTN-Backup-Restore/total)  

# BOTN Backup ~ Restore  

# About  

I created this tool to make backing up and restoring SaveGames, ToyPresets, and CharacterPresets far more straightforward. Instead of navigating multiple folders and windows just to extract files from ZIP archives, this tool streamlines the entire process.  
The idea came from seeing the same question pop up repeatedly in the Discord server—“Where is the SaveGames path?” I wanted to build something that reduces confusion and requires as little user effort as possible.  
This is a not‑for‑profit project and follows the same usage conditions as the base game, excluding its early development builds. However, if you support DerelictHelmsman on 
 [Patreon](<https://www.patreon.com/c/BreedersOfTheNephelym>) or [SubscribeStar](<https://subscribestar.adult/derelict-enertainment>), you’re welcome to use this tool with those early builds as well.  
  
# Disclaimer  
I am not involved in the development of the main game and would never claim otherwise. This tool is entirely separate from the primary project. I simply have DerelictHelmsman’s approval to create it and share it with anyone who finds it useful
 
---
<p align="center"><img src="https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_1.png" alt=Main Application"></p>
  
When you first open the application:  
* Checks if `%LocalAppData%\OBF\Saved` exists; if false, the tool will create the folders.  
* Checks if CharacterPresets & ToyPresets & SavedGames exists; if false, the tool will create the folders.  
* Saves the __Saved to...__ chosen path to `HKLU\\Software\\BOTNBackup` and checks the chosen path from `HKLU\\Software\\BOTNBackup` on application startup.  
* Saves window position to `HKLU\\SOFTWARE\\BOTNBackup`.  
* ~~Saves window Height and Width, this posed issues with window display and would cause more confusion.~~  
  
Other Features  
* [Added] 1.0.2-alpha.3 - Added a progress bar in Restore, this progress bar helps mostly large archives or more than one archive in the list to extract.  
  * This should help avoid confusion for when the application is appearing as though it's doing nothing, while everything is greyed out and non responsive.  
  * I could add a 'Show Log' button, but this would mean full rewrite of the restore functions.  
* [Added] 1.0.2-alpha.3 - Added ToyPresets choice.  
* Only targets and extracts `.sav` files from archives.
---
To fully populate these folders after a Windows Installation or Reset:  
1. Run BOTN (You can use Steam or if you are a Supporter, use the build from Patreon or SubscribeStar.)  
2. Once you get to the main menu, click Exit Game.  
  
At this stage all folders and files are restored.  
  
# Backup  
<p align="center"><img src="https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_2.png" alt="Backup"></p>

For Backing up, follow these steps:  
1. Click which Folder, __CharacterPresets__, __ToyPresets__, or __SaveGames__.  
2. Ensure that __Backup__ is selected.  
3. Click __Save to...__ button and choose drive and/or folder.   
5. Click __Backup__, a _Success prompt should appear_, _a file {selector}\_dd-mm-yyyy.zip file should be saved to the destination chosen in step 3_.  
  
# Restore  
<p align="center"><img src="https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_3.png" alt="Restore"></p>
  
For Restoring, follow these steps:  
1. Click which folder, __CharacterPresets__, __ToyPresets__, or __SaveGames__.  
2. Ensure that __Restore__ is selected _(Backup is selected by default)_.  
3. __Drag and drop__ or click __Add Archive__ button and select the file.  
   Accepted filetypes include _(.zip, .rar, .7z, .sav). You can place many files in this selector_.  
5. Click __Restore__ button, _(.zip, .rar, .7z) will be extracted, (.sav) will be copied_.
  
# Installation of Character Presets  
  
To install Character Presets do these steps:  
1. Click on __CharacterPresets__.  
2. Ensure that __Restore__ is selected.  
3. __Drag and drop__ or click __Add Archive__ button and select the file.  
   Accepted filetypes include _(.zip, .rar, .7z, .sav). You can place many files in this selector_.  
4. Click __Restore__ button, _(.zip, .rar, .7z) will be extracted, (.sav) will be copied_.  
  
# Installation of Toy Presets  

To install ToyPresets do these steps:  
1. Click on __ToyPresets__.  
2. Ensure that __Restore__ is selected.  
3. __Drag and drop__ or click __Add Archive__ button and select the file. _ToyPresets\_dd-mm-yyyy.zip or the package from toy_pattern-presets channel in the discord e.g. DefaultToyPresetsUpdated.zip_.  
   Accepted filetypes include _(.zip, .rar, .7z, .sav)_.
4. Click __Restore__ button, _(.zip, .rar, .7z) will be extracted, (.sav) will be copied_.
---
The purpose of creating a separate `.zip` backup for individual __SaveGames__, __ToyPresets__, and __CharacterPresets__ is to keep these two elements distinct and avoid unintended overwrites. For example, if the tool targeted the entire __"Saved"__ folder when you only wanted to restore __CharacterPresets__, it could accidentally replace all your existing __SaveGames__, and __ToyPresets__. 
  
# To restore a specific SaveGame:  
* Extract the desired `SaveGames_dd-mm-yyyy.zip` file.  
* Rename the extracted `.sav` file to match an available save slot (e.g., rename it to `4.sav` if you already have `0.sav`, `1.sav`, `2.sav`, `3.sav`, and `GameActions.sav`).
---
For additional questions or information regarding the game, please ask in the [Breeders of the Nephelym](https://discord.gg/MHkf62B5EJ) Discord server or [Breeders of the Nephelym](https://steamcommunity.com/app/1161770/discussions/) Steam Forum Discussion or consult the [Breeders of the Nephelym Wiki](https://breedersofthenephelym.miraheze.org/wiki/Breeders_of_the_Nephelym_Wiki).  
If you have specific questions or issues with this tool, please use the [Issues](https://github.com/Ozzi448/BOTN-Backup-Restore/issues) tab.  
