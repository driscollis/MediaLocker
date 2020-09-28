# MediaLocker

## Background

This is the first release of a real project that I’ve been involved in. I had written an article last month that inspired Werner Bruhin to want to take it and make it into a demonstration program for new wxPython programmers in how to do MVC and CRUD while interfacing with a database. Thus, MediaLocker was born. We hope you like it.

## Description

A wxPython database application that can help you keep track of your media. Currently, it only tracks your Book library. You can read more about the project’s development in the following two articles:

* [Improving MediaLocker: wxPython, SQLAlchemy and MVC](http://www.blog.pythonlibrary.org/2011/11/30/improving-medialocker-wxpython-sqlalchemy-and-mvc/)
* [wxPython and SQLAlchemy: An Intro to MVC and CRUD](http://www.blog.pythonlibrary.org/2011/11/10/wxpython-and-sqlalchemy-an-intro-to-mvc-and-crud/)

## Requirements

* Python 2.6+
* wxPython 2.8.11+ with the new pubsub (download here) or wxPython 2.9.3
* SQLAlchemy 0.7.3+
* ObjectListView 1.2

## Configuration

After you have downloaded the source, run “python setup_lib.py develop” in the main folder before you try to run “mediaLocker.py”. If you are on wxPython 2.8, download the pubsub path (above) and extract it to “C:\Python27\Lib\site-packages\wx-2.9.2-msw\wx\lib” (or wherever your wxPython is installed).
