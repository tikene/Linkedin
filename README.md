### Linkedin auto apply for jobs bot

This script automatically applies for any available Linkedin jobs.

Some require extra questions in order to apply, such as why do you wanna join their company. These will be skipped since creating an answer for every question would be impossible/a big headache (unless gpt-3?).

Tested on English and Spanish Linkedin, Windows 10.

It's currently under development, if you encounter any issues please let me know using the Issues tab.



**Features**:
- Filter by job name, location and experience
- Settings are automatically saved to a config file
- SMS & Bot verification supported


**Requirements**:
- pip3 install -r requirements.txt
- Chrome
- A curriculum must be added to your Linkedin already


**TODO**: 
- Click on next jobs page
- Select custom curriculum
- Add support for more job filters, such as remote work 
- Invisible browser



**Instructions**:

The first time you run the program a setup is required. You must enter the account credentials and specify the job search filters. Once Linkedin loads, it will automatically type the locations you've introduced in the search bar and then wait for a location to be clicked by the user, once you've been redirected you can press enter and the program will save it automatically.



**Images**:

![console_output](https://user-images.githubusercontent.com/92279236/145089269-d6c6f1d3-94fc-47fc-b240-f5875158812a.jpg)

![console_output2](https://user-images.githubusercontent.com/92279236/145090059-70d70403-1bdc-4586-93d2-752cde30475a.png)
