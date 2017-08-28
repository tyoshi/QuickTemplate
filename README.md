# QuickTemplate
QuickTemplate is a SublimeText plugin that allows you to quickly create and apply templates.

# Overview
This plug-in allows you to quickly create templates and data files, so that you can generate text that applies them.

## Installation

### Manual
Clone or copy this repository into the packages directory. You will need to rename the folder to `QuickTemplate` if using this method. By default, the Package directory is located at:

* OS X: ~/Library/Application Support/Sublime Text 3/Packages/
* Windows: %APPDATA%/Sublime Text 3/Packages/
* Linux: ~/.config/sublime-text-3/Packages/

## Usage

### Commands
* QuickTemplate - show command list (Ctrl+Alt+j)
* QuickTemplate apply template -  A command that applies data to a template and generates text
* QuickTemplate create new template file
* QuickTemplate create new data file
* QuickTemplate open template file
* QuickTemplate open data file

### Create template file
Templates can be written in Jinja2 format.
http://jinja.pocoo.org/docs/

### Create data file
In the data file, define the data to be used in the template.
Data can be defined in YAML format, JSON format, Python Dict instance.

## License
This software is released under the MIT License, see LICENSE.txt.
