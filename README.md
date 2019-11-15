# xkcd-downloader
Small program (intended to be used as a command line utility) that allows the download and visualization of xkcd comics to the folder where the script is located. It can also download the explanation found at http://www.explainxkcd.com/ for the selected comic.

## Requirements:
- Python 3
- Beautiful Soup
- PIL
- requests

## Downloading comics

### Command line arguments
Now you can directly ask for specific comics via command line arguments by running the program as:

```python
python xkcd.py 2 56 78 254 789 -g -e -s
``` 
And also ranges of comics:

```python
python xkcd.py 2-56 78-254 -g -e -s
``` 
Or a combination of both:

```python
python xkcd.py 2-56 64 78-254 27 -g -e -s
``` 

Download all comics by using:
```python
python xkcd.py -a 
```
And a random comic:
```python
python xkcd.py -r
```
Depending on the value stored at xkcd\_max.txt this might be a bit slow since it first has to determine the available range of comic numbers.

where the numbers specify the comics to download, the flag ```-g``` stands for **get** (if the flag is not present no comics will be downloaded), the flag ```-e``` stands for **explain** (will print explanations directly to console separating them y dashed lines) and the flag ```-s``` stands for **show**, which will show the downloaded comics. Finally, the flag ```-r``` downloads a **random** comic and the flag ```-a``` will download **all** the available comics. You will need some patience though.

If no comic numbers or ranges are specified but the flag ```-g``` is set the latest comic will be downloaded.

### Without command line arguments
If no flags are passed the program will execute normally. It will ask for a specific comic number and download it. In the case that no input comic number is given, it will download the latest one. After that it will ask the user if another comic is to be downloaded. If the answer is no, the program will terminate its execution. 

In this case, the program will always show the explanation at http://www.explainxkcd.com/ for the selected comic.

## TODO
Check the issues page to know the future enhancements or bugs to be corrected.
