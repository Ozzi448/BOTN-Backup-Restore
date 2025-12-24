![Static Badge](https://img.shields.io/badge/build-repo-blue?logo=github&link=https%3A%2F%2Fgithub.com%2FOzzi448%2FBOTN-Backup-Restore%2Freleases%2Ftag%2Fv1.0.2-alpha.3) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Ozzi448/BOTN-Backup-Restore/total)  

# BOTN Backup ~ Restore
  
I was inspired to create this tool to make backing up and restoring SaveGames and CharacterPresets easier. Instead of opening multiple folders and windows just to extract files from ZIP archives, this tool simplifies the entire process.  
The idea came from repeatedly seeing people in the Discord server ask, “Where is the SaveGames path?”—so I wanted to build something that reduces confusion and requires minimal user interaction.  
  
![Main Application](https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_1.png)  
  
When you first open the application:  
* Checks if `%LocalAppData%\OBF\Saved` exists; if false, the tool will create the folders.  
* Checks if CharacterPresets & SavedGames exists; if false, the tool will create the folders.  
* Checks Saved to.. location from `HKLU\\Software\\BOTNBackup`.  
* Saves window position to `HKLU\\SOFTWARE\\BOTNBackup`.  
* [Removed] (Saves window Height and Width, this posed issues with window display and would cause more confusion.)  
* [Added] 1.0.2-alpha.3 - Progress bar in Restore, this progress bar helps mostly for large archives and more than one archive in the list to extract.  
* [Added] 1.0.2-alpha.3 - ToyPresets.  
  
To fully populate these folders after a Windows Installation or Reset:  
1. Run BOTN (You can use Steam or if you are a Supporter, use the build from Patreon or SubscribeStar.)  
2. Once you get to the main menu, click Exit Game.  
  
At this stage all folders and files are restored.  
  
# Backup  
![Backup](https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_2.png)  

For Backing up, follow these steps:  
1. Click which Folder, CharacterPresets or SaveGames.  
2. Ensure that Backup is selected.  
3. Click Save to... button and choose Drive and/or Folder.  
   [Bug] (You will need to click Drive and/or Folder again inorder to re-select the path.)  
5. Click Backup, a Success prompt should appear, a file {selector}_dd-mm-yyyy.zip file should be saved to the destination chosen in step 3.  
  
# Restore  
![Restore](https://github.com/Ozzi448/BOTN-Backup-Restore/blob/c4f6f95d9fe83dfd9cd35023202d454cf4051873/Images/BOTN_Backup_~_Restore_3.png)  
  
For Restoring, follow these steps:  
1. Click which folder, CharacterPresets or SaveGames.  
2. Ensure that Restore is selected (Backup is selected by default).  
3. Drag and drop or click Add Archive button and select the file.  
   Accepted filetypes include (.zip, .rar, .7z, .sav). *You can place many files in this selector.*  
5. Click Restore button, (.zip, .rar, .7z) will be extracted, (.sav) will be copied.
  
# Installation of Character Presets
  
To install Character Presets do these steps:  
1. Click on CharacterPresets.  
2. Ensure that Restore is selected.  
3. Drag and drop or click Add Archive button and select the file.  
   Accepted filetypes include (.zip, .rar, .7z, .sav). *You can place many files in this selector.*  
4. Click Restore button, (.zip, .rar, .7z) will be extracted, (.sav) will be copied.
  
---  
  
The purpose of creating separate `.zip` backups for individual SaveGames and CharacterPresets is to keep these two elements distinct and avoid unintended overwrites. For example, if the tool targeted the entire "Saved" folder when you only wanted to restore CharacterPresets, it could accidentally replace all your existing SaveGames.  
To restore a specific SaveGame:  
* Extract the desired `SaveGames_dd-mm-yyyy.zip` file.  
* Rename the extracted `.sav` file to match an available save slot (e.g., rename it to `4.sav` if you already have `0.sav`, `1.sav`, `2.sav`, `3.sav`, and `GameActions.sav`).  
  
For additional questions or information regarding the game, please ask in the [Breeders of the Nephelym](https://discord.gg/MHkf62B5EJ) Discord server or consult the [Breeders of the Nephelym Wiki](https://breedersofthenephelym.miraheze.org/wiki/Breeders_of_the_Nephelym_Wiki).  
If you have specific questions or issues with this tool, please use the [Issues](https://github.com/Ozzi448/BOTN-Backup-Restore/issues) tab.  
