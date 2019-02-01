# collectLeagueOfLegends

#Why did I made this program

This project has for purpose to collect automatically match info and match timeline from league of legends API. 
The quantity of request per minutes will depend of your API key.
This program respect the maximum rates of your api key, you won't get banned. (Do not try to multiprocess it
or then you'll risk to over request LOL server and then get restraint.)

You can either collect the match timeline or/and match info. You can choose until which season 
you want to collect the data and you can easily collect data from specific players. (When it has collect
the data of the players you specified it'll choose random player)

#Requirements

For this project you'll need python, an api key from league of legends 
(You can find it here : https://developer.riotgames.com) and optionally Elasticsearch.

I really recommend you to have an elastic cluster. Because when you want to analyze a lot of data you have
 to know how many data you have and where the data are located.
In this program I use elasticsearch to have an overview of my data and to know the uri of each data.
If you don't want to use elasticsearch you can turn it off in the yaml.




If you have a basic key you'll have to run it everyday because your API Key will long only one day.
I won't recommend for an application key because it'll use all your api calls.

The program will shut down if the key is outdated.

#How does it worked 


You have first to fill in the config.yaml. When it's done just run app.py.

The program will saved the json files collect from league of legends and will organized them in the folder
you indicate you want them. It will be organized by PlatformId, SeasonId, QueueId, match or timeline and by
id.

After it, it'll index a summarize json in your Elasticsearch index. You'll find in this json
game_id, each players team and champions, the game duration, the URI to the match info and 
the match timeline, the winning team, game season ...

It will give you the opportunity to find easily specifics data you want to analyze. Like I want
to know the win rates of Lucian fighting against Miss Fortune when Miss Fortune play with 
Leona. You just have to make a query in your elastic cluster and withdraw all URI games answering
the query and here you go!


#How to install the application

You just have to git clone this project.

Then install the requirement.txt with : pip -r install requirement.txt

Run your elasticsearch.

Fill the config.yaml and launch app.py



#More information/Bugs/Want to improve it

You can contact me on this email:
edwynpeignon.website@gmail.com

