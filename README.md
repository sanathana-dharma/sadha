ReadMe
===========

This is EasyConnect code on Git


How to run tests
================

```bash
pip install nose
pip install nosegae
pip install mock
cd to/project/path
nosetests
```

Its also possible to automatically run the tests while you update your files
(useful if you can attach terminal window somewehre and write the code).

```bash
pip install nosy
cd to/project/path
nosy
```


To generate a test coverage report:

```bash
pip install coverage
nosetests --with-coverage --cover-html --cover-inclusive --cover-erase --cover-html-dir=test_coverage_report
```

The report will be in test_coverage_report folder. Open index.html and see.
It will include some external modules, you can ignore them.

![image](https://cloud.githubusercontent.com/assets/193864/7063807/4fad3f40-dedc-11e4-9995-999978887656.png)
![image](https://cloud.githubusercontent.com/assets/193864/7063814/56cfe3a4-dedc-11e4-9b90-9453ff7b73ac.png)
