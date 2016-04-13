# Getting started

Een bot schrijven is op zich triviaal. Het is niet meer dan een programma
schrijven (in eender welke programmeertaal) die informatie inleest via standaard invoer, en die commando's
stuurt schrijft naar standaard uitvoer. We zullen je bot oproepen met één argument: de naam die we toekennen
aan je bot. Op die manier weet je welke forten van jou zijn.

Mocht dit niet duidelijk zijn, kan je altijd eens kijken naar de voorbeeld-bots
op [de GitHub repo](https://github.com/ZeusWPI/aichallenge/tree/master/battlebots/testbots).

## Op je eigen computer testen

Stel dat je nu een dergelijk programma hebt geschreven, bijvoorbeeld genaamd
`bot.py`, dan willen we deze natuurlijk testen door deze te laten vechten tegen
andere bots of tegen zichzelf. Hiervoor schrijven we eerste een klein
configuratie-bestandje in JSON, bijvoorbeeld `example.json`:

    {
        "players": {
            "bot1": "python bot.py",
            "bot2": "python bot.py"
        },
        "mapfile": "example.input",
        "logfile": "example.log",
        "max_steps": 500
    }

Wanneer we dit configuratiebestandje meegeven aan de arbiter, zullen twee
versies van `bot.py` tegen elkaar vechten op het speelveld van `example.input`.
Deze zal een verslag van het gevecht uitschrijven in `example.log`.
De arbiter is een Python 3.5 programma dat in [de GitHub repo](https://github.com/ZeusWPI/aichallenge) staat, dus clone eerst deze repo
en roep dit programma als volgt met je zonet geschreven configuratiebestand als
argument:

    python3 arbiter.py example.json

Let op de paden in het config bestand!

Vervolgens kunnen we dit verslag gebruiken om het verloop van het gevecht te
visualisueren. Open het HTML-bestand `visualize/visualize.html` van deze repo in
je browser en selecteer `example.data` in de arbiter directory.

## Laten vechten tegen andere bots

Als je een ietwat werkende bot hebt, kan je deze laten vechten tegen bots van
andere deelnemers. [Maak een account aan]({{ url_for('register') }}) op deze
site, laad je bot op en er zullen automatisch gevechten met je bot worden
uitgevoerd. Hoe meer matches gespeeld, hoe meer je rangschikking ten opzichte
van de andere bots convergeert.

Zo, nu je weet hoe je bot kan testen, ben je klaar om wicked bots te beginnen
schrijven!