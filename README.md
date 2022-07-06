# zxcs
A comprehensive download conversion management script set for http://www.zxcs.me/

## Prerequisite
1. Python3 environment with `beautifulsoup4` `patoolib` `requests` installed
2. `pandoc` `unrar` installed in system path. if you are using Kobo Ereader, `kepubify` is needed.

## Useage

  ```Python3 run.py```
  
  then enter the book id which in the url, it will download the cover image and the text file automatically. an `epub` file and a `kepub` file will be generated after the conversion.
  
## Miscellaneous 
  You can edit `epub.css` for your own style of the epub book
  `bug.py` `praise.py` `batch.py` are the crawler to collect the book info on the site, and batch download. not completed.
  `single.py` is used to convert some txt download out of zxcs. not completed.
  

