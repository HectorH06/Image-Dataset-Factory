![Made with Python](https://forthebadge.com/images/badges/made-with-python.svg)

```ascii
██╗███╗   ███╗ ██████╗     ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
██║████╗ ████║██╔════╝     ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║██╔████╔██║██║  ███╗    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
██║██║╚██╔╝██║██║   ██║    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
██║██║ ╚═╝ ██║╚██████╔╝    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
╚═╝╚═╝     ╚═╝ ╚═════╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝

       by HectorH06 (@HectorH06)          version 2.4
```

### General Description

```diff
- ONLY WORKS WITH GOOGLE CHROME INSTALLED ON WINDOWS OS, other OS might not be supported even if the webdriver version is changed
```

This project creates image datasets using google images as source. Separates them in training and test groups and generates the respective dictionaries for supervised learning.

For the scraper functions: meaningful changes to this project but kept the basics: https://github.com/ohyicong/Google-Image-Scraper. Fixed as much as possible from it.
This project bypasses new restrictions for webscraping.

If you are looking for other image scrapers, JJLimmm has created image scrapers for Gettyimages, Shutterstock, and Bing. <br>
Visit their repo here: https://github.com/JJLimmm/Website-Image-Scraper

## Features

- Scrapes n images from google about custom topics
- Separates each topic in a training set and a test set
- Creates data dictionaries with all the images (train and test)
- 50 images about a topic with all its files takes about 15 minutes to download
- Implemented AlexNet to classify the images (experiment)