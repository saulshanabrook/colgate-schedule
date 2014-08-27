# Colgate Schedule
Add your course schedule from your portal to iCal or Google Calendar automatically

## Instructions

Add an iCalendar address that will have all your courses in it to 
[Google Calendar](https://support.google.com/calendar/answer/37100?hl=en) or
[Apple Calendar](http://support.apple.com/kb/PH11523) or download the
`.ics` file by putting the calendar address in your browser, to import it to
another program.

The address you should use is
`http://colgate-schedule.herokuapp.com/<portal username>/<portal password>/`


## Possible Questions:
### How does it work?
It scrapes the schedule page, using your username and password, and looks
for the class times. Then it parses those times and creates a `.csv` file
with them.

You can see all of the code on [Github](https://github.com/saulshanabrook/colgate-schedule)

### But Isn't this horribly insecure?
Well yes, because

1. I am not ussing SSL because they make you pay for it on Heroku. So every
   time your browser goes and updates the calendar, anyone looking at the
   web traffic will be able to see your username and password. bad.
   One way to minimize this vulnerability is to actually download
   the `.ics` file once and then import it to your calendar of choice, that
   way tou are only exposing your username and password over the network
   once, instead of whenever your calendar refreshes.
2. You are sending your username and password for Colgate to someone who is not
   Colgate. That is a bad idea. I can say that I won't do anything malicious,
   like look at the logs to see everyone's usernames and password, but it is
   literally one keystroke away. One solution is to do this all on the client
   side, which I should be doing. Maybe that will be the rewrite. I just
   don't like Javascript as much as Python, but it makes much more sense.
   While I am working on that, you could deploy your own version. It runs
   for free on Heroku, just click this nice big button, and then you won't
   have to worry about me snooping into your traffic.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/saulshanabrook/colgate-schedule)

### Wait, it isn't working!!
It is pretty dumb. Also I have hard coded in the year and vacation time,
so unless I can figure out a good way to scrape that, it is stuck on 
2014-15 for now.

If it breaks for one of your classes, let me know, just [leave an issue](https://github.com/saulshanabrook/colgate-schedule/issues/new)
with as much info as you can, obviously not your username and password.
