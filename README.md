# Timeline - Followback subject test

Capture subject information about substance use.

## Stand-alone mode

In stand-alone mode the timeline followback will not depend on external files provided by the abcd-report framework of ABCD. Instead local copies of those files will be used. No connection to REDCap will be attempted to get events and participant names. Instead local files are read in to supply this information.

An easy way to test this module locally is to run a local php web-server with:

```
php -S localhost:8000 -t .
```

and connect to http://localhost:8000 to see the page.

In stand-alone mode resulting files are stored in the data/anonymous/ directory.