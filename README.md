# adslib
Download private library from NASA ADS

adslib is a command line utility, written in Python, that uses the [NASA ADS API](https://github.com/adsabs/adsabs-dev-api) to download a private library from the [NASA Astrophysics Data System](https://ui.adsabs.harvard.edu/).

In order to use it, you must [set up an API key](http://adsabs.github.io/help/api/).

# Examples:

```
python3 adslib.py -h
```
prints the keyword definitions:
```
usage: adslib.py [-h] [--bibtex BIBTEX] [--html HTML] library

Download library from NASA ADS.

positional arguments:
  library          NASA ADS Library ID

optional arguments:
  -h, --help       show this help message and exit
  --bibtex BIBTEX  File for BibTeX output
  --html HTML      File for HTML output
```

QdlkTDaJTkuhuKTF-tRx3Q is the Private Library identifier for the papers related to the [Parker Solar Probe/FIELDS instrument suite](http://fields.ssl.berkeley.edu/).  HTML and/or BibTeX files for this library can be downloaded with the command:

```
python3 adslib.py QdlkTDaJTkuhuKTF-tRx3Q --bibtex fields_papers.bib --html fields_papers.html
```
The output will be similar to the output below:
```
Loading bibcodes from input library: QdlkTDaJTkuhuKTF-tRx3Q
Number of bibcodes retreieved: 3
Remaining Requests: 977
Allowed Requests: 1000

Output HTML file: fields_papers.html
Number of bibcodes in library: 3
Remaining Big Requests: 81
Allowed Big Requests: 100

Output BibTeX file: fields_papers.bib
Retrieved 3 abstracts, starting with number 1.  Total number selected: 3.
Remaining Export Requests: 183
Allowed Export Requests: 200
```
