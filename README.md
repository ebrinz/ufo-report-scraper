# ufo-report-scraper

Scrapes nuforc website reports from [here](http://www.nuforc.org/webreports/ndxevent.html).

This is a well worn path. There are many folks who have scraped this website, and offer ready made repos.

I just thought I'd do some python practice, and leave myself a fun dataset for when I'm feeling analytical.

Currently only consuming raw data.

More data trasforming and NLP to come.


### Get raw data

clone repo, cd in, then:

```bash
pip install -r requirements.txt
```

then:
```bash
python3 scrape.py
```
and let it rip for a good while.

you may need to restart it if nuforc throttles you.

after getting all reports for each month, it will create a json file for that month with all related reports.

but, once you have the data, each subsequent execution will only get new files.

so, you can periodically update without crawling all pages again.


### Next steps

1) cleanse timestamps
2) geocode city, st
3) homogenize duration
4) grab sighting subject noun groups from description
5) sentiment analyisis
6) ...