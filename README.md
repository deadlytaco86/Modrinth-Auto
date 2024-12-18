# Modrinth-Auto
Download Minecraft Java mods automatically!

This program allows you to select minecraft java mods you want to download from a (for now) pre defined checklist. These mods will then be downloaded with just a push of a button. The mods will be for your chosen version and platform. The program will also tell you if it has found a download for the version and platform.

# future plans
Future versions will likely include a "try all" checkbox at the top of the predefined list to reduce the number of clicks.
Future versions will also generate a savefile in documents that will preselect the options you used during a previous download.
Further future versions will allow you to search modrinth from within the program and add additional mods to a "my mods" section"

# how to run
If you choose to run the .py file:
install the libraries at the top, then run the program how you want to. Just keep in mind the location of the base_links.json file.

If you choose to create an executable:
download all needed libraries as well as pyinstaller
You can use the provided .spec file. It is already configured so all you have to do is run the pyinstaller command: pyinstaller "Modrinth Auto.spec"
note that the json file has to be in the same folder as the script.
